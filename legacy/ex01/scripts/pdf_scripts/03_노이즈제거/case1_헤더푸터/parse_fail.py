import fitz
import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/03_case1_헤더푸터.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/03_case1_헤더푸터_실패.md")
    
    print(f"[Failure 03] 전처리 시작: {input_pdf}")
    doc = fitz.open(input_pdf)
    text = ""
    for page in doc:
        text += page.get_text()
    
    os.makedirs(os.path.dirname(output_md), exist_ok=True)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# [문서 처리 실패] 03_case1_헤더푸터 - 반복적 노이즈(Noise) 유입\n\n")
        f.write("### 상황 분석\n")
        f.write("- **증상**: 추출된 텍스트 본문 사이사이에 '문서 보안', 'Page X'와 같은 부가 정보가 무질서하게 섞여 있음.\n")
        f.write("- **원인**: 본문과 메타데이터 영역을 구분하지 않고 페이지 전체 텍스트를 한꺼번에 긁어왔기 때문임.\n\n")
        f.write("--- \n")
        f.write(f"### 추출된 텍스트 결과\n")
        f.write(f"```text\n{text}\n```\n\n")
    print(f"실패 결과 생성: {output_md}")

if __name__ == "__main__":
    main()
