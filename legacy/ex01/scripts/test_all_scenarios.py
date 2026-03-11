import fitz  # PyMuPDF
import os
import re
from datetime import datetime

def parse_pdf_to_markdown(pdf_path, output_path):
    """
    일반적인 텍스트 기반 PDF 파서 (PyMuPDF 사용)
    """
    if not os.path.exists(pdf_path):
        return False

    try:
        doc = fitz.open(pdf_path)
        file_name = os.path.basename(pdf_path)
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        markdown_content = f"""---
title: {file_name}
type: RAG_VULNERABILITY_TEST_RESULT
date: {current_date}
source: {pdf_path}
---

# RAG 전처리 테스트 결과: {file_name}

> [!NOTE] 
> 본 문서는 일반적인 텍스트 기반 파서(PyMuPDF)로 추출된 결과입니다. 
> 원본 PDF의 복잡한 레이아웃(다단, 표 등)이 어떻게 파괴되었는지 확인해 보세요.

"""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            
            markdown_content += f"## Page {page_num + 1}\n\n"
            
            # 기본적인 헤더 변환 시도
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if not line: continue
                
                if re.match(r'^\d+\.\s+', line):
                    markdown_content += f"### {line}\n\n"
                elif re.match(r'^\d+\.\d+', line):
                    markdown_content += f"#### {line}\n\n"
                else:
                    markdown_content += f"{line}  \n"
            
            markdown_content += "\n"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        doc.close()
        return True
    except Exception as e:
        print(f"❌ {pdf_path} 처리 중 에러: {str(e)}")
        return False

def main():
    # 경로 설정
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # ex01
    input_root = os.path.join(base_dir, "data/docs")
    output_root = os.path.join(base_dir, "data/output")
    
    scenarios = [
        ("hr/HR_사내규정_다단.pdf", "01_다단_파괴_테스트.md"),
        ("onboarding/ONB_입사가이드_투명표.pdf", "02_투명표_인식_테스트.md"),
        ("security/SEC_보안정책_노이즈.pdf", "03_헤더푸터_노이즈_테스트.md"),
        ("security/SEC_보안규정_스캔.pdf", "04_OCR_스캔_테스트.md"),
        ("ops/OPS_성과평가_차트.pdf", "05_차트_비전_테스트.md"),
    ]

    print("🚀 5종 RAG 취약점 시나리오 전처리 테스트 시작")
    print("-" * 50)

    for pdf_rel_path, md_name in scenarios:
        pdf_path = os.path.join(input_root, pdf_rel_path)
        output_path = os.path.join(output_root, md_name)
        
        if os.path.exists(pdf_path):
            success = parse_pdf_to_markdown(pdf_path, output_path)
            if success:
                print(f"✅ 성공: {pdf_rel_path} -> {md_name}")
            else:
                print(f"❌ 실패: {pdf_rel_path}")
        else:
            print(f"⚠️ 건너뜀 (파일 없음): {pdf_rel_path}")

    print("-" * 50)
    print(f"🎉 모든 테스트 완료! 결과 확인: {output_root}")

if __name__ == "__main__":
    main()
