# 📖 Case 05: 시각적 속성 (Visual Attributes)

## 1. 개요 (Summary)
- **난이도 (Difficulty)**: 중 (Medium)
- **주요 라이브러리 (Key Library)**: `openpyxl`
- **핵심 개념 (Core Concept)**: 텍스트 데이터 값뿐만 아니라, **셀의 배경색(Fill)** 이나 **폰트 스타일(Font)** 과 같은 시각적 정보를 추출하여 정형 데이터로 변환합니다.

## 2. 케이스 분석 (Case Analysis)

### 🔹 Case 1: 색상 기반 분류 (Color Classification)
- **입력 (Input)**: `../data/05_case1_색상분류.xlsx`
- **문제 (Problem)**: 엑셀의 "상태" 컬럼에 텍스트(`위험`, `지연`)가 적혀있지만, 실제 업무에서는 텍스트 없이 **"빨간색 셀은 위험"**이라는 암묵적 규칙만 존재하는 경우가 많습니다. `pandas.read_excel()`은 이 색상 정보를 무시합니다.
- **해결 (Solution)**:
    1. `openpyxl`로 워크북을 엽니다 (Data-only 모드와 Style 접근 모드 고려).
    2. 셀의 `fill.start_color.index` 속성을 조회하여 ARGB 색상 코드를 얻습니다.
    3. 색상 코드(`FFFF0000`)를 의미 있는 텍스트(`Critical`)로 매핑하여 새로운 컬럼(`visual_flag`)을 생성합니다.
- **핵심 코드 (Key Code)**:
  ```python
  from openpyxl import load_workbook
  
  # openpyxl로 직접 로드
  wb = load_workbook(input_file)
  ws = wb.active
  
  for row in ws.iter_rows(min_row=2):
      status_cell = row[4] # E열
      color_code = status_cell.fill.start_color.index # FFFF0000 etc.
      
      if color_code == "FFFF0000":
          visual_status = "Critical (위험)"
      elif color_code == "FFFFFF00":
          visual_status = "Warning (지연)"
      else:
          visual_status = "Normal"
  ```

## 3. RAG 구축 전략 (RAG Strategy)

| 상황 (Context) | 처리 방식 (Method) | 최적 포맷 (Format) | RAG 장점 (Benefit) |
| :--- | :--- | :--- | :--- |
| **색상으로 상태 표현** | **Visual to Text** | **JSON** | "빨간색 셀"을 "위험(Critical)"이란 단어로 변환하여 검색 가능하게 만듦. |
| **취소선(Strikethrough)** | **Filtered Extraction** | **CSV** | 취소선은 "삭제된 데이터"를 의미하므로, 추출 시 제외하거나 "Deleted" 플래그 추가. |
| **굵은 글씨(Bold)** | **Tagging** | **Markdown** | `**강조된 내용**`으로 변환하여 LLM에게 중요도를 전달. |

> **💡 본 실습의 선택**:
> - **Case 1 -> JSON**: 시각적 속성(`visual_flag`)은 원본 데이터(`status_text`)와 함께 묶여야 문맥이 완성되므로, 객체 단위로 저장하는 JSON이 적합합니다. RAG 시스템은 이제 "빨간색으로 표시된 위험 프로젝트가 뭐야?"라는 질문에 답할 수 있습니다.

## 4. RAG 비교 분석 (Success vs Fail)

| 구분 | 파일 | 포맷 (Format) | RAG 처리 결과 (예시) |
| :--- | :--- | :--- | :--- |
| **성공 (Success)** | `05_case1_색상분류_성공.md` | Markdown | `# [Document Success] ... - Color to Text` <br> -> **"빨간색 셀은 위험, 노란색은 지연 상태입니다."**라고 정확히 답변 가능. |
| **실패 (Fail)** | `05_case1_색상분류_실패.md` | Markdown | `| ID | ... | 상태 |`<br>`| 1 | ... | 위험 |` <br> -> 색상 정보가 없어서 **"어떤 게 위험한 건지 색깔로는 알 수 없습니다."**라고 답변함. |
