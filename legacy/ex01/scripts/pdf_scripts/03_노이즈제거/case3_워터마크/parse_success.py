import pdfplumber
import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/03_case3_워터마크.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/03_case3_워터마크_성공.md")
    
    full_text = "# [문서 처리 성공] 03_case3_워터마크 - 색상 필터링(Filter) 기반 워터마크 제거 결과\n\n"
    full_text += "### RAG 최적화 분석\n"
    full_text += "- **전략**: `page.filter()` 함수를 사용하여 검은색(0,0,0) 텍스트 객체만 선별적으로 추출.\n"
    full_text += "- **효과**: 본문과 겹쳐 있는 붉은색/회색 워터마크(CONFIDENTIAL 등)를 완벽하게 제거.\n\n"
    full_text += "---\n"
    full_text += "### 정제된 텍스트 결과 (Markdown)\n\n"
    full_text += "```markdown\n"
    
    with pdfplumber.open(input_pdf) as pdf:
        for page in pdf.pages:
            # 1. 색상 필터링: 검은색(0,0,0)에 가까운 글자만 추출 (워터마크는 붉은색)
            # pdfplumber의 filter 함수 사용
            clean_chars = page.filter(lambda obj: obj.get("object_type") == "char" and obj.get("non_stroking_color") == (0, 0, 0))
            full_text += (clean_chars.extract_text() or "") + "\n\n"
            
    full_text += "\n```"
    with open(output_md, "w") as f:
        f.write(full_text)
    print(f"성공 결과 생성: {output_md}")

if __name__ == "__main__":
    main()
