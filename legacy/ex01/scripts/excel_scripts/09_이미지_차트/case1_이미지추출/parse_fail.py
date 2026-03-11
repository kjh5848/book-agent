import pandas as pd
import os

# 파일 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(current_dir, "../../../../data/docs/ex_excel/", "09_case1_이미지추출.xlsx")
output_dir = os.path.join(current_dir, "../../../../data/processed/")
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "09_case1_이미지추출_실패.md")

print(f"Reading {input_file}...")

# 1. 일반적인 읽기 (Pandas)
# 이미지는 무시되고 텍스트만 읽힘
df = pd.read_excel(input_file, header=None)

print("--- [Fail Load] (Images Ignored) ---")
print(df)

# 2. 결과 저장
with open(output_file, "w", encoding="utf-8") as f:
    f.write("# [Document Fail] 09_case1_이미지추출 - Images/Charts Ignored\n\n")
    f.write("### ❌ RAG 실패 원인 분석\n")
    f.write("- **증상**: 엑셀의 핵심 데이터(매출 차트, 제품 사진 등)가 **이미지** 객체로 존재할 때, Pandas는 이를 완전히 무시함.\n")
    f.write("- **원인**: `pandas.read_excel()`은 텍스트/숫자 데이터만 읽을 수 있으며, 시각적 객체(Drawing Objects)는 로드 대상에서 제외됨.\n\n")
    f.write("---\n")
    f.write("### 📄 정제된 텍스트 결과 (Sample)\n")
    f.write(df.to_markdown(index=False))

print(f"  -> Saved failure case to {os.path.basename(output_file)}")
