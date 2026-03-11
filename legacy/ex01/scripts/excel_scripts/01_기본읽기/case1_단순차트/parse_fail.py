import pandas as pd
import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 가상 시나리오를 위한 경로 설정
    input_xlsx = os.path.join(current_dir, "../../../../data/docs/ex_excel/01_case1_단순차트.xlsx")
    output_md = os.path.join(current_dir, "../../../../data/processed/01_case1_단순차트_실패.md")
    
    print(f"🚀 [Excel Fail 01] Naive Pandas Read 시도 중...")
    
    try:
        # 아무런 옵션 없이 읽기
        df = pd.read_excel(input_xlsx)
        
        os.makedirs(os.path.dirname(output_md), exist_ok=True)
        with open(output_md, "w", encoding="utf-8") as f:
            f.write("# [Document Fail] 01_case1_단순차트 - Simple Chart w/o Context\n\n")
            f.write("### ❌ RAG 실패 원인 분석\n")
            f.write("- **증상**: 엑셀 서식 정보 소실 및 시각적 개체(차트) 무시.\n")
            f.write("- **원인**: `pandas.read_excel()`은 데이터 값은 정확히 읽지만, 차트나 이미지가 전달하는 시각적 문맥(Context)을 놓침.\n\n")
            f.write("---\n")
            f.write("### 📄 정제된 텍스트 결과 (Sample)\n")
            f.write(df.head().to_markdown(index=False))
            
        print(f"✅ Excel 실패 결과 생성: {output_md}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
