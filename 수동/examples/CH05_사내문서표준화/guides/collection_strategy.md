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
| HWP / HWPX | 중간 | pyhwp / LibreOffice 변환 | 중간~높음 | `pyhwp`, `subprocess` |
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

### 2-4. HWP / HWPX — pyhwp 또는 LibreOffice 변환

HWP(한컴 한글)는 국내 공공기관·기업에서 많이 사용하는 형식입니다.
두 가지 접근법이 있으며, 환경에 따라 선택하십시오.

**방법 A: pyhwp (텍스트 추출만 필요할 때)**

```python
import subprocess
import tempfile
import os

def extract_text_from_hwp_pyhwp(file_path: str) -> str:
    """
    pyhwp CLI를 사용해 HWP 파일에서 텍스트를 추출합니다.
    설치: pip install pyhwp

    Args:
        file_path: .hwp 파일 경로

    Returns:
        추출된 텍스트. 실패 시 빈 문자열 반환.

    주의:
        - pyhwp는 HWP 5.x 형식까지 지원 (HWPX 미지원)
        - 표·이미지 내부 텍스트는 추출 불가
    """
    try:
        result = subprocess.run(
            ["hwp5txt", file_path],  # pyhwp CLI 도구
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"[경고] hwp5txt 실패: {result.stderr}")
            return ""
    except FileNotFoundError:
        print("[오류] pyhwp가 설치되지 않았습니다. pip install pyhwp")
        return ""
```

**방법 B: LibreOffice → DOCX 변환 (권장, 더 안정적)**

```python
import subprocess
import tempfile
import os
from pathlib import Path
from docx import Document

def extract_text_from_hwp_libreoffice(file_path: str) -> str:
    """
    LibreOffice를 사용해 HWP/HWPX를 DOCX로 변환 후 텍스트를 추출합니다.
    사전 조건: LibreOffice 설치 필요 (brew install libreoffice / apt install libreoffice)

    Args:
        file_path: .hwp 또는 .hwpx 파일 경로

    Returns:
        추출된 전체 텍스트
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # LibreOffice로 DOCX 변환
        result = subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to", "docx",
                "--outdir", tmpdir,
                file_path,
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"[오류] LibreOffice 변환 실패: {result.stderr}")
            return ""

        # 변환된 DOCX 읽기
        stem = Path(file_path).stem
        docx_path = os.path.join(tmpdir, f"{stem}.docx")
        if not os.path.exists(docx_path):
            print("[오류] 변환된 DOCX 파일을 찾을 수 없습니다.")
            return ""

        doc = Document(docx_path)
        parts = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
        return "\n".join(parts)


# 사용 예시
if __name__ == "__main__":
    # 방법 A (pyhwp)
    text_a = extract_text_from_hwp_pyhwp("data/hr/인사규정.hwp")

    # 방법 B (LibreOffice, HWPX 포함)
    text_b = extract_text_from_hwp_libreoffice("data/hr/인사규정.hwpx")
    print(f"추출 완료: {len(text_b)}자")
```

> **HWPX**: HWP의 XML 기반 신규 형식(.hwpx)은 ZIP 파일 내부에 XML이 있어,
> `zipfile` + XML 파싱으로도 접근 가능하지만, LibreOffice 변환이 가장 간단합니다.

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
- [ ] 각 파일 형식에 맞는 라이브러리가 설치되어 있는가 (`pip install pymupdf python-docx pyhwp openpyxl`)
- [ ] HWP/HWPX 파일이 포함된 경우 LibreOffice가 설치되어 있는가 (`brew install libreoffice` / `apt install libreoffice`)
- [ ] 스캔 PDF가 포함된 경우 10장 OCR 섹션을 참조하였는가
- [ ] 수집된 파일을 저장할 디렉토리 구조가 설계되어 있는가 (`data/{부서명}/`)
- [ ] 민감 정보(개인정보, 재무 기밀)가 포함된 문서의 처리 방침이 결정되었는가
