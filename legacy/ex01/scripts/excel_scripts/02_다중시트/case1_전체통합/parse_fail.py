import pandas as pd
import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_xlsx = os.path.join(current_dir, "../../../../data/docs/ex_excel/02_case1_시트필터.xlsx")
    output_md = os.path.join(current_dir, "../../../../data/processed/02_case1_전체통합_실패.md")
    
    print(f"🚀 [Excel Fail 02] 시트 옵션 무시 시도 중...")
    
    try:
        # 첫 번째 시트만 읽기 (기본값)
        df = pd.read_excel(input_xlsx)
        
        os.makedirs(os.path.dirname(output_md), exist_ok=True)
        with open(output_md, "w", encoding="utf-8") as f:
            f.write("# [Document Fail] 02_case1_전체통합 - Single Sheet Loading Only\n\n")
            f.write("### ❌ RAG 실패 원인 분석\n")
            f.write("- **증상**: 엑셀 내의 '주문내역', '고객정보' 시트가 존재함에도 불구하고, 첫 번째 시트(Sheet1)만 로드됨.\n")
            f.write("- **원인**: `pandas.read_excel()`은 기본적으로 첫 번째 시트만 로드하며, `sheet_name=None` 옵션 없이는 전체 시트 접근이 불가능함.\n\n")
            f.write("---\n")
            f.write("### 📄 정제된 텍스트 결과 (Sample)\n")
            f.write(df.head().to_markdown(index=False))
            
        print(f"✅ Excel 실패 결과 생성: {output_md}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
