# 문서 유형별 수집 전략 가이드

이 가이드는 RAG 시스템 구축을 위한 사내 문서 수집 방법과 우선순위를 정의합니다.
올바른 수집 전략을 수립하면 이후 전처리 부담이 줄어들고 벡터 DB(6장)에 입력되는 데이터 품질이 향상됩니다.

---

## 1. 문서 유형별 수집 우선순위 매트릭스

| 유형 | 우선순위 | 수집 방법 | 전처리 난이도 | 권장 라이브러리 |
|------|---------|---------|------------|--------------|
| PDF (텍스트 레이어 있음) | 높음 | PyMuPDF | 낮음 | `pymupdf` |
| Word (.docx) | 높음 | python-docx | 낮음 | `python-docx` |
| Markdown | 높음 | 직접 읽기 | 없음 | 표준 라이브러리 |
| HWP / HWPX | 중간 | **PDF로 변환 후 PDF 파이프라인 위임** | 낮음 (변환 후) | `subprocess` + LibreOffice |
| 스캔 PDF (이미지) | 낮음 | OCR (10장 참조) | 높음 | `easyocr`, `llava` |
| Excel | 중간 | openpyxl | 중간 | `openpyxl`, `pandas` |

> **판단 기준**: 동일한 업무 가치가 있는 문서라면, 전처리 난이도가 낮은 유형부터 수집합니다.
> 스캔 PDF는 OCR 오류율이 높으므로, 같은 내용의 디지털 원본이 있다면 원본을 우선 사용하십시오.

---

## 2. 유형별 수집 코드 예시

### 2-1. PDF (텍스트 레이어 있음) — PyMuPDF

텍스트 레이어가 있는 PDF는 PyMuPDF(`fitz`)로 직접 추출합니다.
이미지처럼 보여도 실제로는 선택 가능한 텍스트가 있다면 이 방법을 사용하십시오.

```python
import fitz  # pip install pymupdf

def extract_text_from_pdf(file_path: str) -> str:
    """
    텍스트 레이어가 있는 PDF에서 전체 텍스트를 추출합니다.

    Args:
        file_path: PDF 파일 경로

    Returns:
        추출된 전체 텍스트 (페이지 구분 없이 연결)
    """
    doc = fitz.open(file_path)
    pages_text = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")  # "text" 모드: 텍스트 레이어 추출
        pages_text.append(text)

    doc.close()
    return "\n".join(pages_text)


# 사용 예시
if __name__ == "__main__":
    raw_text = extract_text_from_pdf("data/hr/연차규정_v2.pdf")
    print(f"추출 완료: {len(raw_text)}자")
```

### 2-2. Word 문서 (.docx) — python-docx

Word 문서는 단락(paragraph) 단위로 순서대로 추출합니다.
표(table) 안의 텍스트는 별도로 처리해야 합니다.

```python
from docx import Document  # pip install python-docx

def extract_text_from_docx(file_path: str) -> str:
    """
    Word(.docx) 파일에서 단락 및 표 텍스트를 추출합니다.

    Args:
        file_path: .docx 파일 경로

    Returns:
        추출된 전체 텍스트
    """
    doc = Document(file_path)
    parts = []

    # 단락 추출
    for para in doc.paragraphs:
        if para.text.strip():  # 빈 단락 제외
            parts.append(para.text.strip())

    # 표 내부 텍스트 추출
    for table in doc.tables:
        for row in table.rows:
            row_texts = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_texts:
                parts.append(" | ".join(row_texts))  # 셀을 " | "로 구분

    return "\n".join(parts)


# 사용 예시
if __name__ == "__main__":
    raw_text = extract_text_from_docx("data/hr/신입사원_온보딩가이드.docx")
    print(f"추출 완료: {len(raw_text)}자")
```

### 2-3. Markdown — 직접 읽기

Markdown은 별도 라이브러리 없이 텍스트 파일로 읽습니다.
RAG 입력 시 `#`, `**` 등의 마크다운 기호를 유지하거나 제거할지 정책을 결정하십시오.
기호를 제거하면 LLM 컨텍스트 토큰을 절약할 수 있습니다.

```python
import re

def extract_text_from_markdown(file_path: str, remove_syntax: bool = True) -> str:
    """
    Markdown 파일에서 텍스트를 읽고 선택적으로 마크다운 기호를 제거합니다.

    Args:
        file_path: .md 파일 경로
        remove_syntax: True이면 마크다운 기호 제거 (기본값 True)

    Returns:
        추출된 텍스트
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if remove_syntax:
        # 헤더 기호(#) 제거
        content = re.sub(r"^#{1,6}\s+", "", content, flags=re.MULTILINE)
        # 굵게/기울임 기호 제거
        content = re.sub(r"\*{1,2}(.+?)\*{1,2}", r"\1", content)
        # 인라인 코드 기호 제거
        content = re.sub(r"`(.+?)`", r"\1", content)

    return content.strip()


# 사용 예시
if __name__ == "__main__":
    raw_text = extract_text_from_markdown("data/dev/API_설계가이드.md")
    print(f"추출 완료: {len(raw_text)}자")
```

### 2-4. HWP / HWPX — 처리 방법 개요

HWP(한컴 한글)는 국내 공공기관·기업에서 많이 사용하는 형식입니다.
크게 세 가지 접근법이 있습니다.

| 방법 | 도구 | 장점 | 단점 |
|------|------|------|------|
| **A. pyhwp** | `pip install pyhwp` (`hwp5txt` CLI) | 추가 설치 간단 | HWP 5.x만 지원, 표·이미지 추출 불가 |
| **B. LibreOffice → DOCX** | `libreoffice --convert-to docx` | HWPX 포함, 텍스트/표 추출 가능 | 레이아웃 복잡 시 표 깨짐 |
| **C. PDF로 변환 후 PDF 파이프라인 위임** | `libreoffice --convert-to pdf` | 레이아웃 보존, 이후 처리 통일 | LibreOffice 설치 필요 |

**본 책에서는 방법 C를 사용합니다.**

HWP를 PDF로 변환하면 이후 처리는 일반 PDF와 완전히 동일합니다.
어떤 도구(한컴오피스, LibreOffice, 클라우드 변환기)로 PDF를 만들든 상관없습니다.

```
HWP 파일
    ↓  LibreOffice (또는 한컴오피스에서 직접 PDF 저장)
PDF 파일  →  CH06 extractor.py (pdfplumber / Vision LLM)  →  Markdown
```

**LibreOffice로 HWP → PDF 자동 변환**

```python
import subprocess
from pathlib import Path

def hwp_to_pdf(hwp_path: str, output_dir: str = ".") -> str:
    """
    LibreOffice headless로 HWP/HWPX를 PDF로 변환합니다.
    사전 조건: brew install libreoffice  또는  apt install libreoffice

    Args:
        hwp_path  : .hwp 또는 .hwpx 파일 경로
        output_dir: PDF 저장 디렉토리

    Returns:
        생성된 PDF 파일 경로 (이후 CH06 파이프라인에 그대로 전달)
    """
    result = subprocess.run(
        ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", output_dir, hwp_path],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"LibreOffice 변환 실패: {result.stderr}")

    pdf_path = str(Path(output_dir) / f"{Path(hwp_path).stem}.pdf")
    print(f"✓ 변환 완료: {pdf_path}")
    return pdf_path

# 사용 예시
# pdf_path = hwp_to_pdf("data/hr/HR_취업규칙_v1.0.hwp", output_dir="data/hr/")
# → 이후 CH06의 extract_text_pdfplumber(pdf_path) 또는 extract_pdf_to_markdown(pdf_path) 사용
```

> **방법 A, B가 궁금하다면?**
> - **pyhwp**: `pip install pyhwp` 후 `hwp5txt 파일.hwp > output.txt`로 텍스트 추출 가능.
>   단순 텍스트만 필요하고 표/이미지가 없는 경우에 적합.
> - **LibreOffice → DOCX**: `--convert-to docx` 후 `python-docx`로 파싱.
>   표 구조를 보존해야 하는 경우에 활용. 단, 복잡한 레이아웃에서는 표가 깨질 수 있음.
>
> 세 방법 모두 LibreOffice가 설치되어 있으면 사용 가능합니다.
> 본 책의 실습에서는 PDF 파이프라인 하나로 모든 형식을 통일하는 방법 C를 따릅니다.

---

### 2-5. Excel — openpyxl

Excel 파일은 시트별, 행별로 순회하며 셀 값을 추출합니다.
빈 행이나 헤더 행 처리 방침을 명확히 정해두어야 합니다.

```python
import openpyxl  # pip install openpyxl

def extract_text_from_excel(file_path: str, sheet_name: str = None) -> str:
    """
    Excel(.xlsx) 파일의 셀 데이터를 텍스트로 추출합니다.

    Args:
        file_path: .xlsx 파일 경로
        sheet_name: 특정 시트명 (None이면 첫 번째 시트 사용)

    Returns:
        행 단위로 결합된 텍스트
    """
    wb = openpyxl.load_workbook(file_path, data_only=True)

    if sheet_name:
        ws = wb[sheet_name]
    else:
        ws = wb.active

    rows_text = []
    for row in ws.iter_rows(values_only=True):
        # None 셀 제거 후 문자열 변환
        cell_values = [str(cell) for cell in row if cell is not None]
        if cell_values:
            rows_text.append(" | ".join(cell_values))

    return "\n".join(rows_text)


# 사용 예시
if __name__ == "__main__":
    raw_text = extract_text_from_excel("data/finance/2024년_예산현황.xlsx")
    print(f"추출 완료: {len(raw_text)}자")
```

---

## 3. 수집 우선순위 결정 흐름도

```
사내 문서 목록 확보
        |
        v
디지털 원본이 있는가?
   Yes → 파일 형식 확인 (PDF/Word/Markdown/Excel)
   No  → 스캔본 또는 이미지 → 10장 OCR 섹션 참조
        |
        v
PDF인 경우: 텍스트 레이어 확인 (파일 열기 → 텍스트 선택 가능 여부)
   텍스트 레이어 있음 → PyMuPDF로 즉시 수집 (우선순위 높음)
   이미지 PDF       → 10장 OCR 섹션 참조 (우선순위 낮음)
```

---

## 4. 수집 체크리스트

수집을 시작하기 전에 아래 항목을 확인하십시오.

- [ ] 수집 대상 문서 목록이 확정되었는가 (부서별 협조 완료)
- [ ] 각 파일 형식에 맞는 라이브러리가 설치되어 있는가 (`pip install pymupdf pdfplumber python-docx openpyxl`)
- [ ] HWP/HWPX 파일이 포함된 경우 LibreOffice가 설치되어 있는가 (`brew install libreoffice` / `apt install libreoffice`)
- [ ] HWP → PDF 변환 시 파일명 네이밍 규칙(`{부서}_{문서명}_{버전}.pdf`)을 유지했는가
- [ ] 스캔 PDF가 포함된 경우 10장 OCR 섹션을 참조하였는가
- [ ] 수집된 파일을 저장할 디렉토리 구조가 설계되어 있는가 (`data/{부서명}/`)
- [ ] 민감 정보(개인정보, 재무 기밀)가 포함된 문서의 처리 방침이 결정되었는가
