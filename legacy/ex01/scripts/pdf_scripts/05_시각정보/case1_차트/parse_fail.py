import fitz
import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/05_case1_차트.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/05_case1_차트_실패.md")
    
    print(f"🚀 [Failure 05] 전처리 시작: {input_pdf}")
    doc = fitz.open(input_pdf)
    text = ""
    for page in doc:
        text += page.get_text()
    
    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# [Failure] 05_case1_차트 - 수치 맥락 상실(Context Loss)\n\n")
        f.write("### 🚨 상황 분석\n")
        f.write("- **증상**: 숫자(85, 92...)만 추출되고, 이것이 X축(연도)인지 Y축(매출)인지, 범례(Apple/Samsung)인지 구분 불가능.\n")
        f.write("- **원인**: PDF 내 차트는 '이미지' 또는 '벡터 그래픽'으로 존재하며, 텍스트 레이어는 좌표값만 가지고 있어 시각적 관계 정보가 없음.\n\n")
        f.write("--- \n")
        f.write(f"### 📄 추출된 텍스트 결과\n")
        extracted_text = text if text.strip() else "(내용 없음)"
        f.write(f"```text\n{extracted_text[:300]}...\n```\n\n")
    print(f"✅ 실패 결과 생성: {output_md}")

if __name__ == "__main__":
    main()
