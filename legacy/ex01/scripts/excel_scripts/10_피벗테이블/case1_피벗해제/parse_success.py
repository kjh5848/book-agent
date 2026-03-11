import pandas as pd
import os

# 파일 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(current_dir, "../../../../data/docs/ex_excel/", "10_case1_피벗해제.xlsx")
output_dir = os.path.join(current_dir, "../../../../data/processed/")
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "10_case1_피벗해제_성공.json")

print(f"Reading {input_file}...")

# 1. 일반적인 읽기 (병합된 셀은 NaN으로 나옴)
df = pd.read_excel(input_file)
print("--- [Raw Load] (Merged cells become NaN) ---")
print(df.head(10)) 
# 예상: 2024는 첫 행만 있고, 나머지 행의 연도/분기는 NaN

# 2. 전처리: 결측치 채우기 (Forward Fill)
# '연도', '분기' 컬럼이 병합되어 있으므로, 위에서 아래로 값을 채워야 함.
# ffill() 메서드는 이전 유효한 값을 다음 NaN에 복사함.

# 비즈니스 로직상 채워야 할 컬럼 지정
cols_to_fill = ["연도", "분기"]

# ffill 적용
df_clean = df.copy()
df_clean[cols_to_fill] = df_clean[cols_to_fill].ffill()

print("\n--- [Cleaned Load] (After ffill) ---")
print(df_clean.head(10))

# 3. 데이터 검증 (옵션)
# 만약 연도가 없는 행이 있다면 삭제하거나 에러 처리
if df_clean["연도"].isnull().any():
    print("Warning: Some rows still have NaN Years.")

# 4. 저장 (Markdown)
md_output = os.path.join(output_dir, "10_case1_피벗해제_성공.md")
with open(md_output, "w", encoding="utf-8") as f:
    f.write("# [Document Success] 10_case1_피벗해제 - Pivot Table Unmelting\n\n")
    f.write("### ✅ RAG 최적화 분석\n")
    f.write("- **전략**: `ffill()`을 사용하여 병합된 셀(Merged Cells)의 값을 아래로 전파.\n")
    f.write("- **효과**: 모든 행이 독립적인 문맥(Context)을 가지게 되어, 부분 검색 시에도 \"언제, 누구의 실적\"인지 정확히 파악 가능.\n\n")
    f.write("---\n")
    f.write("### 📄 정제된 텍스트 결과 (Sample)\n\n")
    f.write(df_clean.to_markdown(index=False))

print(f"  -> Saved to {os.path.basename(md_output)}")
