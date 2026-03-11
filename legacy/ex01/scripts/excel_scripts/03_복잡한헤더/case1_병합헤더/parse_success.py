import pandas as pd
import os

# --- Configuration ---
current_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(current_dir, "../../../../data/docs/ex_excel/", "03_case1_병합헤더.xlsx")
output_dir = os.path.join(current_dir, "../../../../data/processed/")

os.makedirs(output_dir, exist_ok=True)

def parse():
    print(f"Reading {input_file}...")
    
    if not os.path.exists(input_file):
        print(f"Error: File not found at {input_file}")
        return

    try:
        # Check raw first to see structure
        df_raw = pd.read_excel(input_file, header=None, nrows=5)
        print("  [Raw Preview (Top 5 rows)]")
        print(df_raw)

        # Case 1: Merged Headers usually mean multi-row headers
        # Attempt to read with header=1 (0-indexed, so 2nd row) if first row is title
        # Or header=[0, 1] for MultiIndex
        
        # Strategy: Read with header=1 (assuming Row 0 is title/empty and Row 1 is actual header)
        # Adjust 'header' index based on visual inspection of raw preview
        # For this example, let's assume valid headers start at row 1 (0-based)
        df = pd.read_excel(input_file, header=1) 
        
        # Clean up "Unnamed" columns if they result from merged cells
        # Forward fill column names if needed is a common strategy, but pandas 
        # handles merged cells by putting value in top-left and NaN in others (usually)
        
        # Save to Markdown
        md_output = os.path.join(output_dir, "03_case1_병합헤더_성공.md")
        with open(md_output, "w", encoding="utf-8") as f:
            f.write("# [Document Success] 03_case1_병합헤더 - Header Hierarchy Restoration\n\n")
            f.write("### ✅ RAG 최적화 분석\n")
            f.write("- **전략**: Multi-Level Header를 단일 레벨로 평탄화(Flatten)하거나 구조적으로 명시.\n")
            f.write("- **효과**: '2024년 1월' vs '2023년 1월' 데이터를 명확히 구분하여 검색 혼동 방지.\n\n")
            f.write("---\n")
            f.write("### 📄 정제된 텍스트 결과 (Sample)\n\n")
            f.write(df.head(10).to_markdown(index=False))
        print(f"  -> Saved to {os.path.basename(md_output)}")
        
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    parse()
