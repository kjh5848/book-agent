# 📖 Case 06: 다중 테이블 (Multiple Tables)

## 1. 개요 (Summary)
- **난이도 (Difficulty)**: 상 (Hard)
- **주요 라이브러리 (Key Library)**: `pandas`
- **핵심 개념 (Core Concept)**: 하나의 시트 안에 물리적으로 떨어진 여러 개의 표가 존재할 때, **빈 행(NaN)을 기준으로 클러스터링(Clustering)** 하여 개별 표로 분리합니다.

## 2. 케이스 분석 (Case Analysis)

### 🔹 Case 1: 이격된 표 분리 (Table Splitting)
- **입력 (Input)**: `../data/06_case1_이격된표.xlsx`
- **문제 (Problem)**: 시트 상단에는 `1월 매출 현황`, 하단에는 `현재 재고 현황`이 있습니다. 이를 `read_excel()`로 한 번에 읽으면, 서로 다른 헤더와 빈 공간(NaN)이 뒤섞여서 **사용 불가능한 데이터프레임**이 됩니다.
- **해결 (Solution)**:
    1. `header=None`으로 전체를 Raw 데이터로 읽습니다.
    2. 데이터가 존재하는 행(Valid Rows)의 인덱스를 찾습니다.
    3. 연속된 인덱스끼리 그룹화(Clustering)하여 표의 **시작 행과 끝 행**을 감지합니다.
    4. 각 그룹(Cluster)을 슬라이싱(`iloc`)하여 개별 CSV로 저장합니다.
- **핵심 코드 (Key Code)**:
  ```python
  # 1. 전체 데이터 로드
  df_raw = pd.read_excel(input_file, header=None)
  
  # 2. 데이터가 있는 행만 추출하여 클러스터링
  valid_rows = df_raw.dropna(how='all').index.tolist()
  clusters = [[...], [...]] # 예: [0~4행], [8~13행]
  
  # 3. 클러스터별 분리 저장
  for cluster in clusters:
      sub_df = df_raw.iloc[cluster[0]:cluster[-1]+1]
      sub_df.to_csv(f"../output/06_case1_이격된표_{name}_성공.csv")
  ```

## 3. RAG 구축 전략 (RAG Strategy)

| 상황 (Context) | 처리 방식 (Method) | 최적 포맷 (Format) | RAG 장점 (Benefit) |
| :--- | :--- | :--- | :--- |
| **표가 서로 독립적** | **Clustering & Split** | **CSV** | 각 표를 개별 파일로 분리하여 검색 정확도를 높임. |
| **표 간 연관성 높음** | **Merge & ID** | **JSON** | `{ "Sales": [...], "Inventory": [...] }` 구조로 묶어서 관계 유지. |
| **설명이 포함된 보고서** | **Markdown** | **Markdown** | 텍스트 설명과 함께 표를 배치하여 문맥 흐름 보존. |

> **💡 본 실습의 선택**:
> - **Case 1 -> CSV (Split)**: 두 표(`매출`, `재고`)는 성격이 다른 독립적인 데이터입니다. 이를 하나의 거대한 표나 문서로 묶는 것보다, **개별 CSV 파일로 쪼개어(Chunking)** 저장하는 것이 RAG 검색 효율성 면에서 훨씬 유리합니다.

## 4. RAG 비교 분석 (Success vs Fail)

| 구분 | 파일 | 포맷 (Format) | RAG 처리 결과 (예시) |
| :--- | :--- | :--- | :--- |
| **성공 (Success)** | `06_case1_이격된표_매출현황_성공.csv` | CSV (Separated) | `| 제품명 | 매출액 |` <br> -> **"매출 표에서 '노트북' 찾아줘"**라고 하면 정확히 해당 CSV만 검색됨. |
| **실패 (Fail)** | `06_case1_이격된표_실패.md` | CSV (Mixed) | `[표 1]`, `NaN`, `NaN`, `[표 2]` <br> -> 위아래 표가 섞여서 **"이게 매출인지 재고인지 컬럼이 뒤섞여 알 수 없습니다."** 현상 발생. |

