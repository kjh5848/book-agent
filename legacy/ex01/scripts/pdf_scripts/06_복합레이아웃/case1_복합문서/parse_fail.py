import fitz
import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/06_case1_복합문서.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/06_case1_복합문서_실패.md")
    
    print(f"🚀 [Failure 06] 기본 파서 시도 (레이아웃 무시): {input_pdf}")
    
    if not os.path.exists(input_pdf):
        print(f"❌ 에러: 파일을 찾을 수 없습니다. {input_pdf}")
        return

    doc = fitz.open(input_pdf)
    text = ""
    for page in doc:
        text += page.get_text()
    
    os.makedirs(os.path.dirname(output_md), exist_ok=True)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# [Failure] 06_case1_복합문서 - 레이아웃 붕괴(Layout Collapse)\n\n")
        f.write("### 🚨 상황 분석\n")
        f.write("- **증상**: 2단 다단 본문과 중간 표의 숫자들이 앞뒤 구분 없이 '한 줄'로 뒤섞여 추출됨.\n")
        f.write("- **원인**: 문서의 기하학적 영역(Zone)을 분석하지 않고, 단순히 글자가 나타나는 좌표 순서대로 텍스트를 나열했기 때문.\n\n")
        f.write("--- \n")
        f.write(f"### 📄 추출된 텍스트 결과\n")
        extracted_text = text if text.strip() else "(내용 없음)"
        f.write(f"```text\n{extracted_text[:300]}...\n```\n\n")
    
    print(f"✅ 실패 결과 생성: {output_md}")

if __name__ == "__main__":
    main()
