import os
import pdfplumber

def convert_pdf_to_md(pdf_path, output_path):
    """
    PDF 파일을 마크다운으로 변환하는 전략
    - 텍스트 추출 및 기본적인 레이아웃 유지 시도
    """
    print(f"[PDF Strategy] Converting {pdf_path}...")
    
    with pdfplumber.open(pdf_path) as pdf:
        full_text = []
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                full_text.append(f"## Page {i+1}\n\n{text}")
        
        md_content = "\n\n".join(full_text)
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"  -> Saved to {output_path}")

if __name__ == "__main__":
    # Test code
    pass
