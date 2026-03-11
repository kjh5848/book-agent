import pandas as pd
import os

# --- Configuration ---
current_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(current_dir, "../../../../data/docs/ex_excel/", "02_case2_일괄처리.xlsx")
output_dir = os.path.join(current_dir, "../../../../data/processed/")

os.makedirs(output_dir, exist_ok=True)

def parse():
    print(f"Reading {input_file}...")
    
    if not os.path.exists(input_file):
        print(f"Error: File not found at {input_file}")
        return

    try:
        # Read all sheets
        all_sheets = pd.read_excel(input_file, sheet_name=None)
        print(f"  Sheets found: {list(all_sheets.keys())}")
        
        # Save to single Markdown for better RAG context
        md_output = os.path.join(output_dir, "02_case2_일괄처리_성공.md")
        with open(md_output, "w", encoding="utf-8") as f:
            f.write("# [Document Success] 02_case2_일괄처리 - 전체 시트 일괄 통합 결과\n\n")
            for name, df in all_sheets.items():
                f.write(f"### 📂 시트: {name}\n")
                f.write(df.to_markdown(index=False))
                f.write("\n\n")
            f.write("> **Mentor's Note**: 모든 시트를 개별 파일로 쪼개는 대신, 하나의 마크다운 문서로 통합하여 LLM이 시트 간의 연관 관계를 한꺼번에 파악할 수 있도록 구성했습니다.")
        print(f"  -> Saved to {os.path.basename(md_output)}")
        
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    parse()
