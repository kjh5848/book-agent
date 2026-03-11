# 📖 Case 02: 다중 시트 (Multiple Sheets)

## 1. 개요 (Summary)
- **난이도 (Difficulty)**: 하 (Easy)
- **주요 라이브러리 (Key Library)**: `pandas`
- **핵심 개념 (Core Concept)**: 엑셀 파일 하나에 여러 개의 시트가 있을 때, 특정 시트만 골라 읽거나 전체를 순회(Iteration)하며 읽어야 합니다.

## 2. 케이스 분석 (Case Analysis)

### 🔹 Case 1: 시트 필터링 (Sheet Filtering)
- **입력 (Input)**: `../data/02_case1_시트필터.xlsx`
- **문제 (Problem)**: 시트 목록 중 불필요한 시트(`Sheet1` 등)가 섞여 있고, 필요한 시트(`고객정보`, `주문내역`)만 읽어야 함.
- **해결 (Solution)**: `pd.ExcelFile()` 객체로 시트 목록(`sheet_names`)을 먼저 확인한 후, 조건문으로 필터링하여 읽습니다.
- **핵심 코드 (Key Code)**:
  ```python
  xls = pd.ExcelFile("../data/02_case1_시트필터.xlsx")
  
  data = {}
  for sheet_name in xls.sheet_names:
      if "Sheet" in sheet_name:
          continue
      data[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
  ```

### 🔹 Case 2: 일괄 처리 (Batch Processing)
- **입력 (Input)**: `../data/02_case2_일괄처리.xlsx`
- **문제 (Problem)**: 시트 이름을 모르거나, 개수가 많아서 일일이 지정하기 힘들 때.
- **해결 (Solution)**: `sheet_name=None` 옵션을 주면, 모든 시트를 {시트명: DataFrame} 형태의 딕셔너리로 한 번에 반환합니다.
- **핵심 코드 (Key Code)**:
  ```python
  # sheet_name=None -> 모든 시트 읽기
  all_sheets = pd.read_excel("../data/02_case2_일괄처리.xlsx", sheet_name=None)
  
  for name, df in all_sheets.items():
      df.to_csv(f"../output/02_case2_일괄처리_{name}_성공.csv", index=False)
  ```

## 3. RAG 구축 전략 (RAG Strategy)

| 상황 (Context) | 처리 방식 (Method) | 최적 포맷 (Format) | RAG 장점 (Benefit) |
| :--- | :--- | :--- | :--- |
| **특정 시트만 필요** | **Filtering** | **JSON** | 불필요한 시트(백업용, 임시데이터)를 제거하여 검색 품질 향상. |
| **모든 시트가 독립적** | **Splitting** | **Multi-CSV/MD** | 각 시트를 개별 문서로 취급하여 검색 단위(Chunk) 최적화. |
| **시트 간 관계 중요** | **Merging** | **Single-MD** | "A시트의 고객 ID가 B시트의 주문 ID와 연결됨"을 한 문맥에서 파악 가능. |

> **💡 본 실습의 선택**:
> - **Case 1 -> JSON**: 필터링된 결과는 구조가 단순하므로 JSON으로 저장하여 메타정보(시트명 등)를 함께 담습니다.
> - **Case 2 -> CSV**: 각 시트가 독립적인 데이터셋(예: 월별 매출)이라면, 별도 CSV 파일로 저장하여 관리하는 것이 좋습니다.

## 4. RAG 비교 분석 (Success vs Fail)

| 구분 | 파일 | 포맷 (Format) | RAG 처리 결과 (예시) |
| :--- | :--- | :--- | :--- |
| **성공 (Success)** | `filtered_sheets.json` | JSON (Multi-sheet) | `{ "Sheet1": [...], "Sheet2": [...] }` <br> -> **"전체 시트의 내용을 모두 검색할 수 있습니다."** |
| **실패 (Fail)** | `02_case1_전체통합_실패.md` | CSV (Single-sheet) | `Sheet1 Data...` <br> -> **"Sheet2에 있는 내용은 찾을 수 없습니다."**라고 답변. |
