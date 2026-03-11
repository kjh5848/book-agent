import fitz
import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/04_case1_EasyOCR.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/04_case1_EasyOCR_실패.md")
    
    print(f"🚀 [Fail 04-1] 단순 텍스트 추출 시도 (PyMuPDF)...")
    
    if not os.path.exists(input_pdf):
        print(f"❌ 오류: 입력 파일을 찾을 수 없습니다. ({input_pdf})")
        return

    try:
        doc = fitz.open(input_pdf)
        extracted_text = ""
        for page in doc:
            extracted_text += page.get_text()
        
        doc.close()
        
        with open(output_md, "w", encoding="utf-8") as f:
            f.write("# [Failure] 04_case1_EasyOCR - 단순 텍스트 추출 실패\n\n")
            f.write("### 🚨 상황 분석\n")
            f.write("- **증상**: `page.get_text()` 호출 시 아무런 내용도 반환되지 않음 (Empty String).\n")
            f.write("- **원인**: 문서가 스캔 이미지(Image-only PDF)로 구성되어 있어, 텍스트 레이어가 존재하지 않기 때문임.\n\n")
            f.write("--- \n")
            f.write(f"### 📄 추출된 텍스트 결과\n")
            extracted_text = extracted_text if extracted_text.strip() else "(아무런 텍스트도 추출되지 않았습니다)"
            f.write(f"```text\n{extracted_text}\n```\n\n")
            
        print(f"✅ 실패 시나리오 결과 생성 완료: {output_md}")
        
    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
