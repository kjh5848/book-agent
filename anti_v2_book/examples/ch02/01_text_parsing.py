# 01_text_parsing.py
import fitz  # PyMuPDF
import os

def step1_load_pdf(file_path: str) -> fitz.Document:
    """PDF 파일 로드하기"""
    print(f"[1] '{file_path}' 파일을 불러옵니다.")
    if not os.path.exists(file_path):
        raise FileNotFoundError("PDF 파일이 없습니다. 먼저 00_setup_pdf.py를 실행하세요!")
    return fitz.open(file_path)

def step2_extract_basic_text(doc: fitz.Document) -> str:
    """기본 메서드로 텍스트만 추출해보기 (한계점 체감용)"""
    print("[2] PyMuPDF의 기본 기능(get_text)으로 텍스트를 추출합니다.\n")
    
    full_text = ""
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        full_text += text
        
    return full_text

def step3_print_issues(extracted_text: str):
    """결과 출력 및 문제점 분석"""
    print("=== [추출된 텍스트 결과] ===")
    print(extracted_text)
    print("===========================\n")
    print("🤔 [생각해보기] 결과물에서 '표(Table)' 데이터가 어떻게 깨졌는지 확인하셨나요?")
    print("단순히 get_text()만 쓰면, 표 안의 데이터가 줄바꿈 덩어리로 변해서")
    print("AI(LLM)가 맥락(행과 열의 구조)을 전혀 이해하지 못하게 됩니다.")
    print("이것이 우리가 다음 실습(02_table_parsing.py)에서 표를 정교하게 분리해야 하는 이유입니다!")

if __name__ == "__main__":
    print("=== [CH02-1] 기초 텍스트 파싱 실습 ===")
    pdf_path = "data/dummy_rules.pdf"
    
    document = step1_load_pdf(pdf_path)
    text_result = step2_extract_basic_text(document)
    step3_print_issues(text_result)
