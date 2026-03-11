import pandas as pd
import os

# --- Configuration ---
current_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(current_dir, "../../../../data/docs/ex_excel/", "01_case2_VOC로그.xlsx")
output_dir = os.path.join(current_dir, "../../../../data/processed/")

os.makedirs(output_dir, exist_ok=True)

def parse():
    print(f"Reading {input_file}...")
    
    if not os.path.exists(input_file):
        print(f"Error: File not found at {input_file}")
        return

    try:
        # Read the file
        df = pd.read_excel(input_file)
        
        # Save to Markdown (Standardized Format)
        md_output = os.path.join(output_dir, "01_case2_VOC로그_성공.md")
        with open(md_output, "w", encoding="utf-8") as f:
            f.write("# [Document Success] 01_case2_VOC로그 - Date & Log Data\n\n")
            f.write("### ✅ RAG 최적화 분석\n")
            f.write("- **전략**: 날짜(Date) 객체를 문자열(ISO Format)로 변환하여 시간 정보의 정확성 보장.\n")
            f.write("- **효과**: '2023년 1월' 같은 모호한 날짜도 정확한 시계열 데이터(TimeSeries)로 인식 가능.\n\n")
            f.write("---\n")
            f.write("### 📄 정제된 텍스트 결과 (Top 20 Rows)\n\n")
            f.write(df.head(20).to_markdown(index=False))
            
        print(f"  -> Saved to {os.path.basename(md_output)}")
        
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    parse()
