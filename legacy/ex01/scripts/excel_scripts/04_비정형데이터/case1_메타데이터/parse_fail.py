import pandas as pd
import os

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_xlsx = os.path.join(current_dir, "../../../../data/docs/ex_excel/04_case1_메타데이터.xlsx")
    output_md = os.path.join(current_dir, "../../../../data/processed/04_case1_메타데이터_실패.md")
    
    print(f"🚀 [Excel Fail 04] 비정형 레이아웃 무시 시도 중...")
    
    try:
        # 비정형 구조(상단 메타데이터 등)를 무시하고 통째로 읽기
        df = pd.read_excel(input_xlsx)
        
        os.makedirs(os.path.dirname(output_md), exist_ok=True)
        with open(output_md, "w", encoding="utf-8") as f:
            f.write("# [Document Fail] 04_case1_좌표추출 - Unstructured Layout\n\n")
            f.write("### ❌ RAG 실패 원인 분석\n")
            f.write("- **증상**: 문서 상단의 '보고서 명', '작성자' 등의 텍스트 정보가 데이터 테이블의 헤더로 잘못 인식됨.\n")
            f.write("- **원인**: 엑셀 제약조건(좌표) 없이 `read_excel`로 통째로 읽으면, 비정형 텍스트와 표 데이터가 뒤섞여(Mixed) 검색 품질이 저하됨.\n\n")
            f.write("---\n")
            f.write("### 📄 정제된 텍스트 결과 (Sample)\n")
            f.write(df.head(10).to_markdown(index=False))
            
        print(f"✅ Excel 실패 결과 생성: {output_md}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
