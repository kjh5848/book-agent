import fitz
import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/05_case2_플로우차트.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/05_case2_플로우차트_실패.md")
    
    doc = fitz.open(input_pdf)
    text = ""
    for page in doc:
        text += page.get_text()
    
    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# [Failure] 05_case2_플로우차트 - 프로세스 흐름 단절(Broken Link)\n\n")
        f.write("### 🚨 상황 분석\n")
        f.write("- **증상**: 'Training -> Evaluation -> Deploy'와 같은 순서 정보가 사라지고, 단어들이 무작위로 나열됨.\n")
        f.write("- **원인**: OCR은 좌상단에서 우하단으로 텍스트를 읽기 때문에, 화살표(Arrow)가 지시하는 논리적 순서를 전혀 인지하지 못함.\n\n")
        f.write("--- \n")
        f.write(f"### 📄 추출된 텍스트 결과\n")
        extracted_text = text if text.strip() else "(내용 없음)"
        f.write(f"```text\n{extracted_text[:300]}...\n```\n\n")
    print(f"✅ 실패 결과 생성: {output_md}")

if __name__ == "__main__":
    main()
