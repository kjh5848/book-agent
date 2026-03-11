import pandas as pd
import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(current_dir, "../../../../data/docs/ex_excel/", "02_case2_일괄처리.xlsx")
    output_md = os.path.join(current_dir, "../../../../data/processed/02_case2_일괄처리_실패.md")
    
    print(f"🚀 [Excel Failure 02-2] 일괄 처리 누락 시물레이션 중...")
    
    try:
        # 모든 시트가 아닌 첫 번째 시트만 읽기 (기본값의 함정)
        df = pd.read_excel(input_file)
        
        os.makedirs(os.path.dirname(output_md), exist_ok=True)
        with open(output_md, "w", encoding="utf-8") as f:
            f.write("# [Failure] 02_case2_일괄처리 - 전체 시트 중 일부만 로드됨\n\n")
            f.write("### 🚨 상황 분석\n")
            f.write("- **증상**: 12개월분 매출 시트가 있음에도 불구하고, 1월 시트 데이터만 추출됨.\n")
            f.write("- **원인**: `pd.read_excel()` 호출 시 `sheet_name=None` 옵션을 주지 않아 기본값인 0번 시트만 처리됨.\n\n")
            f.write("--- \n")
            f.write("### 📄 추출된 데이터 샘플 (첫 시트만 반영)\n")
            f.write(df.head().to_markdown())
            f.write("\n\n> **Mentor's Note**: '일괄 처리'라는 목표를 잊고 습관적으로 함수를 호출하면 이런 결과가 나옵니다. 데이터가 12배 적게 들어간 RAG 시스템이 제대로 된 연간 분석을 할 수 있을까요? 절대 불가능합니다.")
            
        print(f"✅ Excel 실패 결과 생성: {output_md}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
