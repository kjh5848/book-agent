import os
import fitz
import easyocr
import numpy as np
from PIL import Image
import io

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/04_case1_EasyOCR.pdf")
    output_path = os.path.join(current_dir, "../../../../data/processed/04_case1_EasyOCR_성공.md")
    
    print(f"🚀 [Success 04-1] EasyOCR 로컬 엔진 가동 중 (표준 인보이스 판독)...")
    
    if not os.path.exists(input_pdf):
        print(f"❌ 오류: 입력 파일을 찾을 수 없습니다. ({input_pdf})")
        return

    try:
        reader = easyocr.Reader(['ko', 'en'])
        doc = fitz.open(input_pdf)
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
        results = reader.readtext(np.array(img), detail=0)
        
        doc.close()
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# [Document Success] 04_case1_표준인보이스 - EasyOCR 기반 정형 문서 판독 결과\n\n")
            f.write("### ✅ RAG 최적화 분석\n")
            f.write("- **전략**: 로컬 `EasyOCR` 엔진을 사용하여 이미지 기반 PDF의 텍스트를 비용 없이 추출.\n")
            f.write("- **효과**: 정형화된 깨끗한 문서(인보이스 등)를 빠르게 데이터화하여 검색 인덱스 생성 가능.\n\n")
            f.write("---\n")
            f.write("### 📄 정제된 텍스트 결과 (List)\n\n")
            for text in results:
                f.write(f"- {text}\n")
            f.write("\n")
            
        print(f"✅ EasyOCR 판독 결과 저장 완료: {output_path}")
        
    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
