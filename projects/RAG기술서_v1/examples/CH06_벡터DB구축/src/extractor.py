"""
규칙 기반 PDF 텍스트 추출 모듈.

pdfplumber와 PyMuPDF(fitz) 두 가지 방식으로 PDF에서 텍스트를 추출합니다.
pdfplumber는 표(table) 감지 및 Markdown 변환을 지원합니다.
파일명 네이밍 규칙({부서}_{문서명}_{버전}.pdf)에서 메타데이터를 자동 추출합니다.
"""

import os
import re
from pathlib import Path


def extract_text_pdfplumber(pdf_path: str) -> list[dict]:
    """pdfplumber로 PDF 페이지별 텍스트를 추출합니다.

    표(table)가 감지된 페이지는 extract_table()로 셀 내용을 보존하고
    Markdown 표 형식으로 변환합니다. 표가 없는 페이지는 일반 텍스트로 추출합니다.

    Args:
        pdf_path: 텍스트를 추출할 PDF 파일의 경로.

    Returns:
        페이지별 추출 결과 딕셔너리의 리스트.
        각 딕셔너리 구조:
            {
                "page": int,        # 페이지 번호 (1부터 시작)
                "text": str,        # 추출된 텍스트 (표는 Markdown 형식)
                "source": str,      # 파일명
                "has_table": bool,  # 표 포함 여부
            }

    Raises:
        FileNotFoundError: pdf_path에 파일이 존재하지 않을 때.
        RuntimeError: pdfplumber 미설치 또는 추출 중 오류 발생 시.
    """
    # --- Input ---
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(
            f"PDF 파일을 찾을 수 없습니다: {pdf_path}\n"
            "data/ 폴더에 파일이 있는지 확인하십시오."
        )

    source_name = Path(pdf_path).name
    pages: list[dict] = []

    # --- Process ---
    try:
        import pdfplumber
    except ImportError:
        raise RuntimeError(
            "pdfplumber가 설치되지 않았습니다. 'pip install pdfplumber'를 실행하십시오."
        )

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                has_table = False
                text_parts: list[str] = []

                # 표 감지: 페이지에서 표 영역을 찾습니다
                tables = page.extract_tables()
                if tables:
                    has_table = True
                    # 표 위에 있는 일반 텍스트 추출
                    plain_text = page.extract_text()
                    if plain_text and plain_text.strip():
                        text_parts.append(plain_text.strip())

                    # 각 표를 Markdown 형식으로 변환
                    for table in tables:
                        md_table = _table_to_markdown(table)
                        if md_table:
                            text_parts.append(md_table)
                else:
                    # 표가 없는 페이지: 일반 텍스트 추출
                    plain_text = page.extract_text()
                    if plain_text and plain_text.strip():
                        text_parts.append(plain_text.strip())

                combined_text = "\n\n".join(text_parts).strip()
                if combined_text:
                    pages.append(
                        {
                            "page": page_num + 1,
                            "text": combined_text,
                            "source": source_name,
                            "has_table": has_table,
                        }
                    )

    except Exception as e:
        raise RuntimeError(
            f"pdfplumber로 PDF 텍스트를 추출하는 중 오류가 발생했습니다: {e}"
        )

    # --- Output ---
    return pages


def extract_text_pymupdf(pdf_path: str) -> list[dict]:
    """PyMuPDF(fitz)로 PDF 페이지별 텍스트를 추출합니다.

    pdfplumber와 비교 목적으로 제공되는 대안 추출기입니다.
    fitz.open()으로 PDF를 열고 각 페이지의 텍스트를 추출합니다.

    Args:
        pdf_path: 텍스트를 추출할 PDF 파일의 경로.

    Returns:
        페이지별 추출 결과 딕셔너리의 리스트.
        각 딕셔너리 구조:
            {
                "page": int,        # 페이지 번호 (1부터 시작)
                "text": str,        # 추출된 텍스트
                "source": str,      # 파일명
                "has_table": bool,  # 항상 False (표 미감지)
            }

    Raises:
        FileNotFoundError: pdf_path에 파일이 존재하지 않을 때.
        RuntimeError: PyMuPDF 미설치 또는 추출 중 오류 발생 시.
    """
    # --- Input ---
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(
            f"PDF 파일을 찾을 수 없습니다: {pdf_path}\n"
            "data/ 폴더에 파일이 있는지 확인하십시오."
        )

    source_name = Path(pdf_path).name
    pages: list[dict] = []

    # --- Process ---
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise RuntimeError(
            "PyMuPDF가 설치되지 않았습니다. 'pip install pymupdf'를 실행하십시오."
        )

    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if text and text.strip():
                pages.append(
                    {
                        "page": page_num + 1,
                        "text": text.strip(),
                        "source": source_name,
                        "has_table": False,
                    }
                )
        doc.close()
    except Exception as e:
        raise RuntimeError(
            f"PyMuPDF로 PDF 텍스트를 추출하는 중 오류가 발생했습니다: {e}"
        )

    # --- Output ---
    return pages


def is_complex_layout(pages: list[dict], threshold: float = 0.3) -> bool:
    """규칙 기반 파싱 품질을 판단하여 Vision LLM 권장 여부를 반환합니다.

    페이지당 평균 글자 수가 전체 기대 글자 수의 threshold 미만이면
    레이아웃이 복잡하다고 판단하여 Vision LLM 사용을 권장합니다.
    결재란, 다단 레이아웃, 이미지 위주 페이지를 감지하는 데 사용합니다.

    Args:
        pages: extract_text_pdfplumber 또는 extract_text_pymupdf가 반환한 페이지 리스트.
        threshold: 판단 임계값. 페이지당 평균 글자 수 / 기대 글자 수 비율.
                   기본값은 0.3 (30% 미만이면 복잡 레이아웃으로 판단).

    Returns:
        True이면 Vision LLM 권장, False이면 규칙 기반 파싱으로 충분함.

    Raises:
        ValueError: pages 리스트가 비어 있을 때.
    """
    # --- Input ---
    if not pages:
        raise ValueError(
            "pages 리스트가 비어 있습니다. PDF 추출 결과를 확인하십시오."
        )

    # --- Process ---
    # 기대 글자 수: A4 기준 약 30행 × 50자 = 1,500자 (일반 텍스트 문서 기준)
    expected_chars_per_page = 1500

    total_chars = sum(len(p["text"]) for p in pages)
    avg_chars_per_page = total_chars / len(pages)
    ratio = avg_chars_per_page / expected_chars_per_page

    # --- Output ---
    return ratio < threshold


def parse_filename_metadata(pdf_path: str) -> dict:
    """파일명에서 메타데이터를 자동 추출합니다.

    네이밍 규칙 {부서}_{문서명}_{버전}.pdf를 따르는 파일명을 파싱합니다.
    예: HR_취업규칙_v1.0.pdf → department=HR, doc_name=취업규칙, version=v1.0

    Args:
        pdf_path: 메타데이터를 추출할 PDF 파일 경로 (또는 파일명).

    Returns:
        메타데이터 딕셔너리:
            {
                "department": str,   # 부서 코드 (예: HR, FIN)
                "doc_name": str,     # 문서명 (예: 취업규칙)
                "version": str,      # 버전 (예: v1.0)
                "source": str,       # 파일명 (예: HR_취업규칙_v1.0.pdf)
            }
        네이밍 규칙에 맞지 않으면 각 필드를 "unknown"으로 채워 반환합니다.

    Raises:
        없음. 파싱 실패 시 unknown 값으로 반환합니다.
    """
    # --- Input ---
    filename = Path(pdf_path).name
    stem = Path(pdf_path).stem  # 확장자 제외 파일명

    # --- Process ---
    # 네이밍 규칙: {부서}_{문서명}_{버전}
    # 버전 패턴: v로 시작하는 마지막 세그먼트
    parts = stem.split("_")

    if len(parts) >= 3:
        department = parts[0]
        version_candidate = parts[-1]

        # 버전 패턴 검사: v + 숫자 + 점 + 숫자 (예: v1.0, v2.1)
        if re.match(r"^v\d+(\.\d+)*$", version_candidate):
            version = version_candidate
            doc_name = "_".join(parts[1:-1])
        else:
            # 버전 패턴 불일치 시
            version = "unknown"
            doc_name = "_".join(parts[1:])
    elif len(parts) == 2:
        department = parts[0]
        doc_name = parts[1]
        version = "unknown"
    elif len(parts) == 1:
        department = parts[0]
        doc_name = "unknown"
        version = "unknown"
    else:
        department = "unknown"
        doc_name = "unknown"
        version = "unknown"

    metadata = {
        "department": department,
        "doc_name": doc_name,
        "version": version,
        "source": filename,
    }

    # --- Output ---
    return metadata


def _table_to_markdown(table: list[list]) -> str:
    """pdfplumber가 반환한 표 데이터를 Markdown 표 형식으로 변환합니다.

    None 셀은 빈 문자열로 처리하고, 헤더 행 아래에 구분선을 삽입합니다.

    Args:
        table: pdfplumber.extract_tables()가 반환한 2D 리스트.

    Returns:
        Markdown 표 형식 문자열. 빈 표이면 빈 문자열을 반환합니다.
    """
    # --- Input ---
    if not table or not table[0]:
        return ""

    # --- Process ---
    rows: list[str] = []
    for i, row in enumerate(table):
        # None 셀을 빈 문자열로 변환, 줄바꿈 제거
        cells = [str(cell).replace("\n", " ").strip() if cell is not None else "" for cell in row]
        rows.append("| " + " | ".join(cells) + " |")

        # 헤더 행 다음에 구분선 삽입
        if i == 0:
            separator = "|" + "|".join([" --- " for _ in row]) + "|"
            rows.append(separator)

    # --- Output ---
    return "\n".join(rows)
