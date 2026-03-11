import pandas as pd
import os

# 파일 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(current_dir, "../../../../data/docs/ex_excel/", "10_case1_피벗해제.xlsx")
output_dir = os.path.join(current_dir, "../../../../data/processed/")
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "10_case1_피벗해제_실패.md")

print(f"Reading {input_file}...")

# 1. 일반적인 읽기 (Pandas)
# 병합된 셀은 맨 위 셀만 값을 갖고, 나머지는 NaN 처리됨
df = pd.read_excel(input_file)

print("--- [Fail Load] (Merged Cells as NaN) ---")
print(df.head(10))

# 2. 결과 저장
with open(output_file, "w", encoding="utf-8") as f:
    f.write("# [Document Fail] 10_case1_피벗해제 - Merged Cells (NaN)\n\n")
    f.write("### ❌ RAG 실패 원인 분석\n")
    f.write("- **증상**: 병합된 셀(Merged Cells)이 포함된 피벗 테이블을 읽으면, 첫 번째 셀만 값을 갖고 나머지는 `NaN`으로 비어있음.\n")
    f.write("- **원인**: 엑셀의 시각적 그룹핑(병합)은 데이터적으로는 '빈 셀'로 취급되므로, `ffill` 등으로 평탄화하지 않으면 상위 그룹 정보가 소실됨.\n\n")
    f.write("---\n")
    f.write("### 📄 정제된 텍스트 결과 (Sample)\n")
    f.write(df.to_markdown(index=False))

print(f"  -> Saved failure case to {os.path.basename(output_file)}")
