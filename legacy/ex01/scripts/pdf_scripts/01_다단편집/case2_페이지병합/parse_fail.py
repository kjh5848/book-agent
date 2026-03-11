import fitz
import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/01_case2_페이지병합.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/01_case2_페이지병합_실패.md")
    
    if not os.path.exists(input_pdf):
        print(f"❌ 에러: 파일을 찾을 수 없습니다. {input_pdf}")
        return

    doc = fitz.open(input_pdf)
    text = ""
    for page in doc:
        text += page.get_text()
    
    os.makedirs(os.path.dirname(output_md), exist_ok=True)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# [문서 처리 실패] 01_case2_페이지병합 - 문맥 뒤섞임\n\n")
        f.write("### 상황 분석\n")
        f.write("- **증상**: 왼쪽 단의 문장 끝과 오른쪽 단의 문장 시작이 한 줄로 합쳐짐. (예: `왼쪽문장 오오른쪽문장`)\n")
        f.write("- **원인**: PDF 파서가 수평으로 인접한 두 텍스트 블록을 하나의 행으로 인식하여 물리적 순서대로 이어 붙였기 때문임.\n\n")
        f.write("--- \n")
        f.write(f"### 추출된 텍스트 결과\n")
        f.write(f"```text\n{text}\n```\n\n")
    print(f"실패 결과 생성: {output_md}")

if __name__ == "__main__":
    main()
