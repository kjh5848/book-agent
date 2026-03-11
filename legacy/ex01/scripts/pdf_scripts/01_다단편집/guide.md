# Case 01: 다단 레이아웃 (Column Layout)

## 1. 개요 (Summary)
- **난이도(Difficulty)**: 중급 (Medium)
- **주요 라이브러리(Key Library)**: `pdfplumber`
- **핵심 개념(Core Concept)**: PDF는 문단(Paragraph)을 모릅니다. 단어의 좌표(x, y)를 보고 우리가 직접 문단을 재조립해야 합니다.

## 2. 사례 분석 (Case Analysis)

### Case 1: 다단 편집 - 단어 찢어짐 해결 (Shredding)
- **Input**: `01_case1_다단편집.pdf`
- **Problem**: **"단어 찢어짐"** . 기본적으로 단을 나누는 구분선이 있어 레이아웃 자체는 파악이 가능합니다. 하지만 텍스트가 **양쪽 맞춤(Justified)** 되어 있어 글자 사이 간격이 넓고, 이로 인해 글자가 찢어지거나 줄바꿈이 정상적으로 되지 않습니다.
- **Solution**: `x_tolerance` 값을 사용하여 넓게 퍼진 글자들을 하나의 단어로 봉합하고, 올바른 줄바꿈을 유도합니다.
    > **Tip. x_tolerance란?**
    > - `pdfplumber`가 글자를 추출할 때 **"가로(x축)로 얼마나 떨어져 있는 글자까지 같은 단어로 묶을지"** 결정하는 허용 오차 값입니다.
    > - **값이 적을 때**: `H e l l o` 처럼 글자가 낱개로 찢어집니다. (기본값)
    > - **값이 적절할 때(`5`~`10`)**: `Hello`로 정상 복원됩니다.
    > - **값이 너무 클 때**: `HelloWorld` 처럼 옆 단어까지 붙어버립니다.
    >
    > **Q. 한글과 영어의 차이는?**
    > - **영어(가변폭)**: `i`와 `W`의 너비 차이가 큽니다. 단어 간 공백이 확실해서 비교적 `x_tolerance`에 덜 민감합니다.
    > - **한글(고정폭)**: 글자가 '네모 반듯'해서 자간이 일정해 보이지만, **조사(은/는/이/가)** 가 붙어 있어 단어 경계가 모호할 수 있습니다.
    > - **결론**: **양쪽 맞춤(Justified)** 이 적용된 경우, 언어 무관하게 글자가 찢어지므로 **과감하게 키우는 것(3 -> 5~10)** 이 유리합니다.
- **핵심 코드(Key Code - `parse_성공.py`)**:
  ```python
  # x_tolerance를 늘려서 찢어진 단어 봉합
  text = page.extract_text(x_tolerance=5)
  ```
  > **주의**: 이 방법은 단어는 붙여주지만, **왼쪽/오른쪽 단을 구별하지는 못합니다** . 문장이 뒤섞이는 문제(Stitching)는 아래 **Case 2**에서 해결합니다.


### Case 2: 페이지 병합 (Stitching)
- **Input**: `01_case2_페이지병합.pdf`
- **Problem**: **"레이아웃 미분리"** . Case 1과 달리 단을 나누는 명확한 레이아웃 정보나 구분선이 없어, 파서가 전체를 통으로 인식하는 경우입니다.
    - 결과: 왼쪽 단의 문장과 오른쪽 단의 문장이 같은 높이(y좌표)에 있으면, 한 줄로 이어져 읽히는 **Stitching(바느질)** 현상이 발생합니다. (왼쪽 절반 + 오른쪽 절반이 섞임)
- **Solution**: **공간 분할(Cropping)** . 페이지를 물리적으로 반으로 잘라서 왼쪽을 먼저 읽고, 오른쪽을 나중에 읽습니다.
- **핵심 코드(Key Code - `parse_성공.py`)**:
  ```python
  width = page.width
  mid = width / 2
  
  # 1. 왼쪽 단 (Left Column)
  left_bbox = (0, 0, mid, height)
  left_col = page.crop(left_bbox).extract_text()
  
  # 2. 오른쪽 단 (Right Column)
  right_bbox = (mid, 0, width, height)
  right_col = page.crop(right_bbox).extract_text()
  ```

### Case 3: 내포된 표 (Nested Tables)
- **Input**: `01_case3_내포된표.pdf`
- **Problem**: 다단 안에 **박스(표/이미지)** 가 들어있는 경우. 단순 Crop으로는 박스 내부의 텍스트가 잘리거나, 본문과 섞여버립니다.
- **Solution**: **재귀적 분할(Recursive Split)** .
    1. `page.rects`로 박스(사각형) 좌표를 먼저 찾습니다.
    2. 박스 영역을 제외한 위/아래 공간을 먼저 읽습니다.
    3. 박스 내부는 별도로(다단인지, 표인지) 판단하여 추출합니다.
- **핵심 코드(Key Code - `parse_성공.py`)**:
  ```python
  # 박스(Rect) 감지
  candidates = [r for r in page.rects if r["x0"] < mid] # 왼쪽 단 내부의 박스 찾기
  
  if candidates:
      inner_rect = max(candidates, key=lambda x: x['width'])
      
      # Zone A: 박스 위쪽 텍스트
      top_area = page.crop((0, 0, mid, inner_rect['top']))
      
      # Zone B: 박스 내부 처리 (예: 제목 + 2단 분리)
      inner_box = page.crop((inner_rect['x0'], inner_rect['top'], inner_rect['x1'], inner_rect['bottom']))
      
      # Zone C: 박스 아래쪽 텍스트
      bottom_area = page.crop((0, inner_rect['bottom'], mid, height))
  ```

---
> **전략의 핵심**: 무조건 전체를 읽지 마세요.
> 사람이 문서를 읽는 순서(**왼쪽 -> 오른쪽, 위 -> 아래**) 대로 좌표를 잘라서(Crop) 읽는 것이 가장 정확합니다.

## 3. RAG 구축 전략 (RAG Strategy)

다단 편집 문서에서 가장 중요한 것은 **"사람이 읽는 순서 그대로 텍스트를 복원하는 것"** 입니다. RAG의 임베딩(Vector) 모델은 단어의 순서와 인접성을 기반으로 의미를 파악하기 때문입니다.

| 문제 상황 | RAG에 미치는 영향 (Risk) | 해결 전략 (Solution) |
| :--- | :--- | :--- |
| **단어 찢어짐(Case 1)** | `대 한 민 국` 처럼 글자가 흩어지면, 검색 엔진이 "대한민국"이라는 키워드를 찾지 못합니다. | **x_tolerance 조정**: 흩어진 글자들을 하나의 온전한 단어로 봉합합니다. |
| **문단 섞임(Case 2)** | 왼쪽 단의 문장과 오른쪽 단의 문장이 섞이면, 전혀 다른 의미의 문장이 되어 할루시네이션을 유발합니다. | **공간 분할(Cropping)**: 물리적으로 구역을 나누어 순서대로 텍스트를 추출합니다. |
| **정보 소실(Case 3)** | 박스 내부 텍스트가 본문과 섞이거나 누락되어, 핵심 데이터(표/이미지 설명)를 잃습니다. | **재귀적 분할(Recursive Split)**: 박스는 별도 영역으로 취급하여 독립적으로 추출합니다. |

> **본 실습의 핵심**:
> - **Markdown 헤더 활용**: `## [왼쪽 메인 컬럼]` 처럼 구역을 명시해주면, LLM이 "여기부터는 앞 문장과 이어지지 않는 새로운 단락이구나"라고 이해할 수 있어 문맥 혼란을 방지합니다.

## 4. RAG Comparison (Success vs Fail)

### 성공 사례 (Success)
- **파일**: `01_case1_다단편집_성공.md`
- **결과**: `x_tolerance` 조정으로 단어가 온전하게 복원됨.

```markdown
## Page 1

문서번호: HR-2026-001
사내 인사 규정 (발췌) 버전: v2.0 (Draft)
대외비 (Confidential)
4. 휴가 및 리프레시 (Leave & Refresh) 3일 이상: 의사 소견서 또는 진단서 제출 필요
4.1 스마트 휴가 승인 (Smart Approval) 4.3 워케이션 지원 (Workation)
Metacoding Inc.는 구성원의 자율성을 존중하며,
회사는 직원들이 창의적인 환경에서 업무에 몰입하고
휴가 사용에 있어 불필요한 절차를 최소화합니다.
재충전할 수 있도록 다음과 같은 워케이션 프로그램을
이를 위해 'Ask-Less, Trust-More' 원칙을 기반으로
적극 지원합니다. 사무실을 벗어나 새로운 환경에서
휴가 제도를 운영하고 있습니다.
일하는 것은 리프레시뿐만 아니라 창의적 사고에도 큰
도움이 됩니다.
```

### 실패 사례 (Fail)
- **파일**: `01_case1_다단편집_실패.md`
- **결과**: 단어가 낱개로 찢어져 검색(Indexing) 불가능.

```text
사내 인사 규정 (발췌)
문서번호: HR-2026-001
버전: v2.0 (Draft)
대외비 (Confidential)
4. 휴가 및 리프레시 (Leave & Refresh)
4.1 스마트 휴가 승인 (Smart Approval)
Metacoding Inc.는 구성원의 자율성을 존중하며,
휴가 사용에 있어 불필요한 절차를 최소화합니다.
이를 위해 'Ask-Less, Trust-More' 원칙을 기반으로
휴가 제도를 운영하고 있습니다.
```

