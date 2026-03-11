import pdfplumber
import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/03_case2_사이드바.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/03_case2_사이드바_성공.md")
    
    full_text = "# [문서 처리 성공] 03_case2_사이드바 - 수직 분할(Vertical Crop) 기반 본문/사이드바 분리 결과\n\n"
    full_text += "### RAG 최적화 분석\n"
    full_text += "- **전략**: 페이지 너비의 70% 지점을 기준으로 본문과 사이드바(광고/링크)를 물리적으로 분리.\n"
    full_text += "- **효과**: 문맥(Context)이 섞이는 것을 방지하고, 본문과 부가 정보를 명확히 구분하여 저장.\n\n"
    full_text += "---\n"
    full_text += "### 정제된 텍스트 결과 (Markdown)\n\n"
    full_text += "```markdown\n"
    
    with pdfplumber.open(input_pdf) as pdf:
        for page in pdf.pages:
            width = page.width
            # 70% 지점을 경계로 설정 (HTML CSS 기준)
            sidebar_boundary = width * 0.7
            
            # 본문 영역 (왼쪽 70%)
            main_body = page.crop((0, 0, sidebar_boundary, page.height))
            # 사이드바 영역 (오른쪽 30%)
            sidebar = page.crop((sidebar_boundary, 0, width, page.height))
            
            full_text += "#### [본문 영역]\n" + (main_body.extract_text() or "") + "\n\n"
            full_text += "#### [사이드바/주석 영역]\n" + (sidebar.extract_text() or "") + "\n\n"
            
    full_text += "\n```"
    with open(output_md, "w") as f:
        f.write(full_text)
    print(f"성공 결과 생성: {output_md}")

if __name__ == "__main__":
    main()
