import fitz
import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/01_case3_내포된표.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/01_case3_내포된표_실패.md")
    
    doc = fitz.open(input_pdf)
    text = ""
    for page in doc:
        text += page.get_text()
    
    os.makedirs(os.path.dirname(output_md), exist_ok=True)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# [문서 처리 실패] 01_case3_내포된표 - 박스 내부 텍스트 유실\\n\\n")
        f.write("### 상황 분석\\n")
        f.write("- **증상**: 다단 사이에 삽입된 정보 박스 내부의 텍스트가 본문 흐름 중간에 갑자기 튀어나와 문맥을 단절시킴.\n")
        f.write("- **원인**: 레이아웃 분석 없이 텍스트 좌표 순서로만 읽었기 때문에 시각적인 박스 구조를 무시함.\n\n")
        f.write("--- \n")
        f.write(f"### 추출된 텍스트 결과\\n")
        f.write(f"```text\n{text}\n```\n\n")
    print(f"실패 결과 생성: {output_md}")

if __name__ == "__main__":
    main()
