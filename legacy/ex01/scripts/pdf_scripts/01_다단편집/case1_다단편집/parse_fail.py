import fitz
import os

def main():
    # 현재 파일 위치: 실습용/ex01/scripts/pdf_scripts/01_column/case1_shredding/failure/parse_실패ure.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/01_case1_다단편집.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/01_case1_다단편집_실패.md")
    
    print(f"🚀 [Failure 01] 기본 파서 시도: {input_pdf}")
    if not os.path.exists(input_pdf):
        print(f"❌ 에러: 파일을 찾을 수 없습니다. {input_pdf}")
        return

    doc = fitz.open(input_pdf)
    text = ""
    for page in doc:
        text += page.get_text()
    
    os.makedirs(os.path.dirname(output_md), exist_ok=True)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# [문서 처리 실패] 01_case1_다단편집 - 기본 파서 결과\\n\\n")
        f.write("### 상황 분석\\n")
        f.write("- **증상**: 단어들이 음절 단위로 찢어지거나(`대 한 민 국`), 좌우 단이 무질서하게 뒤섞임.\n")
        f.write("- **원인**: 단순 텍스트 추출기는 좌표 기반의 '문단' 개념이 없어, 가로 줄에 걸리는 모든 글자를 순서대로 나열함.\n\n")
        f.write("--- \n")
        f.write(f"### 추출된 텍스트 결과\\n")
        f.write(f"```text\n{text}\n```\n\n")

    print(f"실패 결과 생성: {output_md}")

if __name__ == "__main__":
    main()
