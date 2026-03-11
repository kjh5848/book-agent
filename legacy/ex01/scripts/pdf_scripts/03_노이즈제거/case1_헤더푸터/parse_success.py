import pdfplumber
import os

def parse_성공_03():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/03_case1_헤더푸터.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/03_case1_헤더푸터_성공.md")
    
    with pdfplumber.open(input_pdf) as pdf:
        full_text = ""
        for page in pdf.pages:
            # 헤더/푸터 영역을 제외하고 중앙 본문 영역만 Crop (좌표 기준)
            # top: 100, bottom: 750 정도로 제한하여 노이즈 제거
            bbox = (0, 100, page.width, 750) 
            cropped = page.crop(bbox)
            full_text += cropped.extract_text() + "\n\n"
            
    os.makedirs(os.path.dirname(output_md), exist_ok=True)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# [문서 처리 성공] 03_case1_헤더푸터 - 영역 자르기(Crop) 기반 노이즈 제거 결과\n\n")
        f.write("### RAG 최적화 분석\n")
        f.write("- **전략**: `page.crop(bbox)`를 사용하여 상단(0~100)과 하단(750~)의 노이즈 영역을 좌표 기반으로 제거.\n")
        f.write("- **효과**: 반복되는 무의미한 텍스트(헤더/푸터)가 제거되어 검색 품질 향상.\n\n")
        f.write("---\n")
        f.write("### 정제된 텍스트 결과 (Markdown)\n\n")
        f.write(full_text)
    print(f"성공 결과 생성 완료: {output_md}")

if __name__ == "__main__":
    parse_성공_03()
