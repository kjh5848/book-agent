"""문서 텍스트 추출 모듈.

TXT, PDF 파일에서 텍스트를 추출합니다.
PyMuPDF를 1차 시도하고, 실패 시 pdfplumber로 대체합니다.
"""

import sys
from pathlib import Path
from typing import Optional


def extract_from_txt(file_path: str) -> dict[str, str]:
    """텍스트 파일에서 내용을 읽어 반환합니다.

    Args:
        file_path: 텍스트 파일의 경로 (절대 또는 상대)

    Returns:
        추출 결과 딕셔너리 {"content": str, "source": str, "doc_type": str}

    Raises:
        FileNotFoundError: 파일이 존재하지 않을 경우
        UnicodeDecodeError: 파일 인코딩이 UTF-8이 아닐 경우
    """

    # --- Input ---
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(
            f"파일을 찾을 수 없습니다: {file_path}\n"
            "경로가 올바른지 확인하십시오."
        )

    # --- Process ---
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # UTF-8 실패 시 CP949(한국어 Windows 인코딩) 시도
        try:
            content = path.read_text(encoding="cp949")
            print(f"  [경고] UTF-8 디코딩 실패, CP949로 재시도: {path.name}")
        except UnicodeDecodeError as err:
            raise UnicodeDecodeError(
                "utf-8",
                b"",
                0,
                1,
                f"파일 인코딩을 읽을 수 없습니다: {file_path}\n"
                "UTF-8 또는 CP949 형식으로 저장된 파일만 지원합니다.",
            ) from err

    content = content.strip()
    if not content:
        print(f"  [경고] 빈 파일입니다: {path.name}")

    # --- Output ---
    return {
        "content": content,
        "source": path.name,
        "doc_type": "txt",
    }


def extract_from_pdf(file_path: str) -> dict[str, str]:
    """PDF 파일에서 텍스트를 추출합니다.

    PyMuPDF(fitz)를 1차 시도합니다.
    PyMuPDF가 없거나 추출 결과가 비어있으면 pdfplumber로 대체합니다.

    Args:
        file_path: PDF 파일의 경로

    Returns:
        추출 결과 딕셔너리 {"content": str, "source": str, "doc_type": str}

    Raises:
        FileNotFoundError: 파일이 존재하지 않을 경우
        RuntimeError: 두 라이브러리 모두 추출에 실패할 경우
    """

    # --- Input ---
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(
            f"PDF 파일을 찾을 수 없습니다: {file_path}\n"
            "경로가 올바른지 확인하십시오."
        )

    content = ""
    method_used = ""

    # --- Process ---
    # 1차 시도: PyMuPDF
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(file_path)
        pages_text: list[str] = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            if page_text.strip():
                pages_text.append(page_text)
        doc.close()
        content = "\n".join(pages_text).strip()
        method_used = "PyMuPDF"
    except ImportError:
        print(f"  [정보] PyMuPDF 미설치. pdfplumber로 대체합니다: {path.name}")
    except Exception as e:
        print(f"  [경고] PyMuPDF 추출 실패 ({e}). pdfplumber로 대체합니다: {path.name}")

    # 2차 시도: pdfplumber (PyMuPDF 실패 또는 결과 없을 때)
    if not content:
        try:
            import pdfplumber

            with pdfplumber.open(file_path) as pdf:
                pages_text = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        pages_text.append(page_text)
            content = "\n".join(pages_text).strip()
            method_used = "pdfplumber"
        except ImportError:
            raise RuntimeError(
                f"PDF 추출 라이브러리가 없습니다: {file_path}\n"
                "다음 명령어로 설치하십시오: pip install pymupdf pdfplumber"
            )
        except Exception as e:
            raise RuntimeError(
                f"PDF 텍스트 추출에 실패했습니다: {file_path}\n"
                f"오류: {e}"
            ) from e

    if not content:
        print(f"  [경고] 텍스트를 추출할 수 없는 PDF입니다: {path.name}")
        print("  이미지 기반 PDF의 경우 OCR 처리가 필요합니다.")

    if method_used:
        print(f"  [{method_used}] 추출 완료: {path.name} ({len(content)}자)")

    # --- Output ---
    return {
        "content": content,
        "source": path.name,
        "doc_type": "pdf",
    }


def extract_all(docs_dir: str) -> list[dict[str, str]]:
    """디렉토리 내의 모든 TXT, PDF 파일을 추출합니다.

    지원 형식: .txt, .pdf
    지원하지 않는 형식은 건너뜁니다.

    Args:
        docs_dir: 문서가 있는 디렉토리 경로

    Returns:
        각 문서의 추출 결과 딕셔너리 리스트.
        빈 리스트가 반환되면 대상 파일이 없는 것입니다.

    Raises:
        FileNotFoundError: 디렉토리가 존재하지 않을 경우
    """

    # --- Input ---
    dir_path = Path(docs_dir)
    if not dir_path.exists():
        raise FileNotFoundError(
            f"디렉토리를 찾을 수 없습니다: {docs_dir}\n"
            "경로가 올바른지 확인하십시오."
        )
    if not dir_path.is_dir():
        raise FileNotFoundError(
            f"디렉토리가 아닙니다: {docs_dir}\n"
            "디렉토리 경로를 입력하십시오."
        )

    # --- Process ---
    results: list[dict[str, str]] = []
    supported_extensions = {".txt", ".pdf"}

    all_files = sorted(dir_path.iterdir())
    target_files = [f for f in all_files if f.is_file() and f.suffix.lower() in supported_extensions]

    if not target_files:
        print(f"  [경고] {docs_dir} 에서 지원 형식 파일을 찾지 못했습니다.")
        print(f"  지원 형식: {', '.join(supported_extensions)}")
        return results

    print(f"  총 {len(target_files)}개 파일 추출 시작...")

    for file_path in target_files:
        ext = file_path.suffix.lower()
        try:
            if ext == ".txt":
                doc = extract_from_txt(str(file_path))
            elif ext == ".pdf":
                doc = extract_from_pdf(str(file_path))
            else:
                continue

            if doc["content"]:
                results.append(doc)
                print(f"  완료: {file_path.name} ({len(doc['content'])}자)")
            else:
                print(f"  건너뜀 (빈 내용): {file_path.name}")

        except (FileNotFoundError, RuntimeError) as e:
            print(f"  [오류] {file_path.name}: {e}")
            continue

    # --- Output ---
    print(f"  추출 완료: {len(results)}/{len(target_files)}개 성공")
    return results


if __name__ == "__main__":
    base_dir = Path(__file__).parent.parent
    sample_dir = base_dir / "data" / "sample_docs"

    print("=== 문서 추출 테스트 ===")
    docs = extract_all(str(sample_dir))

    if not docs:
        print("추출된 문서가 없습니다.")
        sys.exit(1)

    for doc in docs:
        print(f"\n파일: {doc['source']} (유형: {doc['doc_type']})")
        print(f"내용 미리보기: {doc['content'][:100]}...")
