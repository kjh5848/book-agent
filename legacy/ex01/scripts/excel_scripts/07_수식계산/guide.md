# 📖 Case 07: 수식 및 참조 (Formula Evaluation)

## 1. 개요 (Summary)
- **난이도 (Difficulty)**: 중 (Medium)
- **주요 라이브러리 (Key Library)**: `openpyxl` (via `pandas` engine)
- **핵심 개념 (Core Concept)**: 엑셀 셀에 저장된 데이터는 두 가지 형태(수식 문자열 vs 계산된 값)로 존재합니다. RAG는 **"계산된 최종 값(Evaluated Value)"**이 필요하므로, 로드 시 옵션을 정확히 지정해야 합니다.

## 2. 케이스 분석 (Case Analysis)

### 🔹 Case 1: 수식 계산 (Formula Evaluation)
- **입력 (Input)**: `../data/07_case1_수식계산.xlsx`
- **문제 (Problem)**: 엑셀 파일에 `=A1*B1` 같은 수식이 들어있을 때, 기본적으로 라이브러리는 수식 문자열 자체를 읽어옵니다. LLM에게 "가격이 얼마야?"라고 물었는데 `"=B2*C2"`라고 답하면 곤란합니다.
- **해결 (Solution)**:
    1. `openpyxl.load_workbook(..., data_only=True)` 옵션을 사용합니다.
    2. 이 옵션은 엑셀 파일 내부의 XML 캐시(Cache)에 저장된 **계산 결과값**을 불러옵니다.
    3. `pandas.read_excel()`은 기본적으로 값을 읽어오려고 시도하지만, 엔진 설정에 따라 수식을 읽을 수도 있습니다. 확실하게 하기 위해 엔진 옵션을 확인하세요.
- **핵심 코드 (Key Code)**:
  ```python
  from openpyxl import load_workbook
  
  # data_only=True: 수식(=SUM) 대신 계산된 값(100)을 읽음
  wb = load_workbook(input_file, data_only=True)
  ws = wb.active
  value = ws['D2'].value 
  ```

## 3. RAG 구축 전략 (RAG Strategy)

| 상황 (Context) | 처리 방식 (Method) | 최적 포맷 (Format) | RAG 장점 (Benefit) |
| :--- | :--- | :--- | :--- |
| **최종 값 필요** | **Value Evaluation** | **Markdown** | 사용자는 "결과"를 묻지 "공식"을 묻지 않음. 깔끔한 표 형태로 값만 전달. |
| **검증(Audit) 필요** | **Formula & Value** | **JSON** | `{ "Formula": "=A+B", "Value": 10 }` 형태로 저장하여 계산 근거 확보. |
| **대량 데이터** | **Batch Process** | **CSV** | 수식 계산 후 값만 빠르게 CSV로덤프. |

> **💡 본 실습의 선택**:
> - **Case 1 -> Markdown**: 수식을 계산한 **최종 결과값(Value)** 만을 Markdown 표로 변환하여, LLM이 "A제품의 총액은 얼마인가?"에 대해 즉답할 수 있도록 합니다.

## 4. RAG 비교 분석 (Success vs Fail)

| 구분 | 파일 | 포맷 (Format) | RAG 처리 결과 (예시) |
| :--- | :--- | :--- | :--- |
| **성공 (Success)** | `07_case1_수식계산_성공.md` | Markdown | `| 품목 | 단가 | 수량 | 총액 |` <br> -> **"총액은 6,600,000원입니다."**라고 정확히 답변. |
| **실패 (Fail)** | `07_case1_수식계산_실패.md` | CSV/MD | `..., =D2+E2` <br> -> **"총액은 D2 더하기 E2입니다."**라는 쓸모없는 답변을 내놓음. |

