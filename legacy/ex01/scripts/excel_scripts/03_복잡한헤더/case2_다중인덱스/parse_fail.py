import pandas as pd
import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(current_dir, "../../../../data/docs/ex_excel/", "03_case2_다중인덱스.xlsx")
    output_md = os.path.join(current_dir, "../../../../data/processed/03_case2_다중인덱스_실패.md")
    
    print(f"🚀 [Excel Failure 03-2] 다중 인덱스 행 유실 시물레이션 중...")
    
    try:
        # 인덱스 설정을 무시하고 평범하게 읽기
        df = pd.read_excel(input_file)
        
        os.makedirs(os.path.dirname(output_md), exist_ok=True)
        with open(output_md, "w", encoding="utf-8") as f:
            f.write("# [Document Fail] 03_case2_다중인덱스 - Hierarchy Loss (NaN)\n\n")
            f.write("### ❌ RAG 실패 원인 분석\n")
            f.write("- **증상**: '본부', '팀' 정보가 첫 번째 행에만 나타나고 나머지 행은 공백(NaN)으로 비어 있음.\n")
            f.write("- **원인**: 엑셀의 병합된 셀(Merged Cells)을 파싱할 때, 상위 값을 하위로 전파(Forward Fill)하지 않으면 문맥이 끊김.\n\n")
            f.write("---\n")
            f.write("### 📄 정제된 텍스트 결과 (Sample)\n")
            f.write(df.head(10).to_markdown(index=False))
            
        print(f"✅ Excel 실패 결과 생성: {output_md}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
