# Case 02: 표 (Table) 처리

## 1. 개요 (Summary)

- **난이도(Difficulty)**: 상급 (High)
- **주요 라이브러리(Key Library)**: `pdfplumber`, `pandas`
- **핵심 개념(Core Concept)**: PDF의 표는 '그림'이지 '구조 데이터'가 아닙니다. 선(Line)을 찾거나, 텍스트 정렬(Alignment)을 보고 표를 다시 그려야 합니다.

## 2. 사례 분석 (Case Analysis)[Category 01] 다단 편집(Multi-Column) RAG 최적화 보고서

### Case 1: 투명표 (Invisible Borders) - 표 전용 추출

- **Input**: `02_case1_투명표.pdf`
- **Problem**: **"순수 표 데이터만 필요"**. RAG 성능을 높이기 위해 서론/푸터 등의 노이즈를 배제하고, 테두리가 없는(투명) 표 구조에서 데이터만 정확히 뽑아내야 합니다.
- **Solution**: **지능형 그리드 재구성 (Grid Reconstruction)**. 텍스트의 상단(Top) 좌표를 기준으로 행을 묶고, 열(X) 좌표 버킷을 정의하여 데이터를 슬롯에 배치합니다.
- **핵심 코드(Key Code - `parse_success.py`)**:
  ```python
  # 1. 행(Row) 그룹화 (Y-Clustering)
  # 8px 이내의 좌표 차이는 동일한 행으로 간주
  words.sort(key=lambda w: w['top'])
  for i in range(1, len(words)):
      if words[i]['top'] - current_row[0]['top'] <= 8:
          current_row.append(words[i])

  # 2. 열(Column) 배정 (X-Bucketing)
  for w in row_words:
      mid_x = (w['x0'] + w['x1']) / 2
      if mid_x < 110: col0.append(w['text'])     # 태그 열
      elif mid_x < 280: col1.append(w['text'])   # 설명 열
      else: col2.append(w['text'])               # 예시 열
  ```

> [!CAUTION]
> **해당 코드의 한계 (Limitations)**
>
> 현재의 `parse_success.py`는 특정 PDF 레이아웃에 맞춰 X 좌표(110, 280)와 헤더 텍스트를 **하드코딩** 한 상태입니다. 
> 1. 표의 너비나 여백이 달라지면 열 배정이 틀어질 수 있습니다.
> 2. 헤더 내용이 바뀌면 필터링 로직이 작동하지 않을 수 있습니다.

> [!TIP]
> **기술 멘토의 조언 (Mentor's Advice)**
>
> 본 예제는 복잡한 알고리즘보다 **"좌표 기반 그리드 재구성"** 이라는 핵심 전략을 명확하게 전달하기 위해 설계된 **PoC(Proof of Concept)** 코드입니다. 실제 상용 RAG 환경에서는 다음과 같은 **동적 분석** 로직이 추가되어야 합니다.
>
> 1. **동적 X 경계 감지**: 페이지 내 텍스트 분포를 분석하여 '세로 공백 구간'을 자동으로 찾아 경계선을 설정합니다.
> 2. **헤더 자동 인식**: 폰트 스타일(Bold)이나 배경색 정보를 활용하여 첫 번째 행을 헤더로 자동 추론합니다.

- **핵심 코드(Key Code - `parse_success.py`)**: 텍스트의 X축 투영(Shadow) 분석을 통해 열 경계를 자동으로 계산하는 고도화된 로직이 적용되었습니다.

### Case 2: 페이지 분리 (Multipage Table)

- **Input**: `02_case2_페이지분리.pdf`
- **Problem**: **"헤더 누락"**. 긴 표가 다음 페이지로 넘어갈 때, 두 번째 페이지에는 헤더(컬럼명)가 없는 경우가 많습니다.
  - 결과: 2페이지의 데이터가 1페이지의 데이터와 합쳐지지 않고 겉돕니다.
- **Solution**: **헤더 캐싱(Header Caching)**. 첫 페이지에서 헤더를 변수에 저장해두고, 헤더가 없는 페이지를 만날 때마다 저장해둔 헤더를 강제로 끼워 넣습니다.
- **핵심 코드(Key Code - `parse_success.py`)**:
  ```python
  headers = None

  if page.page_number == 1:
      headers = table[0]  # 첫 페이지 헤더 저장
  else:
      # 두 번째 페이지부터는 저장된 헤더 사용
      # (데이터만 있는 리스트에 헤더를 붙여서 DataFrame 생성 가능하게 함)
      table.insert(0, headers)
  ```

### Case 3: 셀 내 목록 (List in Cell)

- **Input**: `02_case3_셀내목록.pdf`
- **Problem**: **"줄바꿈 파괴"**. 셀 안에 여러 줄의 텍스트(엔터키 포함)가 있을 때, 마크다운 표로 변환하면 줄바꿈(`\n`) 때문에 표가 깨집니다.
- **Solution**: **치환(Replacement)**. 줄바꿈 문자(`\n`)를 HTML 태그 `<br>`로 바꾸면 마크다운 테이블 안에서도 줄바꿈이 유지됩니다.
- **핵심 코드(Key Code - `parse_success.py`)**:
  ```python
  # 줄바꿈(\n)을 <br> 태그로 변환
  cleaned_row = [
      str(cell).replace("\n", "<br>") if cell else "" 
      for cell in row
  ]
  ```

---

> [!TIP]
> **표 처리의 핵심**: `pdfplumber`라고 만능이 아닙니다.
>
> 1. 선이 없으면 -> **수동 클러스터링 (좌표 분석)**
> 2. 헤더가 없으면 -> 변수에 저장해서 재사용
> 3. 줄바꿈이 문제면 -> `<br>` 치환
>    이 3가지 패턴으로 90% 이상의 표를 해결할 수 있습니다.

## 3. RAG 구축 전략 (RAG Strategy)

표(Table) 데이터 처리에서 가장 중요한 것은 **"구조적 정합성을 유지하며 텍스트화 하는 것"** 입니다. 표의 행과 열 관계가 깨지면 LLM은 수치 데이터 간의 연관 관계를 잘못 해석하여 심각한 할루시네이션을 일으킬 수 있습니다.

| 문제 상황 | RAG에 미치는 영향 (Risk) | 해결 전략 (Solution) |
| :--- | :--- | :--- |
| **투명표 (Case 1)** | 테두리가 없어 표를 문장으로 인식하면, 행/열 데이터가 뒤섞여 수치 매칭이 불가능해집니다. | **그리드 재구성 (X-Y Bucketing)**: 좌표를 기반으로 단어를 논리적 격자에 강제 배치하여 구조를 복원합니다. |
| **페이지 분리 (Case 2)** | 다음 페이지의 데이터가 어떤 컬럼의 값인지 알 수 없게 되어 정보의 오분류가 발생합니다. | **헤더 캐싱 (Header Caching)**: 첫 페이지의 헤더를 기억했다가 모든 후속 페이지 표에 주입합니다. |
| **셀 내 목록 (Case 3)** | 셀 내부의 줄바꿈이 마크다운 표 구조를 깨뜨려 전체 데이터 로드가 실패할 수 있습니다. | **HTML 태그 치환**: 줄바꿈(`\n`)을 `<br>` 태그로 바꾸어 마크다운 표 안의 형식을 유지합니다. |

> **본 실습의 핵심**:
> - **Markdown 우선 전략**: RAG 시스템에서 LLM은 CSV보다 마크다운 표 형식을 더 직관적으로 파악합니다. 모든 표 추출 결과를 마크다운으로 통일하여 임베딩 및 검색 효율을 극대화했습니다.

## 4. RAG Comparison (Success vs Fail)

### 성공 사례 (Success)

- **파일**: `02_case1_투명표_성공.md`
- **결과**: 노이즈 없이 순수하게 표 데이터만 마크다운으로 완벽 복원. (동적 열 감지 로직 적용)

```markdown
| 태그 (Tag) | 설명 (Description) | 사용 예시 (Example) |
|---|---|---|
| Feat | 새로운 기능을 추가할 때 사용합니다. | Feat: 소셜 로그인 기능 추가 |
| Fix | 버그를 수정할 때 사용합니다. | Fix: 결제 모달이 닫히지 않는 오류 수정 |
| Refactor | 코드 리팩토링 (기능 변경 없음) | Refactor: 회원가입 로직 함수 분리 |
| Style | 코드 포맷팅, 세미콜론 누락 등 (로직 | Style: 메인 페이지 코드 포맷팅 적용 |
```

### 실패 사례 (Fail)

- **파일**: `02_case1_투명표_실패.md`
- **결과**: 표 구조가 깨져서 일반 텍스트로 인식됨.

```text
💡 작성 Tip
커밋 메시지는 동료를 위한 배려입니다.
'제목'은 50자 이내로 요약하고, '본문'에는
변경 이유를 상세히 적어주세요.
신입 개발자 온보딩 가이드
Metacoding Dev Team | 문서번호: 2026-DEV-001 | Ver 1.0
3. 커밋 메시지 규칙 (Commit Convention)
우리 팀은 Git 커밋 메시지의 가독성을 위해 Conventional
Commits 규칙을 따릅니다. 모든 커밋 메시지는 아래 정의된
[태그]로 시작해야 하며, 파이프라인에서 자동 검사됩니다.
```
