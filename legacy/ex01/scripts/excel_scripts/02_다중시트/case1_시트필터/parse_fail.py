import pandas as pd
import os

# 파일 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
# Note: Case 02 has two sub-cases. Let's pick case2_일괄처리 for failure demo or case1.
# Case 1 is Sheet Filter, Case 2 is Batch Process.
# Let's use Case 2 data which likely has multiple comparable sheets.
# Actually, Case 1 data also has multiple sheets. Let's use Case 1 for now.
input_file = os.path.join(current_dir, "../../../../data/docs/ex_excel/", "02_case1_시트필터.xlsx")
output_dir = os.path.join(current_dir, "../../../../data/processed/")
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "02_case1_시트필터_실패.md")

print(f"Reading {input_file}...")

# 1. 일반적인 읽기 (Pandas Default)
# sheet_name을 지정하지 않으면 첫 번째 시트만 읽음
df = pd.read_excel(input_file)

print("--- [Fail Load] (Only First Sheet) ---")
print(df.head())

# 2. 결과 저장
with open(output_file, "w", encoding="utf-8") as f:
    f.write("# [Document Fail] 02_case1_시트필터 - Missing Sheets\n\n")
    f.write("### ❌ RAG 실패 원인 분석\n")
    f.write("- **증상**: 엑셀 파일 내의 다른 시트(Sheet2, Sheet3 등)가 누락되고 **첫 번째 시트**만 읽힘.\n")
    f.write("- **원인**: `pandas.read_excel()`은 기본적으로 첫 번째 시트만 로드하므로, 중요 정보가 다른 시트에 있을 경우 검색 누락(Retrieval Failure) 발생.\n\n")
    f.write("---\n")
    f.write("### 📄 정제된 텍스트 결과 (Sample)\n")
    f.write(df.to_markdown(index=False))

print(f"  -> Saved failure case to {os.path.basename(output_file)}")
