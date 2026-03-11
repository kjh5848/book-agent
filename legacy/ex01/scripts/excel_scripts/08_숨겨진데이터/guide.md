# 📖 Case 08: 숨겨진 데이터 (Hidden Data)

## 1. 개요 (Summary)
- **난이도 (Difficulty)**: 하 (Easy)
- **주요 라이브러리 (Key Library)**: `openpyxl`
- **핵심 개념 (Core Concept)**: 엑셀의 "숨기기(Hide)" 기능은 시각적으로만 가릴 뿐, 데이터 자체는 파일에 남아있습니다. `pandas`는 이를 구분하지 않고 모두 읽어오므로, **명시적으로 숨김 속성을 확인하여 제외**해야 합니다.

## 2. 케이스 분석 (Case Analysis)

### 🔹 Case 1: 숨겨진 행 제외 (Filtering Hidden Rows)
- **입력 (Input)**: `../data/08_case1_숨겨진행.xlsx`
- **문제 (Problem)**: 사용자가 "구형 스마트폰" 데이터를 삭제하지 않고 **행 숨김** 처리만 해둠. RAG 시스템이 이를 읽으면 **"폐기된 제품"을 "판매중"인 것으로 착각**하여 답변할 수 있습니다.
- **해결 (Solution)**:
    1. `openpyxl`로 시트의 행(Row)을 순회합니다.
    2. `ws.row_dimensions[row.row].hidden` 속성이 `True`인지 확인합니다.
    3. 숨겨진 행이면 건너뛰고(continue), 보이는 행만 리스트에 담아 DataFrame으로 만듭니다.
- **핵심 코드 (Key Code)**:
  ```python
  from openpyxl import load_workbook
  
  wb = load_workbook(input_file)
  ws = wb.active
  
  data = []
  for row in ws.iter_rows(min_row=2):
      # 숨김 여부 체크
      if ws.row_dimensions[row[0].row].hidden:
          continue # 스킵
      
      # 데이터 추출
      data.append([cell.value for cell in row])
  ```

## 3. RAG 구축 전략 (RAG Strategy)

| 상황 (Context) | 처리 방식 (Method) | 최적 포맷 (Format) | RAG 장점 (Benefit) |
| :--- | :--- | :--- | :--- |
| **유효 데이터만 필요** | **Hidden Row Filter** | **Markdown** | 숨겨진(폐기된) 데이터가 검색되지 않도록 원천 차단하여 답변의 신뢰성 확보. |
| **이력 관리 필요** | **Tagging** | **JSON** | `{ "Status": "Hidden", "Data": ... }` 로 저장하여, "삭제된 데이터 내역"을 질문할 때 활용. |
| **단순 리스트** | **Clean Export** | **CSV** | 군더더기 없는 깔끔한 데이터셋 생성. |

> **💡 본 실습의 선택**:
> - **Case 1 -> Markdown**: 사용자에게 보여지는 "유효한(Visible)" 데이터만 남겨 Markdown 표로 변환합니다. RAG는 이제 "숨겨진 데이터"에 대해 아예 모르게 되므로, 환각(Hallucination)없이 정확한 정보만 제공합니다.

## 4. RAG 비교 분석 (Success vs Fail)

| 구분 | 파일 | 포맷 (Format) | RAG 처리 결과 (예시) |
| :--- | :--- | :--- | :--- |
| **성공 (Success)** | `08_case1_숨겨진행_성공.md` | Markdown | `| P101 | P102 |` <br> -> **"현재 판매중인 제품은 P101, P102입니다."** (정답) |
| **실패 (Fail)** | `08_case1_숨겨진행_실패.md` | CSV/MD | `| P101 | P099(폐기) |` <br> -> **"폐기된 P099 제품도 판매중입니다."**라고 잘못 안내하여 고객 클레임 유발. |

