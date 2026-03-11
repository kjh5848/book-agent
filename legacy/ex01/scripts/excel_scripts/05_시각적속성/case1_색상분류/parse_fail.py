import pandas as pd
import os

# 파일 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(current_dir, "../../../../data/docs/ex_excel/", "05_case1_색상분류.xlsx")
output_dir = os.path.join(current_dir, "../../../../data/processed/")
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "05_case1_색상분류_실패.md")

print(f"Reading {input_file}...")

# 1. 일반적인 읽기 (Pandas)
df = pd.read_excel(input_file)

print("--- [Fail Load] (Colors Ignored) ---")
print(df.head())

# 2. Markdown 저장 (to_markdown 대신 수동 변환 or CSV)
# tabulate 의존성을 피하기 위해 간단한 포맷팅 사용
markdown_table = df.to_string(index=False) 
# to_string은 마크다운 테이블은 아니지만 텍스트 덤프임.
# 명확한 비교를 위해 CSV 덤프 후 마크다운 코드블록에 넣음.

with open(output_file, "w", encoding="utf-8") as f:
    f.write("# [Document Fail] 05_case1_색상분류 - Visual Attributes Ignored\n\n")
    f.write("### ❌ RAG 실패 원인 분석\n")
    f.write("- **증상**: 엑셀 셀의 배경색(빨강, 노랑 등)으로 표현된 긴급도 정보가 파이썬 로드 과정에서 완전히 사라짐.\n")
    f.write("- **원인**: `pandas.read_excel()`은 데이터 '값'만 읽어올 뿐, 셀 스타일(배경색, 폰트 등)의 문맥(Context) 정보는 무시하기 때문임.\n\n")
    f.write("---\n")
    f.write("### 📄 정제된 텍스트 결과 (Sample)\n")
    f.write(df.head(10).to_markdown(index=False))

print(f"  -> Saved failure case to {os.path.basename(output_file)}")
