# 📖 Case 04: 비정형 데이터 (Unstructured Data)

## 1. 개요 (Summary)
- **난이도 (Difficulty)**: 상 (Hard)
- **주요 라이브러리 (Key Library)**: `pandas` (iloc), `openpyxl`
- **핵심 개념 (Core Concept)**: 엑셀이 "표"가 아니라 "문서"로 쓰인 경우입니다. (예: 결재 서류, 회의록). 셀 좌표(좌표 기반 추출)를 이용해 메타데이터와 본문을 분리해야 합니다.

## 2. 케이스 분석 (Case Analysis)

### 🔹 Case 1: 메타데이터 추출 (Metadata Extraction)
- **입력 (Input)**: `../data/04_case1_메타데이터.xlsx`
- **문제 (Problem)**: 첫 5줄은 제목, 작성일, 참석자 등의 정보가 있고, 실제 표는 6번째 줄부터 시작됨. `read_excel()`로 그냥 읽으면 엉망이 됨.
- **해결 (Solution)**:
    1. `header=None`으로 전체를 읽습니다.
    2. `.iloc[row, col]`를 사용하여 고정된 위치의 메타데이터(제목 등)를 뽑아냅니다.
    3. 실제 표가 시작되는 위치(예: 5행)부터 다시 슬라이싱(`df.iloc[5:]`)하여 테이블로 만듭니다.
- **핵심 코드 (Key Code)**:
  ```python
  df = pd.read_excel("../data/04_case1_메타데이터.xlsx", header=None)
  
  # 1. 메타데이터 (고정 위치)
  title = df.iloc[0, 0]  # A1 셀
  date = df.iloc[1, 1]   # B2 셀
  
  # 2. 본문 테이블 (5번째 줄부터)
  table_df = df.iloc[5:].copy()
  table_df.columns = df.iloc[4]  # 4번째 줄을 헤더로 설정
  ```

## 3. RAG 구축 전략 (RAG Strategy)

| 상황 (Context) | 처리 방식 (Method) | 최적 포맷 (Format) | RAG 장점 (Benefit) |
| :--- | :--- | :--- | :--- |
| **문서형 엑셀 (Form)** | **Coordinate Extraction** | **Markdown** | 결재란, 제목, 본문을 분리하여 문서의 맥락(Context)을 재구성. |
| **헤더 위치 불명** | **Keyword Search** | **Dynamic Slicing** | "품목명" 같은 키워드를 찾아 그 아래부터 표(Table)로 인식. |
| **복합 데이터** | **Json + Table** | **JSON** | `{ "Meta": {...}, "Data": [...] }` 형태로 구조화하여 검색. |

> **💡 본 실습의 선택**:
> - **Case 1 -> Markdown (with Meta)**: 메타데이터(`작성일`, `참석자`)를 헤더로 명시하고, 본문은 표로 변환하여 LLM이 "누가 언제 작성한 회의록인가?"를 이해하도록 함.

## 4. RAG 비교 분석 (Success vs Fail)

| 구분 | 파일 | 포맷 (Format) | RAG 처리 결과 (예시) |
| :--- | :--- | :--- | :--- |
| **성공 (Success)** | `result_content.md` | Markdown (Structured) | `# 회의록 (2024-01-01)` <br> -> **"1월 1일 회의 안건은?"** 질문에 답변 가능. |
| **실패 (Fail)** | `04_case1_메타데이터_실패.md` | CSV (Mixed) | `| 결재 | 담당 |` <br> -> 표의 헤더가 '결재'가 되어버려 **"품목 데이터가 어디 있는지 찾을 수 없습니다."** |
