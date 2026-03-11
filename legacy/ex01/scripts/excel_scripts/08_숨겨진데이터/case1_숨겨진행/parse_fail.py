import pandas as pd
import os

# 파일 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(current_dir, "../../../../data/docs/ex_excel/", "08_case1_숨겨진행.xlsx")
output_dir = os.path.join(current_dir, "../../../../data/processed/")
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "08_case1_숨겨진행_실패.md")

print(f"Reading {input_file}...")

# 1. 일반적인 읽기 (Pandas)
# 숨겨진 행도 일반 데이터처럼 읽힘
df = pd.read_excel(input_file)

print("--- [Fail Load] (Hidden Rows Included) ---")
print(df)

# 2. 결과 저장
with open(output_file, "w", encoding="utf-8") as f:
    f.write("# [Document Fail] 08_case1_숨겨진행 - Hidden Rows Included\n\n")
    f.write("### ❌ RAG 실패 원인 분석\n")
    f.write("- **증상**: 엑셀에서 '숨기기' 처리한 데이터(구형 모델, 폐기 등)가 포함되어 검색 결과에 노출됨.\n")
    f.write("- **원인**: `pandas.read_excel()`은 숨겨진 행(Hidden Rows) 속성을 무시하고 모든 값을 읽어오므로, 사용자가 제외 의도로 숨긴 데이터가 RAG에 유입됨.\n\n")
    f.write("---\n")
    f.write("### 📄 정제된 텍스트 결과 (Sample)\n")
    f.write(df.to_markdown(index=False))

print(f"  -> Saved failure case to {os.path.basename(output_file)}")
