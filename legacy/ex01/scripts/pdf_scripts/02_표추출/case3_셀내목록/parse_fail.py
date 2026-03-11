import fitz
import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/02_case3_셀내목록.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/02_case3_셀내목록_실패.md")
    
    doc = fitz.open(input_pdf)
    text = ""
    for page in doc:
        text += page.get_text()
    
    os.makedirs(os.path.dirname(output_md), exist_ok=True)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# [문서 처리 실패] 02_case3_셀내목록 - 줄바꿈 파괴\\n\\n")
        f.write("### 상황 분석\\n")
        f.write("- **증상**: 셀 내부의 줄바꿈이 행 바꿈으로 오인되어 표의 행과 열이 무너짐.\n")
        f.write("- **원인**: 마크다운 표 형식은 한 줄(Line)이 하나의 행(Row)을 의미하는데, 데이터 내부의 줄바꿈을 처리하지 않고 그대로 출력했기 때문임.\n\n")
        f.write("--- \n")
        f.write(f"### 추출된 텍스트 결과\\n")
        f.write(f"```text\n{text}\n```\n\n")
    print(f"실패 결과 생성: {output_md}")

if __name__ == "__main__":
    main()
