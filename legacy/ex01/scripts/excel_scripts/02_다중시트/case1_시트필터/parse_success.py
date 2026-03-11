import pandas as pd
import os
import json

# --- Configuration ---
current_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(current_dir, "../../../../data/docs/ex_excel/", "02_case1_시트필터.xlsx")
output_dir = os.path.join(current_dir, "../../../../data/processed/")

os.makedirs(output_dir, exist_ok=True)

def parse():
    print(f"Reading {input_file}...")
    
    if not os.path.exists(input_file):
        print(f"Error: File not found at {input_file}")
        return

    try:
        xls = pd.ExcelFile(input_file)
        print(f"  Sheets found: {xls.sheet_names}")
        
        data_bundle = {}
        target_sheets = ["고객정보", "주문내역"] # Example targets
        
        for sheet in xls.sheet_names:
            if sheet in target_sheets:
                print(f"  -> Processing sheet: {sheet}")
                df = pd.read_excel(xls, sheet_name=sheet)
                data_bundle[sheet] = df.to_dict(orient="records")
            else:
                 print(f"  -> Skipping sheet: {sheet}")

        # Save to Markdown
        md_output = os.path.join(output_dir, "02_case1_시트필터_성공.md")
        with open(md_output, "w", encoding="utf-8") as f:
            f.write("# [Document Success] 02_case1_시트필터 - Data & Order Selection\n\n")
            f.write("### ✅ RAG 최적화 분석\n")
            f.write("- **전략**: '고객정보'와 '주문내역' 시트만 선별(Filtering)하여 통합 문서 생성.\n")
            f.write("- **효과**: 임시 시트나 백업 데이터를 배제하여, 검색 엔진이 정확한 원본 데이터만 참조하도록 보장.\n\n")
            f.write("---\n")
            f.write("### 📄 정제된 텍스트 결과\n\n")
            
            for sheet_name, records in data_bundle.items():
                f.write(f"#### 📌 시트: {sheet_name}\n")
                temp_df = pd.DataFrame(records)
                f.write(temp_df.to_markdown(index=False))
                f.write("\n\n")
        print(f"  -> Saved to {os.path.basename(md_output)}")
        
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    parse()
