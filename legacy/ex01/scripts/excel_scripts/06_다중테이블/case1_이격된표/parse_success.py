import pandas as pd
import os

# 파일 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(current_dir, "../../../../data/docs/ex_excel/", "06_case1_이격된표.xlsx")
output_dir = os.path.join(current_dir, "../../../../data/processed/")
os.makedirs(output_dir, exist_ok=True)

print(f"Reading {input_file}...")

# 1. 엑셀 전체를 Raw 데이터로 읽기 (헤더 없이)
# 중간의 빈 행(NaN)을 포함하여 전체 구조를 파악해야 함
df_raw = pd.read_excel(input_file, header=None)

# 2. 데이터가 있는 행(Row)만 찾아서 클러스터링 (테이블 분리)
# 행의 모든 값이 NaN인 경우를 기준으로 데이터를 나눔
valid_rows = df_raw.dropna(how='all').index.tolist()

clusters = []
if not valid_rows:
    print("No data found.")
else:
    # 연속된 행 인덱스를 그룹화
    current_cluster = [valid_rows[0]]
    for i in range(1, len(valid_rows)):
        if valid_rows[i] == valid_rows[i-1] + 1:
            current_cluster.append(valid_rows[i])
        else:
            clusters.append(current_cluster)
            current_cluster = [valid_rows[i]]
    clusters.append(current_cluster)

print(f"Detected {len(clusters)} table clusters.")

# 3. 각 클러스터별로 데이터프레임 생성 및 저장
table_names = ["매출현황", "재고현황"]  # 예시: 순서대로 이름 부여

for i, cluster in enumerate(clusters):
    start_row = cluster[0]
    end_row = cluster[-1]
    
    # 해당 범위의 데이터 슬라이싱
    # 첫 행은 제목/헤더일 가능성이 높음. 
    # 여기서는 간단히: 첫 행=[표 제목], 두번째 행=헤더, 그 이후=데이터라고 가정하거나
    # 데이터 내용(헤더 탐지) 로직을 추가할 수 있음.
    
    # 이 예제에서는:
    # Cluster 0: [표 1] (row 0), 헤더 (row 1), 데이터 (row 2-4)
    # Cluster 1: [표 2] (row 8), 헤더 (row 9), 데이터 (row 10-13)
    
    # 제목(Title) 추출 (첫 번째 행)
    table_title = df_raw.iloc[start_row, 0]
    if isinstance(table_title, str) and table_title.startswith("[표"):
        # 제목 행 제외하고, 그 다음 행을 헤더로 사용
        header_row_idx = start_row + 1
        data_start_idx = start_row + 2
    else:
        # 제목이 없으면 첫 행이 헤더
        header_row_idx = start_row
        data_start_idx = start_row + 1
        table_title = f"Table_{i+1}"

    # 서브 데이터프레임 생성
    table_df = df_raw.iloc[data_start_idx : end_row + 1].copy()
    table_df.columns = df_raw.iloc[header_row_idx]
    
    # 저장
    # 파일명에 한글 식별자 포함
    suffix = table_names[i] if i < len(table_names) else f"Table_{i+1}"
    output_filename = f"06_case1_이격된표_{suffix}_성공.csv"
    output_path = os.path.join(output_dir, output_filename)
    
    table_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"  -> Extracted '{table_title}' to {output_filename}")
    print(table_df.head(2))
    print("-" * 30)
