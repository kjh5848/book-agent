# 02_table_parsing.py
import fitz
import os

def step1_load_pdf(file_path: str) -> fitz.Document:
    """PDF 파일 로드하기"""
    print(f"[1] '{file_path}' 파일을 불러옵니다.")
    return fitz.open(file_path)

def step2_extract_tables_to_markdown(doc: fitz.Document) -> str:
    """PDF 내의 표(Table)를 찾아 Markdown 형식으로 변환"""
    print("[2] 표(Table) 구조를 추적하여 마크다운(Markdown)으로 정제합니다...\n")
    
    markdown_result = ""
    for page_num, page in enumerate(doc):
        # PyMuPDF의 훌륭한 find_tables() 메서드 활용
        tables = page.find_tables()
        if not tables:
            print(f"- {page_num+1}페이지: 발견된 표가 없습니다.")
            continue
            
        print(f"- {page_num+1}페이지: {len(tables)}개의 표를 통째로 낚아챘(!?)습니다.")
        
        for idx, table in enumerate(tables):
            # table.to_markdown() 하면 한 방에 마크다운 테이블( | | 형태 )로 변환 가능!
            # 하지만 초보자에게 구조를 보여주기 위해 row 순회 방식을 보여줍니다.
            
            headers = table.extract()[0]  # 첫 줄을 헤더로 가정
            rows = table.extract()[1:]    # 나머지를 데이터로 가정
            
            # 헤더(Header) 만들기
            markdown_result += f"### [추출된 표 {idx+1}]\n"
            markdown_result += "| " + " | ".join(headers) + " |\n"
            markdown_result += "|" + "|".join(["---"] * len(headers)) + "|\n"
            
            # 본문(Body) 만들기
            for row in rows:
                # 빈 셀(None)을 빈 문자열로 처리
                safe_row = [str(cell).strip() if cell is not None else "" for cell in row]
                markdown_result += "| " + " | ".join(safe_row) + " |\n"
            
            markdown_result += "\n"
            
    return markdown_result

def step3_print_result(md_text: str):
    """최종 마크다운 출력"""
    print("\n=== [변환된 마크다운 표] ===\n")
    print(md_text)
    print("=========================\n")
    print("💡 [달라진 점 찾기] 어때요? 이제 행과 열이 | 기호로 묶여서")
    print("LLM이 이 텍스트를 보면 '아하, 사원은 휴가가 3일이구나!' 라고 완벽히 이해할 수 있습니다.")

if __name__ == "__main__":
    print("=== [CH02-2] 심화 표(Table) 파싱 및 Markdown 변환 실습 ===")
    pdf_path = "data/dummy_rules.pdf"
    
    document = step1_load_pdf(pdf_path)
    md_table_text = step2_extract_tables_to_markdown(document)
    step3_print_result(md_table_text)
