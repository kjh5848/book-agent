# Case 03: 노이즈 (Noise) 처리

## 1. 개요 (Summary)
- **난이도 (Difficulty)**: 하 (Low)
- **주요 라이브러리 (Key Library)**: `pdfplumber` (Crop, Filter)
- **핵심 개념 (Core Concept)**: 필요한 텍스트보다 불필요한 텍스트(헤더, 푸터, 워터마크)가 더 많을 때,> **본 실습의 선택**:* 으로 접근합니다.

## 2. 케이스 분석 (Case Analysis)

### Case 1: 헤더/푸터 (Header & Footer)
- **입력 (Input)**: `03_case1_헤더푸터.pdf`
- **문제 (Problem)**: **"반복적인 노이즈"**. 모든 페이지 상단에 "대외비", 하단에 "Page 1/10" 같은 텍스트가 있어서, RAG 검색 시 문맥을 방해합니다.
- **해결 (Solution)**: **영역 자르기(Coordinate Cropping)**. 상하단 10~15% 영역을 물리적으로 잘라내고 본문만 남깁니다.
- **핵심 코드 (Key Code)** `parse_success.py`:
  ```python
  # y 좌표 0~100(헤더), 750~(푸터) 제외
  # bbox = (x0, top, x1, bottom)
  bbox = (0, 100, page.width, 750)
  clean_page = page.crop(bbox)
  text = clean_page.extract_text()
  ```

### Case 2: 사이드바 (Sidebar)
- **입력 (Input)**: `03_case2_사이드바.pdf`
- **문제 (Problem)**: **"문맥 침범"**. 본문을 읽는 도중에 오른쪽 사이드바의 "관련 기사"나 "광고" 텍스트가 갑자기 튀어나옵니다.
- **해결 (Solution)**: **수직 분할(Vertical Split)**. 웹페이지의 CSS 레이아웃처럼, 페이지 너비의 특정 지점(예: 70%)을 기준으로 본문과 사이드바를 분리합니다.
- **핵심 코드 (Key Code)** `parse_success.py`:
  ```python
  boundary = page.width * 0.7
  
  # 본문 (왼쪽 70%)
  body = page.crop((0, 0, boundary, page.height))
  
  # 사이드바 (오른쪽 30%)
  sidebar = page.crop((boundary, 0, page.width, page.height))
  ```

### Case 3: 워터마크 (Watermark)
- **입력 (Input)**: `03_case3_워터마크.pdf`
- **문제 (Problem)**: **"겹친 글자"**. 본문 텍스트 위에 붉은색 또는 회색의 "CONFIDENTIAL" 워터마크가 겹쳐 있어서 OCR/파서가 글자를 잘못 인식합니다.
- **해결 (Solution)**: **색상 필터링(Color Filtering)**. 워터마크는 보통 본문(검은색)과 다른 색상을 씁니다. 검은색(`(0,0,0)`) 글자만 남기고 나머지는 지웁니다.
- **핵심 코드 (Key Code)** `parse_success.py`:
  ```python
  def keep_black_text(obj):
      # 객체 타입이 글자(char)이고, 색상이 검은색인 경우만 True
      return obj.get("object_type") == "char" and obj.get("non_stroking_color") == (0, 0, 0)
  
  clean_page = page.filter(keep_black_text)
  text = clean_page.extract_text()
  ```

## 3. RAG 구축 전략 (RAG Strategy)

노이즈 제거의 핵심은 **"순수 정보(Signal)와 소음(Noise)의 분리"** 입니다. 매 페이지 반복되는 텍스트나 본문과 관련 없는 데이터가 섞여 들어가면 검색 엔진의 Top-K 결과가 오염되어 실질적인 답변 품질이 급격히 저하됩니다.

| 문제 상황 | RAG에 미치는 영향 (Risk) | 해결 전략 (Solution) |
| :--- | :--- | :--- |
| **헤더/푸터 (Case 1)** | 매 페이지 반복되는 텍스트가 검색 결과의 상위권을 차지하여 실제 정답 영역을 밀어버림. | **영역 자르기 (Coordinate Cropping)**: 상하단 10~15% 영역을 물리적으로 제거하여 본문만 남김. |
| **사이드바 (Case 2)** | 본문과 관련 없는 광고나 부가 정보가 문맥을 끊어놓아 LLM의 이해도를 떨어뜨림. | **수직 분할 (Vertical Split)**: 본문 영역(Main Body)의 X좌표 구간만 지정하여 독립적으로 추출. |
| **워터마크 (Case 3)** | 본문 위에 겹친 워터마크가 OCR 인식을 방해하거나 불필요한 단어를 본문 사이에 끼워 넣음. | **색상 필터링 (Color Filtering)**: 텍스트 개체의 색상 속성을 분석하여 본문(검은색)만 추출하고 나머지 제거. |

> **본 실습의 핵심**:
> - **좌표 기반의 정밀도**: 단순히 텍스트를 모두 긁어오는 것이 아니라, 사람이 문서를 볼 때 무시하는 영역을 파이썬 코드에서도 명시적으로 무시(Crop/Filter)해주는 것이 RAG 전처리의 첫걸음입니다.

## 4. RAG Comparison (Success vs Fail)

### 성공 사례 (Success)
- **파일**: `03_case1_헤더푸터_성공.md`
- **결과**: `page.crop()`으로 상하단 노이즈 제거, 본문만 깔끔하게 유지.

```markdown
보안 정책 및 운영 가이드
문서번호: 2026-SEC-001 | 시행일: 2026.01.01
제3장 정보 보안 및 AI 윤리
본 장에서는 Metacoding Inc.의 하이브리드 근무 환경에서 발생할 수 있는 모든 보안 위협에 대응
하기 위한 핵심 원칙을 정의합니다. 우리는 기존의 경계형 보안 모델을 탈피하고, 데이터 중심의 보
안 체계를 수립하였습니다.
```

### 실패 사례 (Fail)
- **파일**: `03_case1_헤더푸터_실패.md`
- **결과**: 헤더/푸터가 본문 중간에 섞여 들어감.

```text
CONFIDENTIAL DOCUMENT - DO NOT DISTRIBUTE
Metacoding Inc. Security Policy v2.0
CONFIDENTIAL
Metacoding Security Team | Security Policy v2.0 - Page 1 | All rights reserved.
보안 정책 및 운영 가이드
문서번호: 2026-SEC-001 | 시행일: 2026.01.01
제3장 정보 보안 및 AI 윤리
본 장에서는 Metacoding Inc.의 하이브리드 근무 환경에서 발생할 수 있는 모든 보안 위협에 대응
하기 위한 핵심 원칙을 정의합니다. 우리는 기존의 경계형 보안 모델을 탈피하고, 데이터 중심의 보
안 체계를 수립하였습니다.
```

