"""
[실패 사례 - 단순 PDF 텍스트 파싱]
일반적인 방식으로 PDF의 텍스트만 긁어올 경우 발생하는 '다단 텍스트 섞임(Shredding)'과 '표 구조 파괴'를 보여줍니다.
"""
import os
import pdfplumber

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, '../../data/docs/hr/HR_취업규칙_v1.0.pdf')
OUTPUT_FILE = os.path.join(BASE_DIR, '../../parsed_data/fail_results/01_HR_취업규칙_fail.md')

def parse_pdf_naive(pdf_path, md_path):
    print(f"📄 단순 PDF 텍스트 추출 시작: {os.path.basename(pdf_path)}")
    os.makedirs(os.path.dirname(md_path), exist_ok=True)
    
    md_content = ["# 취업규칙 (단순 파싱 실패 사례)\n"]
    
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            md_content.append(f"\n## --- Page {i+1} ---\n")
            
            # [실패 원인] layout=True 옵션이 없어서 다단 텍스트가 왼쪽-오른쪽 짬짜면으로 섞여 나옵니다.
            # 표(Table) 역시 구조를 잃고 일반 텍스트로 뒤섞입니다.
            text = page.extract_text()
            if text:
                md_content.append(text)
                md_content.append("\n")
                
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_content))
    print(f"❌ 단순 변환 완료 (다단 섞임 발생): {os.path.basename(md_path)}")

if __name__ == "__main__":
    parse_pdf_naive(INPUT_FILE, OUTPUT_FILE)
