import fitz
import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/06_case1_복합보고서.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/06_case2_복합보고서_실패.md")
    
    print(f"🚀 [Failure 06-2] 기본 파서 시도 (레이아웃 무시): {input_pdf}")
    
    if not os.path.exists(input_pdf):
        print(f"❌ 에러: 파일을 찾을 수 없습니다. {input_pdf}")
        return

    doc = fitz.open(input_pdf)
    text = ""
    for page in doc:
        text += f"\n--- Page {page.number + 1} ---\n"
        text += page.get_text()
    
    os.makedirs(os.path.dirname(output_md), exist_ok=True)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# [Failure] 06_case2_복합보고서 - 통합 레이아웃 붕괴\n\n")
        f.write("### 🚨 상황 분석\n")
        f.write("- **증상**: 다단 텍스트, 투명표, 사이드바 정보가 페이지마다 뒤엉켜 추출됨. 특히 연속표의 경우 헤더 없이 데이터만 나열되어 의미를 잃음.\n")
        f.write("- **원인**: 문서의 기하학적 영역 분할 및 헤더 캐싱 로직 부재로 인해 모든 요소가 하나의 선형 텍스트 흐름으로 강제 통합됨.\n\n")
        f.write("--- \n")
        f.write(f"### 📄 추출된 텍스트 결과 (일부)\n")
        extracted_text = text if text.strip() else "(내용 없음)"
        f.write(f"```text\n{extracted_text[:500]}...\n```\n\n")
    
    print(f"✅ 실패 결과 생성: {output_md}")

if __name__ == "__main__":
    main()
