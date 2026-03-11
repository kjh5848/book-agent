"""
[실패 사례 - 단순 Word 텍스트 파싱]
Word 문서 내부에 지정된 '제목', '본문' 등의 계층 스타일(Style)을 무시하고 텍스트만 뽑아냈을 때 발생하는 문맥 상실을 보여줍니다.
"""
import os
from docx import Document

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, '../../data/docs/sec/SEC_보안규정_v1.0.docx')
OUTPUT_FILE = os.path.join(BASE_DIR, '../../parsed_data/fail_results/03_SEC_보안규정_fail.md')

def parse_word_naive(docx_path, md_path):
    print(f"📝 단순 Word 텍스트 추출 시작: {os.path.basename(docx_path)}")
    os.makedirs(os.path.dirname(md_path), exist_ok=True)
    
    doc = Document(docx_path)
    md_content = ["# 보안규정 (단순 파싱 실패 사례)\n"]
    
    # [실패 원인] 모든 문단을 동일한 가중치의 평문(Flat text)으로 추출합니다.
    # 이 문서가 쪼개져서 벡터DB에 들어갈 경우, AI는 현재 텍스트가 어느 대제목에 속하는지 문맥을 잃어버립니다.
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            md_content.append(text)
            
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_content))
    print(f"❌ 단순 변환 완료 (계층구조 상실): {os.path.basename(md_path)}")

if __name__ == "__main__":
    parse_word_naive(INPUT_FILE, OUTPUT_FILE)
