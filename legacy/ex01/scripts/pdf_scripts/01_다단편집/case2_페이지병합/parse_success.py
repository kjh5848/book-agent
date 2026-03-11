import pdfplumber
import os

def parse_성공_01_b():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/01_case2_페이지병합.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/01_case2_페이지병합_성공.md")
    
    print(f"🚀 [Success 01-B] 공간 정렬 파싱 시작: {input_pdf}")
    
    if not os.path.exists(input_pdf):
        print(f"❌ 에러: 파일을 찾을 수 없습니다. {input_pdf}")
        return

    with pdfplumber.open(input_pdf) as pdf:
        full_text = ""
        for page in pdf.pages:
            width = page.width
            middle = width / 2
            words = page.extract_words()
            
            left_col = [w for w in words if w['x1'] <= middle + 10]
            right_col = [w for w in words if w['x0'] > middle - 10]
            
            left_col.sort(key=lambda x: x['top'])
            right_col.sort(key=lambda x: x['top'])
            
            left_text = " ".join([w['text'] for w in left_col])
            right_text = " ".join([w['text'] for w in right_col])
            
            full_text += f"## Page {page.page_number}\n\n"
            full_text += "### [왼쪽 단]\n" + left_text + "\n\n"
            full_text += "### [오른쪽 단]\n" + right_text + "\n\n"
            
    os.makedirs(os.path.dirname(output_md), exist_ok=True)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# [문서 처리 성공] 01_case2_페이지병합 - 텍스트 스티칭(Stitching) 해결 결과\\n\\n")
        f.write("### RAG 최적화 분석\\n")
        f.write("- **전략**: 공간 좌표(x0) 기반으로 왼쪽/오른쪽 단을 물리적으로 분리(Cropping).\n")
        f.write("- **효과**: 문장 순서(`Reading Order`)가 복원되어 LLM이 문맥을 정확히 이해함.\n\n")
        f.write("---\n")
        f.write("### 정제된 텍스트 결과 (Markdown)\\n\\n")
        f.write("```markdown\n")
        f.write(full_text)
        f.write("\n```")
    print(f"성공 결과 생성 완료: {output_md}")

if __name__ == "__main__":
    parse_성공_01_b()
