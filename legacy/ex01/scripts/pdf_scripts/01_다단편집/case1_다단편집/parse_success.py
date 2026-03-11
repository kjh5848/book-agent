import pdfplumber
import os

def parse_성공_01():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # ex01 폴더로 이동 (success -> 01_column -> pdf_scripts -> scripts -> ex01)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    input_pdf = os.path.join(current_dir, "../../../../data/docs/ex_pdf/01_case1_다단편집.pdf")
    output_md = os.path.join(current_dir, "../../../../data/processed/01_case1_다단편집_성공.md")
    
    print(f"🚀 [Success 01] 전처리 시작: {input_pdf}")
    
    if not os.path.exists(input_pdf):
        print(f"❌ 에러: 파일을 찾을 수 없습니다. {input_pdf}")
        return

    with pdfplumber.open(input_pdf) as pdf:
        full_text = ""
        for page in pdf.pages:
            # layout=True는 시각적 공백을 보존하므로, RAG용 텍스트 추출 시에는 오히려 방해가 될 수 있음.
            # x_tolerance=5로 설정하여 찢어진 글자(Shredding)를 강력하게 봉합.
            text = page.extract_text(x_tolerance=5)
            full_text += f"## Page {page.page_number}\n\n" + text + "\n\n"
            
    os.makedirs(os.path.dirname(output_md), exist_ok=True)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# [문서 처리 성공] 01_case1_다단편집 - 폰트 찢어짐(Shredding) 복원 결과\n\n")
        f.write("### RAG 최적화 분석\n")
        f.write("- **전략**: `x_tolerance=5` 설정으로 흩어진 자소(`대 한 민 국`)를 단어(`대한민국`)로 봉합.\n")
        f.write("- **효과**: 검색 가능한 온전한 키워드(Token) 확보.\n\n")
        f.write("---\n")
        f.write("### 정제된 텍스트 결과 (Markdown)\n\n")
        f.write(full_text)
    print(f"성공 결과 생성 완료: {output_md}")

if __name__ == "__main__":
    parse_성공_01()
