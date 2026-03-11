# 📖 Case 03: 복잡한 헤더 (Complex Header)

## 1. 개요 (Summary)
- **난이도 (Difficulty)**: 중 (Medium)
- **주요 라이브러리 (Key Library)**: `pandas`
- **핵심 개념 (Core Concept)**: 엑셀의 "병합된 셀(Merged Cells)"은 데이터 분석의 주적입니다. Pandas의 `header`와 `index_col` 옵션으로 이를 구조화된 데이터로 풀어내야 합니다.

## 2. 케이스 분석 (Case Analysis)

### 🔹 Case 1: 병합된 헤더 (Merged Header)
- **입력 (Input)**: `../data/03_case1_병합헤더.xlsx`
- **문제 (Problem)**: 헤더가 두 줄 이상으로 되어 있고, 상위 헤더가 셀 병합되어 있음 (예: 2024년 -> 1월, 2월). 기본 호출 시 `Unnamed: 1` 같은 컬럼이 생김.
- **해결 (Solution)**: `header=[0, 1]`과 같이 리스트로 전달하여 **다중 인덱스(MultiIndex)** 컬럼으로 읽습니다.
- **핵심 코드 (Key Code)**:
  ```python
  # 상위 2줄을 헤더로 인식
  df = pd.read_excel("../data/03_case1_병합헤더.xlsx", header=[0, 1])
  
  # 레벨별 접근 가능
  # print(df['2024년']['1월'])
  ```

### 🔹 Case 2: 다중 인덱스 (Multi-Index Row)
- **입력 (Input)**: `../data/03_case2_다중인덱스.xlsx`
- **문제 (Problem)**: 행(Row) 쪽에도 병합된 셀이 있어, 계층 구조를 가짐 (예: 부서 -> 팀).
- **해결 (Solution)**: `index_col=[0, 1]`을 사용하여 앞쪽 컬럼들을 인덱스로 고정시킵니다. 그러면 Pandas가 병합된 빈 셀을 자동으로 앞의 값으로 채워주는 효과(ffill)를 내거나 계층적으로 다룹니다.
- **핵심 코드 (Key Code)**:
  ```python
  # 0, 1번 컬럼을 행 인덱스로 설정
  df = pd.read_excel("../data/03_case2_다중인덱스.xlsx", index_col=[0, 1])
  
  # CSV로 저장 (MultiIndex 평탄화 적용됨)
  df.to_csv("../output/03_case2_다중인덱스_성공.csv", index=False, encoding="utf-8-sig")
  ```

## 3. RAG 구축 전략 (RAG Strategy)

| 상황 (Context) | 처리 방식 (Method) | 최적 포맷 (Format) | RAG 장점 (Benefit) |
| :--- | :--- | :--- | :--- |
| **병합 헤더 (2-Level)** | **Flattening** | **CSV** | `2024년_1월_매출` 처럼 컬럼명을 합치면 검색 정확도 상승. |
| **계층적 분류 (Tree)** | **Hierarchical** | **JSON/Markdown** | 상위 카테고리(부서)와 하위 항목(팀)의 포함 관계를 명시. |
| **반복된 병합 셀** | **Forward Fill** | **CSV/Markdown** | "영업팀"이 빈 칸으로 병합된 경우, 모든 행에 "영업팀"을 채워넣어 검색 누락 방지. |

> **💡 본 실습의 선택**:
> - **Case 1 -> CSV**: 계층적 헤더가 플랫(Flat)하게 정리되어 RAG 검색에 용이합니다.
> - **Case 2 -> CSV**: 다중 인덱스도 유사하게 처리하여 복잡도를 낮춥니다.

## 4. RAG 비교 분석 (Success vs Fail)

| 구분 | 파일 | 포맷 (Format) | RAG 처리 결과 (예시) |
| :--- | :--- | :--- | :--- |
| **성공 (Success)** | `result.csv` | CSV (Flattened) | `| 1월_매출 | 1월_이익 |` <br> -> **"1월 이익은?"**이라고 물으면 정확한 컬럼 매칭 가능. |
| **실패 (Fail)** | `03_case1_병합헤더_실패.md` | CSV (Broken) | `| Unnamed: 1 | 1월 |` <br> -> **"Unnamed: 1 컬럼이 무엇을 의미하는지 알 수 없습니다."** |
