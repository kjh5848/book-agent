import pdfplumber
import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/01_case3_내포된표.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/01_case3_내포된표_성공.md")
    
    if not os.path.exists(input_pdf):
        print(f"❌ Input PDF not found: {input_pdf}")
        return

    full_text = "# [문서 처리 성공] 01_case3_내포된표 - 중첩 다단 구조 복원 (Recursive Split)\\n\\n"
    full_text += "### RAG 최적화 분석\\n"
    full_text += "- **전략**: `pdfplumber.rects`로 내부 박스를 감지하여 별도 영역(Zone)으로 추출.\n"
    full_text += "- **효과**: 표/박스 내부 데이터가 본문 텍스트와 섞이지 않고 독립적으로 보존됨.\n\n"
    full_text += "---\n"
    full_text += "### 정제된 텍스트 결과 (Markdown)\\n\\n"
    full_text += "```markdown\n"
    
    with pdfplumber.open(input_pdf) as pdf:
        for page in pdf.pages:
            width = page.width
            height = page.height
            mid = width / 2
            
            # 1. 메인 컬럼 분할 (왼쪽 / 오른쪽)
            left_main_bbox = (0, 0, mid, height)
            right_main_bbox = (mid, 0, width, height)
            
            # 페이지를 잘라서(crop) 왼쪽/오른쪽 메인 컬럼을 확보합니다.
            # 하지만 내부 박스(Inner Box) 텍스트 추출을 위해서는 정밀한 좌표를 사용하여 다시 crop해야 합니다.
            left_main = page.crop(left_main_bbox)
            right_main = page.crop(right_main_bbox)
            
            full_text += "## [왼쪽 메인 컬럼]\n"
            
            # 2. Rect(사각형)를 사용하여 "내부 박스" 감지
            # 왼쪽 컬럼 내부에 있고, 크기가 적당한 사각형을 필터링합니다.
            candidates = [
                r for r in page.rects
                if (r["x0"] + r["width"]/2) < mid  # 중심점이 왼쪽 컬럼에 위치
                and r["width"] > 100
                and r["height"] > 50
            ]
            
            if candidates:
                # 가장 큰 사각형 선택 (배경 또는 테두리로 추정)
                inner_rect = max(candidates, key=lambda r: r["width"] * r["height"])
                
                inner_top = inner_rect["top"]
                inner_bottom = inner_rect["bottom"]
                inner_left = inner_rect["x0"]
                inner_right = inner_rect["x1"]
                
                # Zone A: 내부 박스 위쪽 텍스트
                # 높이가 음수가 되지 않도록 주의하며 잘라냅니다.
                if inner_top > 50:
                    try:
                        top_area = page.crop((0, 0, mid, inner_top))
                        top_text = top_area.extract_text()
                        if top_text: full_text += top_text + "\n\n"
                    except Exception: pass
                
                # Zone B: 내부 박스 (중첩 레이아웃)
                full_text += "### [Inner Box Analysis]\n"
                
                inner_width = inner_right - inner_left
                inner_mid = inner_left + (inner_width / 2)
                
                # 개선: 박스 내부의 전체 너비 헤더(Header) 확인
                # 상단 25pt 정도를 헤더로 가정합니다.
                header_height = 25 
                
                try:
                    # 1. 내부 헤더 (전체 너비)
                    inner_header_area = page.crop((inner_left, inner_top, inner_right, inner_top + header_height))
                    header_text = inner_header_area.extract_text()
                    if header_text:
                        full_text += f"**{header_text}**\n\n"
                    
                    # 2. 내부 본문 (분할 컬럼)
                    body_top = inner_top + header_height
                    
                    if body_top < inner_bottom:
                        # 내부 왼쪽
                        col1 = page.crop((inner_left, body_top, inner_mid, inner_bottom))
                        text1 = col1.extract_text()
                        
                        # 내부 오른쪽
                        col2 = page.crop((inner_mid, body_top, inner_right, inner_bottom))
                        text2 = col2.extract_text()
                        
                        full_text += f"> **[Inner Left]**\n{text1}\n\n"
                        full_text += f"> **[Inner Right]**\n{text2}\n\n"
                except Exception as e:
                    full_text += f"(내부 박스 분할 실패: {e})\n"
                
                # Zone C: 내부 박스 아래쪽 텍스트
                if inner_bottom < height - 50:
                    try:
                        bottom_area = page.crop((0, inner_bottom, mid, height))
                        bottom_text = bottom_area.extract_text()
                        if bottom_text: full_text += bottom_text + "\n\n"
                    except Exception: pass
                    
            else:
                # 내부 박스가 감지되지 않으면, 평소처럼 추출
                full_text += left_main.extract_text() + "\n\n"
                
            full_text += "## [오른쪽 메인 컬럼]\n"
            full_text += right_main.extract_text() + "\n\n"
    
    full_text += "\n```"

    with open(output_md, "w") as f:
        f.write(full_text)
    print(f"성공 결과 생성: {output_md}")

if __name__ == "__main__":
    main()
