"""
[실습 1 - PDF 구조화 추출]
다단 편집된 문서와 내부에 포함된 표를 구조를 잃지 않고 마크다운으로 추출합니다.
"""
import os
import pdfplumber

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, '../../data/docs/hr/HR_취업규칙_v1.0.pdf')
OUTPUT_FILE = os.path.join(BASE_DIR, '../../parsed_data/success_results/01_HR_취업규칙_success.md')

def convert_pdf_to_md(pdf_path, md_path):
    print(f"📄 PDF 변환 시작: {os.path.basename(pdf_path)}")
    os.makedirs(os.path.dirname(md_path), exist_ok=True)
    
    md_content = ["# 취업규칙 (PDF 파싱 결과)\n"]
    
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            md_content.append(f"\n## --- Page {i+1} ---\n")
            
            # 1. 텍스트 추출 (레이아웃 유지)
            # layout=True: 다단(Multi-column) 텍스트가 섞이는(Shredding) 것을 방지
            # x_tolerance: 자간과 단어 사이의 거리를 조정하여 다단을 더 정확히 인식
            text = page.extract_text(layout=True, x_tolerance=2)
            if text:
                md_content.append(text)
            
            # 2. 표(Table) 추출
            table = page.extract_table({"x_tolerance": 2})
            if table:
                md_content.append("\n### [표 추출 성공]\n")
                # 헤더
                md_content.append("| " + " | ".join(map(str, table[0])) + " |")
                md_content.append("| " + " | ".join(["---"] * len(table[0])) + " |")
                # 데이터 행
                for row in table[1:]:
                    md_content.append("| " + " | ".join(map(str, row)) + " |")
                md_content.append("\n")
                
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_content))
    print(f"✅ 마크다운 변환 완료: {os.path.basename(md_path)}")

if __name__ == "__main__":
    convert_pdf_to_md(INPUT_FILE, OUTPUT_FILE)
