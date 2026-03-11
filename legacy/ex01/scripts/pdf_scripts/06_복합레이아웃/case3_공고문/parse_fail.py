import fitz
import os
import glob

def main():
    # 고정된 절대 경로 사용
    project_root = "/Users/nomadlab/Desktop/김주혁/workspace/coding-study/ai-llm-rag"
    pdf_dir = os.path.join(project_root, "실습용/ex01/data/docs/ex_pdf")
    
    # 공고문 파일명에 특수문자/인코딩 문제가 있을 수 있으므로 패턴으로 찾기
    search_pattern = os.path.join(pdf_dir, "06_case3_복합*.pdf")
    found_files = glob.glob(search_pattern)
    
    if not found_files:
        print(f"❌ 에러: 파일을 찾을 수 없습니다. {search_pattern}")
        return
        
    input_pdf = found_files[0]
    output_md = os.path.join(project_root, "실습용/ex01/data/processed/06_case3_공고문_실패.md")
    
    print(f"🚀 [Failure 06-3] 기본 파서 시도 (실제 공고문): {input_pdf}")
    
    doc = fitz.open(input_pdf)
    text = ""
    for page in doc:
        text += f"\n--- Page {page.number + 1} ---\n"
        text += page.get_text()
    
    os.makedirs(os.path.dirname(output_md), exist_ok=True)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# [Failure] 06_case3_공고문 - 실전 문서 레이아웃 붕괴\n\n")
        f.write("### 🚨 상황 분석\n")
        f.write("- **증상**: 정부 공고문의 복잡한 중첩 리스트, 요건 표, 지원 금액 테이블이 단순 텍스트로 나열되어 가독성이 심각하게 저하됨.\n")
        f.write("- **원인**: 표의 행/열 구분 없이 좌표 순서대로 글자가 추출되어, '지원 항목'과 '금액'의 연결 고리가 끊어짐. LLM이 요건을 오인할 가능성이 매우 높음.\n\n")
        f.write("--- \n")
        f.write(f"### 📄 추출된 텍스트 결과 (일부)\n")
        extracted_text = text if text.strip() else "(내용 없음)"
        f.write(f"```text\n{extracted_text[:700]}...\n```\n\n")
    
    print(f"✅ 실패 결과 생성: {output_md}")

if __name__ == "__main__":
    main()
