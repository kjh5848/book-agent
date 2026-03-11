# 📖 Case 01: 기본 읽기 (Basic Read)

## 1. 개요 (Summary)
- **난이도 (Difficulty)**: 하 (Easy)
- **주요 라이브러리 (Key Library)**: `pandas`, `openpyxl`
- **핵심 개념 (Core Concept)**: 엑셀 파일은 `pandas`로 읽는 것이 표준입니다. 데이터가 표(Table) 형태라면 `read_excel()` 한 줄로 끝납니다.

## 2. 케이스 분석 (Case Analysis)

### 🔹 Case 1: 단순 차트 데이터 (Simple Table)
- **입력 (Input)**: `../data/01_case1_단순차트.xlsx`
- **문제 (Problem)**: 가장 기본적인 형태의 엑셀 데이터.
- **해결 (Solution)**: `pd.read_excel()` 함수를 사용하여 DataFrame으로 변환합니다. 첫 번째 시트를 기본으로 읽습니다.
- **핵심 코드 (Key Code)**:
  ```python
  # 1. 파일 읽기 (상위 data 폴더 참조)
  df = pd.read_excel("../data/01_case1_단순차트.xlsx")

  # 2. JSON으로 변환 (활용하기 좋은 포맷)
  df.to_json("../output/result_chart.json", orient="records", force_ascii=False)
  ```

### 🔹 Case 2: 날짜/시간 데이터 (Date Handling)
- **입력 (Input)**: `../data/01_case2_VOC로그.xlsx`
- **문제 (Problem)**: 엑셀의 날짜 포맷이 파이썬에서 `datetime` 객체로 변환되거나, 문자열로 깨질 수 있습니다.
- **해결 (Solution)**: Pandas는 기본적으로 날짜를 잘 인식하지만, 필요하다면 `parse_dates` 파라미터를 사용하거나 읽은 후 `.dt` 접근자로 포맷팅합니다.
- **핵심 코드 (Key Code)**:
  ```python
  df = pd.read_excel("../data/01_case2_VOC로그.xlsx")
  
  # CSV로 저장 시 날짜 포맷 유지 확인
  df.to_csv("../output/result_voc.csv", index=False)
  ```

## 3. RAG 구축 전략 (RAG Strategy)

| 상황 (Context) | 처리 방식 (Method) | 최적 포맷 (Format) | RAG 장점 (Benefit) |
| :--- | :--- | :--- | :--- |
| **정형 데이터 (Table)** | **CSV / Markdown** | **Markdown** | LLM이 표 구조를 '텍스트'로 이해하기 가장 좋음. |
| **계층적 데이터** | **JSON** | **JSON** | `{"Category": "A", "Items": [...]}` 처럼 구조가 명확할 때 유리. |
| **대용량 로그** | **CSV** | **CSV (Snippet)** | 토큰 절약. 전체를 다 넣기보다 필요한 행(Row)만 검색해서 주입. |

> **💡 본 실습의 선택**:
> - **Case 1 (단순 차트) -> Markdown**: 차트의 수치 정보를 LLM이 바로 해석할 수 있도록 표(Table) 형태로 변환.
> - **Case 2 (VOC 로그) -> CSV/Marketing**: 날짜와 고객 반응이 섞인 로그 데이터는 CSV가 검색(Filter)에 유리.
