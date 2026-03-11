import os
import fitz

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/04_case3_손글씨.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/04_case3_손글씨_실패.md")
    
    print(f"❌ [Fail 04-3] 손글씨 인식 실패 시뮬레이션...")
    
    if os.path.exists(input_pdf):
        doc = fitz.open(input_pdf)
        text = "".join([page.get_text() for page in doc])
        doc.close()
    else:
        text = "(파일 없음)"

    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# [Failure] 04_case3_손글씨 - 인식 불가 및 오인식\n\n")
        f.write("### 🚨 상황 분석\n")
        f.write("- **증상**: 손글씨가 아예 추출되지 않거나, 특수 기호(%, #) 등으로 깨져서 나옴.\n")
        f.write("- **원인**: 일반적인 OCR 모델은 인쇄체(Typed Text) 학습 비중이 높아, 사람의 필기체 특징점(획의 연결 등)을 인식하지 못함.\n\n")
        f.write("--- \n")
        f.write(f"### 📄 추출된 텍스트 결과\n")
        extracted_text = text if text.strip() else "(내용 없음)"
        f.write(f"```text\n{extracted_text[:300]}...\n```\n\n")
        
    print(f"✅ 실패 결과 생성: {output_md}")

if __name__ == "__main__":
    main()
