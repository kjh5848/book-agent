import pandas as pd
import os

# 파일 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(current_dir, "../../../../data/docs/ex_excel/", "06_case1_이격된표.xlsx")
output_dir = os.path.join(current_dir, "../../../../data/processed/")
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "06_case1_이격된표_실패.md")

print(f"Reading {input_file}...")

# 1. 일반적인 읽기 (Pandas)
# 별도 옵션 없이 읽으면 두 개의 표가 엉망으로 섞임
df = pd.read_excel(input_file)

print("--- [Fail Load] (Mashed Tables) ---")
print(df.head(15))

# 2. 결과 저장
with open(output_file, "w", encoding="utf-8") as f:
    f.write("# [Document Fail] 06_case1_이격된표 - Multiple Tables Mixed\n\n")
    f.write("### ❌ RAG 실패 원인 분석\n")
    f.write("- **증상**: 시트에 여러 표가 존재할 때, 상단 표의 구조가 하단 표까지 영향을 미치거나 중간에 `NaN`이 포함됨.\n")
    f.write("- **원인**: `pandas.read_excel()`은 시트 전체를 하나의 테이블로 가정하고 읽기 때문에, 서로 다른 구조의 표들이 뒤섞여(Mixed) 문맥이 파괴됨.\n\n")
    f.write("---\n")
    f.write("### 📄 정제된 텍스트 결과 (Sample)\n")
    f.write(df.to_markdown(index=False))

print(f"  -> Saved failure case to {os.path.basename(output_file)}")
