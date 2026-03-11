"""
[실패 사례 - 복합 도해 스캔본 텍스트 추출]
배경에 텍스트가 박혀있거나 도해가 복잡한 스캔본 PDF를 일반 텍스트 파서로 밀었을 때 발생하는 외계어 현상을 보여줍니다.
"""
import os
import pdfplumber

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_PDF = os.path.join(BASE_DIR, '../../data/docs/ops/OPS_운영보고서_v1.0.pdf')
OUTPUT_FILE = os.path.join(BASE_DIR, '../../parsed_data/fail_results/04_OPS_복합파싱_fail.md')

def parse_vision_naive(pdf_path, md_path):
    print(f"📄 복합 도해 단순 텍스트 추출 시작: {os.path.basename(pdf_path)}")
    os.makedirs(os.path.dirname(md_path), exist_ok=True)
    
    md_content = ["# 운영보고서 (단순 파싱 실패 사례)\n"]
    
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            md_content.append(f"\n## --- Page {i+1} ---\n")
            
            # [실패 원인] 프레젠테이션처럼 텍스트 박스가 둥둥 떠다니는 문서의 경우, 
            # OCR이나 단순 추출 파서가 읽어내는 순서가 인간의 시선과 완전히 달라 '외계어'가 됩니다.
            text = page.extract_text()
            if text:
                md_content.append(text)
                
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_content))
    print(f"❌ 단순 변환 완료 (외계어 발생, 도해 내용 상실): {os.path.basename(md_path)}")

if __name__ == "__main__":
    parse_vision_naive(INPUT_PDF, OUTPUT_FILE)
