"""문서 수집 모듈.

지정된 디렉토리에서 지원 형식의 문서 파일을 수집하고
파일별 기본 메타데이터를 추출합니다.
"""

import os
import sys
from pathlib import Path
from datetime import datetime


# 지원 파일 확장자 (PDF는 추출 처리를 CH06에서 담당)
SUPPORTED_EXTENSIONS: set[str] = {".txt", ".md"}
PDF_EXTENSIONS: set[str] = {".pdf"}


def scan_directory(directory: str) -> list[dict]:
    """지정 디렉토리에서 지원 형식의 파일을 재귀적으로 수집합니다.

    Args:
        directory: 스캔할 디렉토리 경로 (절대 또는 상대 경로)

    Returns:
        파일 정보 딕셔너리 리스트. 각 항목은 아래 키를 포함합니다:
        - file_name: 파일명 (확장자 포함)
        - file_path: 절대 경로
        - extension: 파일 확장자 (소문자)
        - size_bytes: 파일 크기 (바이트)
        - modified_at: 최종 수정 시각 (ISO 8601 형식)
        - is_supported: 전처리 지원 여부

    Raises:
        FileNotFoundError: 디렉토리가 존재하지 않을 경우
        NotADirectoryError: 경로가 디렉토리가 아닐 경우
    """

    # --- Input ---
    dir_path = Path(directory)

    if not dir_path.exists():
        print(f"오류: 디렉토리를 찾을 수 없습니다 - {directory}")
        print("디렉토리 경로를 확인하십시오.")
        sys.exit(1)

    if not dir_path.is_dir():
        print(f"오류: 경로가 디렉토리가 아닙니다 - {directory}")
        sys.exit(1)

    # --- Process ---
    collected_files: list[dict] = []

    for file_path in dir_path.rglob("*"):
        if not file_path.is_file():
            continue

        ext = file_path.suffix.lower()
        all_extensions = SUPPORTED_EXTENSIONS | PDF_EXTENSIONS

        if ext not in all_extensions:
            continue

        stat = file_path.stat()
        modified_at = datetime.fromtimestamp(stat.st_mtime).isoformat()

        file_info = {
            "file_name": file_path.name,
            "file_path": str(file_path.absolute()),
            "extension": ext,
            "size_bytes": stat.st_size,
            "modified_at": modified_at,
            "is_supported": ext in SUPPORTED_EXTENSIONS,
        }
        collected_files.append(file_info)

    # 파일명 기준 정렬
    collected_files.sort(key=lambda x: x["file_name"])

    # --- Output ---
    return collected_files


def print_collection_report(files: list[dict]) -> None:
    """수집된 파일 목록과 통계를 터미널에 출력합니다.

    Args:
        files: scan_directory() 반환값과 동일한 형식의 파일 정보 리스트
    """

    # --- Input ---
    total = len(files)
    supported = sum(1 for f in files if f["is_supported"])
    pdf_count = sum(1 for f in files if f["extension"] == ".pdf")
    total_size = sum(f["size_bytes"] for f in files)

    # --- Process ---
    print("=" * 60)
    print("문서 수집 결과 리포트")
    print("=" * 60)
    print(f"전체 파일 수: {total}개")
    print(f"  - 전처리 가능 (.txt/.md): {supported}개")
    print(f"  - PDF (CH06에서 처리):    {pdf_count}개")
    print(f"전체 크기: {total_size / 1024:.1f} KB")
    print()

    print("{:<35} {:>8} {:>12}".format("파일명", "크기(KB)", "지원 여부"))
    print("-" * 60)

    for file_info in files:
        size_kb = file_info["size_bytes"] / 1024
        support_label = "가능" if file_info["is_supported"] else "CH06 처리"
        print("{:<35} {:>8.1f} {:>12}".format(
            file_info["file_name"][:35],
            size_kb,
            support_label
        ))

    print("=" * 60)

    # --- Output ---
    # (화면 출력 전용 함수, 반환값 없음)


def load_file_content(file_path: str) -> str:
    """텍스트 파일의 내용을 읽어 문자열로 반환합니다.

    Args:
        file_path: 읽을 파일의 절대 경로

    Returns:
        파일 전체 내용 문자열

    Raises:
        FileNotFoundError: 파일이 존재하지 않을 경우
        UnicodeDecodeError: 파일 인코딩이 맞지 않을 경우
    """

    # --- Input ---
    path = Path(file_path)

    if not path.exists():
        print(f"오류: 파일을 찾을 수 없습니다 - {file_path}")
        sys.exit(1)

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        print(f"오류: 지원하지 않는 파일 형식입니다 - {path.suffix}")
        print(f"지원 형식: {', '.join(SUPPORTED_EXTENSIONS)}")
        sys.exit(1)

    # --- Process ---
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        # UTF-8 실패 시 EUC-KR 시도 (구형 한국어 문서)
        with open(path, encoding="euc-kr", errors="replace") as f:
            content = f.read()

    # --- Output ---
    return content


if __name__ == "__main__":
    # 독립 실행 시: 현재 디렉토리의 data/sample_docs 폴더를 스캔
    base_dir = Path(__file__).parent.parent
    sample_dir = base_dir / "data" / "sample_docs"

    print(f"스캔 경로: {sample_dir}")
    print()

    files = scan_directory(str(sample_dir))
    print_collection_report(files)
