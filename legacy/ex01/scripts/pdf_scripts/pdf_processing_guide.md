# PDF 처리 라이브러리 및 스크립트 가이드 (ex01)

이 문서는 `실습용/ex01/scripts/pdf_scripts` 디렉토리에 포함된 PDF 처리 스크립트들이 사용하는 라이브러리와 주요 기법을 설명합니다.

## 1. 사용된 핵심 라이브러리

### `pdfplumber`
- **용도**: PDF 텍스트 추출, 표(Table) 데이터 추출, 레이아웃 분석(좌표 기반 Crop).
- **특징**: `PyMuPDF(fitz)`보다 속도는 느리지만, **표 추출(Table Extraction)** 기능이 강력하고 레이아웃 정보를 상세하게 제공합니다.
- **주요 메서드**:
  - `.open(path)`: PDF 파일 열기
  - `.pages`: 페이지 객체 리스트 접근
  - `.extract_text()`: 텍스트 추출
  - `.extract_table()`: 표 데이터를 리스트 형태로 추출
  - `.crop(bbox)`: 특정 좌표 영역만 잘라내기
  - `.filter(function)`: 특정 조건(예: 표 영역 제외)에 맞는 객체만 필터링

### `pandas`
- **용도**: 추출된 표 데이터를 데이터프레임(DataFrame)으로 변환하고, 마크다운(Markdown) 표 형식으로 출력하는 데 사용됩니다.
- **주요 메서드**:
  - `.DataFrame(data)`: 리스트 데이터를 데이터프레임으로 변환
  - `.to_markdown()`: 데이터프레임을 마크다운 텍스트로 변환

---

## 2. 주요 스크립트별 기법 분석

### A. 텍스트 추출 및 레이아웃 유지 (Column/Shredding)
- **파일**: `01_column/case1_shredding/success/parse_성공_01.py`
- **기법**: `x_tolerance` 옵션을 조절하여 다단 편집된 문서에서도 단어 간격을 적절히 인식하도록 합니다.
```python
with pdfplumber.open(input_pdf) as pdf:
    for page in pdf.pages:
        # layout=True: 텍스트의 물리적 위치를 최대한 보존하여 추출
        text = page.extract_text(layout=True, x_tolerance=2)
```

### B. 표 데이터 추출 (Table)
- **파일**: `02_table/case1_complex_merge/success/parse_성공.py`
- **기법**: `extract_table()`을 사용하여 표 구조를 2차원 리스트로 가져온 후, 마크다운 문법으로 변환합니다.
```python
table = page.extract_table()
if table:
    # 헤더 처리
    md_table = "| " + " | ".join([str(c) for c in table[0]]) + " |\n"
    # 구분선 처리
    md_table += "| " + " | ".join(["---" for _ in table[0]]) + " |\n"
    # 데이터 행 처리
    for row in table[1:]:
        md_table += "| " + " | ".join([str(c) for c in row]) + " |\n"
```

### C. 노이즈 제거 (Noise/Header & Footer)
- **파일**: `03_noise/case1_header_footer/success/parse_성공_03.py`
- **기법**: `crop(bbox)` 기능을 사용하여 헤더와 푸터 영역을 물리적으로 잘라내고, 본문 영역(ROI)에서만 텍스트를 추출합니다.
```python
# bbox = (x0, top, x1, bottom)
# 상단 100, 하단 750 좌표를 기준으로 본문만 선택
bbox = (0, 100, page.width, 750) 
cropped = page.crop(bbox)
text = cropped.extract_text()
```

### D. 복합 레이아웃 분석 (Complex/Integrated)
- **파일**: `06_complex/case1_integrated/success/parse_성공.py`
- **기법**: 
    1. **영역 분할**: 페이지를 좌표 기준(Zone)으로 나눕니다 (Zone A: Intro, Zone B: Table, Zone C: Content).
    2. **필터링**: 본문 텍스트 추출 시, 이미 추출한 표 영역(`table_bboxes`)에 포함된 텍스트는 제외합니다.
```python
# 표 영역에 포함되지 않는 텍스트만 필터링하는 함수 정의
def not_inside_tables(obj):
    # obj['x0'], obj['top'] 등을 확인하여 표 영역과 겹치는지 판단
    ...

# 필터 적용 후 텍스트 추출
text = page.filter(not_inside_tables).extract_text()
```

---

## 3. 고급 기능 (OCR 및 Vision)
`04_ocr` 및 `05_vision` 디렉토리의 스크립트들은 `pdfplumber`로 해결할 수 없는 이미지/차트 분석을 다룹니다. 이 경우, 단순 파이썬 라이브러리가 아닌 **AI 모델(VLM, OCR 엔진)** 연동이 필요합니다.

- **관련 파일**: `ex02/scripts/ai_pdf_to_md.py` (참조용)
- **주요 방식**:
  - **OCR**: `EasyOCR`, `Tesseract` 또는 `Google Cloud Vision API` 활용
  - **Vision**: `GPT-4o`, `Claude 3.5 Sonnet`, `Ollama(LLaVA)` 등의 멀티모달 LLM에게 이미지를 전송하여 텍스트 설명 생성

> **참고**: `ex01`의 성공 예제 스크립트(`parse_성공_04.py`, `parse_성공_05.py`)는 실제 AI 연동 코드가 포함되어 있지 않으며, AI 파이프라인을 거쳤을 때의 **예상 결과(Hardcoded Output)**를 보여주도록 작성되어 있습니다.
