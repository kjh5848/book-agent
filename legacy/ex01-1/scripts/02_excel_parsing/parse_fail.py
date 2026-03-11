"""
[실패 사례 - 단순 엑셀 Pandas 파싱]
복잡한 병합 셀(Merge Cell)이 있는 엑셀 문서를 단일 헤더로 읽었을 때 발생하는 데이터 오염 현상을 보여줍니다.
"""
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, '../../data/docs/fin/FIN_매출현황_v1.0.xlsx')
OUTPUT_FILE = os.path.join(BASE_DIR, '../../parsed_data/fail_results/02_FIN_매출현황_fail.md')

def parse_excel_naive(xlsx_path, md_path):
    print(f"📊 단순 Pandas 엑셀 파싱 시작: {os.path.basename(xlsx_path)}")
    os.makedirs(os.path.dirname(md_path), exist_ok=True)
    
    # [실패 원인] 병합된 표를 단순하게 읽으면 'Unnamed: X' 컬럼이 생기고 값들은 NaN으로 도배됩니다.
    # 실무 문서 상단의 '결재란', '작성일자' 등의 메타데이터로 인해 진짜 표의 헤더를 찾지 못합니다.
    df = pd.read_excel(xlsx_path)
    
    md_content = f"# 매출현황 (단순 파싱 실패 사례)\n\n"
    md_content += df.to_markdown()
    md_content += "\n"
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"❌ 단순 변환 완료 (NaN 발생, 구조 붕괴): {os.path.basename(md_path)}")

if __name__ == "__main__":
    parse_excel_naive(INPUT_FILE, OUTPUT_FILE)
