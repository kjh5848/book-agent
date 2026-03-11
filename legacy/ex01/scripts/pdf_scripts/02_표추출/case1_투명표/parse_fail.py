import fitz
import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/02_case1_투명표.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/02_case1_투명표_실패.md")
    
    print(f"🚀 [Failure 02] 전처리 시작: {input_pdf}")
    doc = fitz.open(input_pdf)
    text = ""
    for page in doc:
        text += page.get_text()
    
    os.makedirs(os.path.dirname(output_md), exist_ok=True)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# [문서 처리 실패] 02_case1_투명표 - 격자 구조 유실\n\n")
        f.write("### 상황 분석\n")
        f.write("- **증상**: 표의 데이터들이 행/열 구분 없이 일반 텍스트 문단처럼 뭉쳐서 나옴.\n")
        f.write("- **원인**: 문서 내에 표를 구분하는 선(Line) 객체가 없어, 파서가 이를 표로 인식하지 못하고 일반 텍스트로 처리함.\n\n")
        f.write("--- \n")
        f.write(f"### 추출된 텍스트 결과\n")
        f.write(f"```text\n{text}\n```\n\n")
    print(f"실패 결과 생성: {output_md}")

if __name__ == "__main__":
    main()
