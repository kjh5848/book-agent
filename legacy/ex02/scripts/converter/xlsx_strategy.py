import os
import pandas as pd

def convert_xlsx_to_md(xlsx_path, output_path):
    """
    Excel(XLSX) 파일을 마크다운으로 변환하는 전략
    - 시트별 표(Table) 구조 유지
    """
    print(f"[XLSX Strategy] Converting {xlsx_path}...")
    
    sheets = pd.read_excel(xlsx_path, sheet_name=None)
    md_content = []
    
    for sheet_name, df in sheets.items():
        md_content.append(f"## Sheet: {sheet_name}")
        # NaN 처리 및 마크다운 표 변환
        md_table = df.fillna("").to_markdown(index=False)
        md_content.append(md_table)
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n\n".join(md_content))
    
    print(f"  -> Saved to {output_path}")

if __name__ == "__main__":
    # Test code
    pass
