import pandas as pd
import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_xlsx = os.path.join(current_dir, "../../../../data/docs/ex_excel/01_case2_VOC로그.xlsx")
    output_md = os.path.join(current_dir, "../../../../data/processed/01_case2_VOC로그_실패.md")
    
    print(f"🚀 [Excel Failure 01-2] 날짜 포맷 깨짐 현상 시물레이션 중...")
    
    try:
        # 날짜 타입 변환 없이 단순히 읽기
        df = pd.read_excel(input_xlsx)
        
        os.makedirs(os.path.dirname(output_md), exist_ok=True)
        with open(output_md, "w", encoding="utf-8") as f:
            f.write("# [Document Fail] 01_case2_VOC로그 - Date Format Mismatch\n\n")
            f.write("### ❌ RAG 실패 원인 분석\n")
            f.write("- **증상**: 엑셀의 날짜 형식이 파이썬 `datetime` 객체로 넘어오며 ISO 포맷(T00:00:00) 등으로 자동 변환됨.\n")
            f.write("- **원인**: 명시적인 문자열 포맷팅이 없어, 사용자가 \"2023년 5월\"과 같이 자연어 질의 시 정확한 매칭이 어려움.\n\n")
            f.write("---\n")
            f.write("### 📄 정제된 텍스트 결과 (Sample)\n")
            # 강제로 문자열로 보여줌 (변환 전 상태 시연)
            f.write(df.head().astype(str).to_markdown(index=False))
            
        print(f"✅ Excel 실패 결과 생성: {output_md}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
