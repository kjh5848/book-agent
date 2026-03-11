import fitz
import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/05_case3_복합범례.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/05_case3_복합범례_실패.md")
    
    doc = fitz.open(input_pdf)
    text = ""
    for page in doc:
        text += page.get_text()
    
    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# [Failure] 05_case3_복합범례 - 데이터 매핑 실패(Context Mismatch)\n\n")
        f.write("### 🚨 상황 분석\n")
        f.write("- **증상**: 기업명(Nvidia, Apple)과 수치(30%, 25%)가 따로 놀아, 어떤 수치가 어떤 기업의 것인지 알 수 없음.\n")
        f.write("- **원인**: 문서는 '색상(Color)'을 통해 정보를 전달하지만, 텍스트 추출 엔진은 색상 정보를 무시하고 글자만 가져오기 때문.\n\n")
        f.write("--- \n")
        f.write(f"### 📄 추출된 텍스트 결과\n")
        extracted_text = text if text.strip() else "(내용 없음)"
        f.write(f"```text\n{extracted_text[:300]}...\n```\n\n")
    print(f"✅ 실패 결과 생성: {output_md}")

if __name__ == "__main__":
    main()
