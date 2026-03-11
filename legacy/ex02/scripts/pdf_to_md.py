import fitz  # PyMuPDF
import os
from datetime import datetime

def parse_pdf_to_markdown(pdf_path, output_path):
    """
    PDF를 읽어서 YAML 메타데이터와 마크다운 구조를 갖춘 파일로 저장합니다.
    """
    print(f"📂 표준화 작업 시작: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"❌ 에러: 파일을 찾을 수 없습니다.")
        return

    doc = fitz.open(pdf_path)
    
    # 1. 메타데이터 생성 (자동화)
    file_name = os.path.basename(pdf_path)
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    markdown_content = f"""---
title: {file_name}
author: AI 업무 비서 시스템
date: {current_date}
source: {pdf_path}
---

"""
    import re

    # 2. 본문 추출 및 헤더 구조화
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        
        # 페이지 구분 출력
        markdown_content += f"## Page {page_num + 1}\n\n"
        
        # 줄 단위로 분석하여 헤더 변환
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if not line: continue
            
            # 패턴 1: '1. 제목' 형식 (Level 1 헤더 -> ###)
            if re.match(r'^\d+\.\s+', line):
                markdown_content += f"### {line}\n\n"
            # 패턴 2: '1.1 제목' 또는 '1.1'만 있는 경우 (Level 2 헤더 -> ####)
            elif re.match(r'^\d+\.\d+', line):
                # 만약 줄이 숫자만 있다면 다음 줄과 합치기 (선택 사항)
                markdown_content += f"#### {line}\n\n"
            else:
                markdown_content += f"{line}  \n" # 일반 본문 (줄바꿈 유지용 스페이스 2개)
        
        markdown_content += "\n"

    # 3. .md 파일로 저장
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"✅ 표준 마크다운 문서 생성 완료: {output_path}")
    print("-" * 50)
    print(markdown_content) # 생성된 마크다운 내용 출력
    print("-" * 50)

if __name__ == "__main__":
    # 실습용 샘플 파일 경로
    input_pdf = "data/metacoding_사내_규정_및_정책.pdf"
    output_md = "parsed_data/standard_policy.md"
    
    parse_pdf_to_markdown(input_pdf, output_md)
