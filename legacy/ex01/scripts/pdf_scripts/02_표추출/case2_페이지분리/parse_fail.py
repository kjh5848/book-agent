import fitz
import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/02_case2_페이지분리.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/02_case2_페이지분리_실패.md")
    
    doc = fitz.open(input_pdf)
    text = ""
    for page in doc:
        text += f"--- Page {page.number + 1} ---\n"
        text += page.get_text() + "\n"
    
    os.makedirs(os.path.dirname(output_md), exist_ok=True)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# [문서 처리 실패] 02_case2_페이지분리 - 헤더 누락\n\n")
        f.write("### 상황 분석\n")
        f.write("- **증상**: 2페이지 이후의 표 데이터가 무엇을 의미하는지 알 수 없는 값들의 나열로 변함.\n")
        f.write("- **원인**: 표가 페이지를 넘어가면서 헤더(Column Name)가 유실되었고, 파서는 이를 1페이지와 연결된 데이터로 보지 못함.\n\n")
        f.write("--- \n")
        f.write(f"### 추출된 텍스트 결과\n")
        f.write(f"```text\n{text}\n```\n\n")
    print(f"실패 결과 생성: {output_md}")

if __name__ == "__main__":
    main()
