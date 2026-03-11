import pandas as pd
import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_xlsx = os.path.join(current_dir, "../../../../data/docs/ex_excel/03_case1_병합헤더.xlsx")
    output_md = os.path.join(current_dir, "../../../../data/processed/03_case1_병합헤더_실패.md")
    
    print(f"🚀 [Excel Fail 03] 병합 헤더 무시 시도 중...")
    
    try:
        # 병합된 헤더를 고려하지 않고 기본으로 읽기
        df = pd.read_excel(input_xlsx)
        
        os.makedirs(os.path.dirname(output_md), exist_ok=True)
        with open(output_md, "w", encoding="utf-8") as f:
            f.write("# [Document Fail] 03_case1_병합헤더 - Broken Header Structure\n\n")
            f.write("### ❌ RAG 실패 원인 분석\n")
            f.write("- **증상**: `Unnamed: 1`, `Unnamed: 2` 등 의미 없는 컬럼명이 생성되고, 상위 헤더 정보가 소실됨.\n")
            f.write("- **원인**: `pandas`는 기본적으로 단일 헤더만 인식하므로, 병합된(Multi-level) 헤더를 평탄화하지 않으면 데이터의 의미를 파악할 수 없음.\n\n")
            f.write("---\n")
            f.write("### 📄 정제된 텍스트 결과 (Sample)\n")
            f.write(df.head(5).to_markdown(index=False))
            
        print(f"✅ Excel 실패 결과 생성: {output_md}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
