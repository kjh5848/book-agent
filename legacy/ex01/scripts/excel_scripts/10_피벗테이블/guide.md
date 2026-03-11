# 📖 Case 10: 피벗 테이블 / 병합된 셀 (Pivot Tables & Merged Cells)

## 1. 개요 (Summary)
- **난이도 (Difficulty)**: 중 (Medium)
- **주요 라이브러리 (Key Library)**: `pandas`
- **핵심 개념 (Core Concept)**: 엑셀의 보고서(Report) 양식은 가독성을 위해 **셀 병합(Merge)** 을 자주 사용합니다. 이를 RAG용 데이터로 변환하려면 합쳐진 셀의 값을 아래쪽 빈 셀들로 **전파(Fill Down / Forward Fill)** 하여 정규화(Normalization)해야 합니다.

## 2. 케이스 분석 (Case Analysis)

### 🔹 Case 1: 피벗 해제 및 데이터 채우기 (Unpivot & Forward Fill)
- **입력 (Input)**: `../data/10_case1_피벗해제.xlsx`
- **문제 (Problem)**: "2024년" 밑에 "1분기", "2분기"가 있고, 그 옆에 "A팀", "B팀"이 있습니다. "2024년"은 첫 번째 셀에만 적혀있고 나머지는 병합되어 비어있습니다(NaN). RAG가 3번째 행을 읽을 때 "연도" 정보가 없으면 답변할 수 없습니다.
- **해결 (Solution)**:
    1. 데이터프레임으로 읽으면 병합된 셀의 첫 번째 칸만 값이 있고 나머지는 `NaN`이 됩니다.
    2. `ffill()`(Forward Fill) 메서드를 사용하여 위쪽의 유효한 값을 아래쪽 `NaN`으로 복사합니다.
    3. 이렇게 하면 모든 행이 "2024년", "1분기" 등의 완전한 문맥(Context)을 갖게 됩니다.
- **핵심 코드 (Key Code)**:
  ```python
  df = pd.read_excel(input_file)
  
  # ['연도', '분기'] 컬럼의 NaN을 위의 값으로 채움
  cols_to_fill = ["연도", "분기"]
  df[cols_to_fill] = df[cols_to_fill].ffill()
  
  # 이제 모든 행이 독립적인 레코드가 됨
  ```

## 3. RAG 구축 전략 (RAG Strategy)

| 상황 (Context) | 처리 방식 (Method) | 최적 포맷 (Format) | RAG 장점 (Benefit) |
| :--- | :--- | :--- | :--- |
| **계층형 데이터** | **Forward Fill** | **Markdown** | 병합된 셀을 해제하고 값을 채워, 모든 행이 독립적인 의미를 갖도록 정규화. |
| **복잡한 집계** | **Pivot/Melt** | **CSV** | 데이터베이스(DB)화 하기 좋은 형태(Long Format)로 변환하여 분석 용이성 확보. |
| **대시보드형** | **Summary Only** | **Text** | 세부 데이터 대신 "합계 100억" 같은 요약 정보만 텍스트로 추출. |

> **💡 본 실습의 선택**:
> - **Case 1 -> Markdown**: `ffill`로 데이터가 채워지면 완벽한 2차원 테이블이 되므로, Markdown 표 형식이 RAG에게 가장 직관적인 구조(Structure)를 제공합니다.

## 4. RAG 비교 분석 (Success vs Fail)

| 구분 | 파일 | 포맷 (Format) | RAG 처리 결과 (예시) |
| :--- | :--- | :--- | :--- |
| **성공 (Success)** | `10_case1_피벗해제_성공.md` | Markdown | `| 2024년 | 2분기 | B팀 |` <br> -> **"2024년 2분기 B팀 실적은?"** 질문에 정확히 답변. |
| **실패 (Fail)** | `10_case1_피벗해제_실패.md` | CSV/MD (NaN) | `| NaN | NaN | B팀 |` <br> -> 연도 정보가 비어있어서 **"이게 2023년 실적입니까 2024년입니까?"**라고 되묻거나 엉뚱한 연도와 오해함. |

