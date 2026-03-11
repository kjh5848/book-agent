import fitz
import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/03_case3_워터마크.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/03_case3_워터마크_실패.md")
    
    doc = fitz.open(input_pdf)
    text = ""
    for page in doc:
        text += page.get_text()
    
    os.makedirs(os.path.dirname(output_md), exist_ok=True)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# [문서 처리 실패] 03_case3_워터마크 - 불필요한 보안 문구 삽입\n\n")
        f.write("### 상황 분석\n")
        f.write("- **증상**: 'CONFIDENTIAL', '배포금지' 등의 워터마크가 본문 문장 중간마다 불쑥 튀어나옴.\n")
        f.write("- **원인**: 시각적으로는 본문 뒤에 배경처럼 깔려 있어도, 파서 입장에서는 이 또한 추출해야 할 하나의 '텍스트 객체'로 보이기 때문임.\n\n")
        f.write("--- \n")
        f.write(f"### 추출된 텍스트 결과\n")
        f.write(f"```text\n{text}\n```\n\n")
    print(f"실패 결과 생성: {output_md}")

if __name__ == "__main__":
    main()
