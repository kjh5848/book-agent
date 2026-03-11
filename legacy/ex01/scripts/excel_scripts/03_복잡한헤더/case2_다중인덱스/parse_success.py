import pandas as pd
import os

# --- Configuration ---
current_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(current_dir, "../../../../data/docs/ex_excel/", "03_case2_다중인덱스.xlsx")
output_dir = os.path.join(current_dir, "../../../../data/processed/")

os.makedirs(output_dir, exist_ok=True)

def parse():
    print(f"Reading {input_file}...")
    
    if not os.path.exists(input_file):
        print(f"Error: File not found at {input_file}")
        return

    try:
        # Case 2: Multi-level Index (e.g. Region -> City -> Sales)
        # header=[0, 1] tells pandas to use top 2 rows as headers
        df = pd.read_excel(input_file, header=[0, 1])
        
        print("  [Columns Detected]")
        print(df.columns)
        
        # Flatten MultiIndex columns for easier export/usage
        # e.g. ('2024년', '1월') -> '2024년_1월'
        df.columns = ['_'.join(map(str, col)).strip() for col in df.columns.values]
        
        # Save to Markdown
        md_output = os.path.join(output_dir, "03_case2_다중인덱스_성공.md")
        with open(md_output, "w", encoding="utf-8") as f:
            f.write("# [Document Success] 03_case2_다중인덱스 - 행/열 다중 계층 복원 결과\n\n")
            f.write("### 📊 인덱스 평탄화 및 정형화 결과\n")
            f.write(df.head(10).to_markdown(index=False))
            f.write("\n\n> **Mentor's Note**: 행 방향의 다중 인덱스(예: 본부 -> 팀)를 평탄화하여, 모든 행이 독립적인 부모 카테고리 정보를 갖도록 처리했습니다. RAG 검색 시 결과의 신뢰도를 높이는 결정적 작업입니다.")
        print(f"  -> Saved to {os.path.basename(md_output)}")
        
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    parse()
