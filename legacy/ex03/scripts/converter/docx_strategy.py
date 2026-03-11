import os
from docx import Document

def convert_docx_to_md(docx_path, output_path):
    """
    Word(DOCX) 파일을 마크다운으로 변환하는 전략
    - 단락(Paragraph) 구조 및 제목(Heading) 인식
    """
    print(f"[DOCX Strategy] Converting {docx_path}...")
    
    doc = Document(docx_path)
    md_content = []
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
            
        # 제목 스타일 처리 (기본적인 수준)
        if para.style.name.startswith('Heading'):
            level = para.style.name.split()[-1]
            try:
                level_int = int(level)
                md_content.append(f"{'#' * level_int} {text}")
            except:
                md_content.append(f"## {text}")
        else:
            md_content.append(text)
            
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n\n".join(md_content))
    
    print(f"  -> Saved to {output_path}")

if __name__ == "__main__":
    # Test code
    pass
