import pandas as pd
import os

# --- 설정 (Configuration) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
# 참고: 입력 데이터는 한 수준 위의 공유 'data' 폴더에 있습니다.
input_file = os.path.join(current_dir, "../../../../data/docs/ex_excel/", "01_case1_단순차트.xlsx")
output_dir = os.path.join(current_dir, "../../../../data/processed/")

# 출력 디렉토리가 존재하는지 확인
os.makedirs(output_dir, exist_ok=True)

def parse():
    print(f"{input_file} 읽는 중...")
    
    if not os.path.exists(input_file):
        print(f"오류: {input_file} 파일을 찾을 수 없습니다.")
        return

    try:
        # 파일 읽기
        df = pd.read_excel(input_file)
        
        # 마크다운으로 저장
        md_output = os.path.join(output_dir, "01_case1_단순차트_성공.md")
        with open(md_output, "w", encoding="utf-8") as f:
            f.write("# [문서 파싱 성공] 01_case1_단순차트 - 기본 표 추출\n\n")
            f.write("### ✅ RAG 최적화 분석\n")
            f.write("- **전략**: 엑셀의 정형 데이터를 Markdown Table로 변환하여 LLM이 구조를 이해하도록 유도.\n")
            f.write("- **효과**: 불필요한 스타일(색상, 폰트)을 제거하고 순수 '데이터(Data)'만 추출하여 토큰 효율성 극대화.\n\n")
            f.write("---\n")
            f.write("### 📄 정제된 텍스트 결과\n\n")
            f.write(df.to_markdown(index=False))
        print(f"  -> {os.path.basename(md_output)} 에 저장되었습니다.")
        
    except Exception as e:
        print(f"파일 처리 중 오류 발생: {e}")

if __name__ == "__main__":
    parse()
