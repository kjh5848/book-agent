import fitz
import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/03_case2_사이드바.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/03_case2_사이드바_실패.md")
    
    doc = fitz.open(input_pdf)
    text = ""
    for page in doc:
        text += page.get_text()
    
    os.makedirs(os.path.dirname(output_md), exist_ok=True)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# [문서 처리 실패] 03_case2_사이드바 - 본문 및 부가 정보 뒤섞임\n\n")
        f.write("### 상황 분석\n")
        f.write("- **증상**: 본문을 읽는 도중 사이드바의 '관련 기사'나 '추천 링크' 텍스트가 문맥 중간에 삽입됨.\n")
        f.write("- **원인**: 2단 레이아웃임에도 불구하고 가로축(y좌표) 기준으로만 텍스트를 나열하여 본문과 사이드바의 경계를 구분하지 못함.\n\n")
        f.write("--- \n")
        f.write(f"### 추출된 텍스트 결과\n")
        f.write(f"```text\n{text}\n```\n\n")
    print(f"실패 결과 생성: {output_md}")

if __name__ == "__main__":
    main()
