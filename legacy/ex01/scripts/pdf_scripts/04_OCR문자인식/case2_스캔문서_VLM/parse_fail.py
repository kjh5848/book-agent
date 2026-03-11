import os
import fitz

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/04_case2_스캔문서_VLM.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/04_case2_스캔문서_VLM_실패.md")
    
    print(f"❌ [Fail 04-2] 단순 텍스트 추출 시도 (왜곡 문서 왜곡 심화)...")
    
    if os.path.exists(input_pdf):
        doc = fitz.open(input_pdf)
        text = "".join([page.get_text() for page in doc])
        doc.close()
    else:
        text = "(파일 없음: 04_case2_스캔문서_VLM.pdf)"

    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# [Failure] 04_case2_스캔문서 - 왜곡으로 인한 정보 손실\n\n")
        f.write("### 🚨 상황 분석\n")
        f.write("- **증상**: 텍스트가 부분적으로 누락되거나, 단어가 끊어져서(St rat eg i c) 추출됨.\n")
        f.write("- **원인**: 문서가 기계적으로 스캔되는 과정에서 기울어짐(Skew)과 구겨짐이 발생하여, 일반적인 OCR 엔진이 글자 라인을 잡지 못함.\n\n")
        f.write("--- \n")
        f.write(f"### 📄 추출된 텍스트 결과\n")
        f.write(f"```text\n{text[:500]}...\n```\n\n")
        
    print(f"✅ 실패 결과 생성: {output_md}")

if __name__ == "__main__":
    main()
