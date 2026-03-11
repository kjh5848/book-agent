import os
import fitz

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/04_case4_저화질.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/04_case4_저화질_실패.md")
    
    print(f"❌ [Fail 04-4] 저화질 노이즈로 인한 판독 불가 시뮬레이션...")
    
    if os.path.exists(input_pdf):
        doc = fitz.open(input_pdf)
        text = "".join([page.get_text() for page in doc])
        doc.close()
    else:
        text = "(파일 없음)"

    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# [Failure] 04_case4_저화질 - 픽셀 뭉개짐(Pixelation)\n\n")
        f.write("### 🚨 상황 분석\n")
        f.write("- **증상**: 글자의 획이 서로 뭉쳐서 'R'이 'B'로, '1'이 'l'로 오인식됨.\n")
        f.write("- **원인**: 문서의 해상도(DPI)가 낮아 OCR 엔진이 글자의 경계선(Edge)을 명확히 따지 못함.\n\n")
        f.write("--- \n")
        f.write(f"### 📄 추출된 텍스트 결과\n")
        extracted_text = text if text.strip() else "(내용 없음)"
        f.write(f"```text\n{extracted_text[:300]}...\n```\n\n")
        
    print(f"✅ 실패 결과 생성: {output_md}")

if __name__ == "__main__":
    main()
