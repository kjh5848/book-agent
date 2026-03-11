"""문서 표준화 파이프라인 진입점.

사내 문서를 수집 → 전처리 → 정규화 → 메타데이터 저장 순서로
전체 파이프라인을 실행합니다.

CH05: 사내 문서 표준화 (AI 업무 비서 구축 - RAG + MCP 실전 가이드)
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트를 sys.path에 추가 (상대 임포트 지원)
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

load_dotenv()

from collector import scan_directory, load_file_content, print_collection_report
from preprocessor import preprocess
from normalizer import normalize_to_markdown, save_normalized_file
from metadata_manager import (
    build_metadata,
    save_metadata,
    load_all_metadata,
    print_metadata_summary,
)

# --- 환경 변수 설정 ---
DOCS_DIR = os.getenv("DOCS_DIR", str(PROJECT_ROOT / "data" / "sample_docs"))
NORMALIZED_OUTPUT_DIR = os.getenv(
    "NORMALIZED_OUTPUT_DIR",
    str(PROJECT_ROOT / "outputs" / "markdown"),
)
METADATA_OUTPUT_DIR = os.getenv(
    "METADATA_OUTPUT_DIR",
    str(PROJECT_ROOT / "outputs" / "metadata"),
)


def run_pipeline(docs_dir: str) -> dict:
    """문서 표준화 전체 파이프라인을 실행합니다.

    실행 순서:
    1. 문서 수집 (collector)
    2. 전처리 (preprocessor)
    3. 정규화 → Markdown 저장 (normalizer)
    4. 메타데이터 추출 및 저장 (metadata_manager)

    Args:
        docs_dir: 문서가 있는 디렉토리 경로

    Returns:
        파이프라인 실행 결과 요약 딕셔너리:
        - total_files: 수집된 전체 파일 수
        - processed_files: 전처리 완료 파일 수
        - normalized_files: 정규화 완료 파일 수
        - metadata_files: 메타데이터 생성 파일 수
        - output_dirs: 출력 디렉토리 경로 목록
    """

    print("=" * 60)
    print("CH05 사내 문서 표준화 파이프라인 시작")
    print("=" * 60)
    print()

    # ============================================================
    # Step 1: 문서 수집
    # ============================================================
    print("[Step 1] 문서 수집")
    print(f"  스캔 경로: {docs_dir}")

    # --- Input ---
    files = scan_directory(docs_dir)
    print_collection_report(files)

    # 전처리 가능한 파일만 필터링 (.txt, .md)
    supported_files = [f for f in files if f["is_supported"]]
    pdf_files = [f for f in files if f["extension"] == ".pdf"]

    if pdf_files:
        print(f"  참고: PDF {len(pdf_files)}개는 CH06에서 처리됩니다.")
        print()

    if not supported_files:
        print("오류: 전처리 가능한 파일(.txt, .md)이 없습니다.")
        print(f"디렉토리를 확인하십시오: {docs_dir}")
        sys.exit(1)

    print(f"  전처리 대상: {len(supported_files)}개 파일\n")

    # ============================================================
    # Step 2 & 3: 전처리 + 정규화
    # ============================================================
    print("[Step 2 & 3] 전처리 및 Markdown 정규화")

    normalized_count = 0
    processed_results: list[dict] = []

    for file_info in supported_files:
        file_path = file_info["file_path"]
        file_name = file_info["file_name"]

        print(f"  처리 중: {file_name}")

        # --- Input ---
        raw_text = load_file_content(file_path)

        # --- Process: 전처리 ---
        cleaned_text = preprocess(raw_text)

        # --- Process: 정규화 ---
        markdown_text = normalize_to_markdown(cleaned_text, file_name)

        # --- Output: Markdown 저장 ---
        normalized_path = save_normalized_file(
            markdown_text, file_name, NORMALIZED_OUTPUT_DIR
        )

        normalized_count += 1
        processed_results.append({
            "file_info": file_info,
            "cleaned_text": cleaned_text,
            "normalized_path": normalized_path,
        })

    print()

    # ============================================================
    # Step 4: 메타데이터 생성 및 저장
    # ============================================================
    print("[Step 4] 메타데이터 생성")

    metadata_count = 0

    for result in processed_results:
        file_info = result["file_info"]
        file_name = file_info["file_name"]

        print(f"  처리 중: {file_name}")

        # --- Input ---
        # --- Process ---
        metadata = build_metadata(
            file_path=file_info["file_path"],
            text=result["cleaned_text"],
            normalized_path=result["normalized_path"],
        )

        # --- Output ---
        save_metadata(metadata, METADATA_OUTPUT_DIR)
        metadata_count += 1

    print()

    # ============================================================
    # 완료 요약
    # ============================================================
    summary = {
        "total_files": len(files),
        "processed_files": len(supported_files),
        "normalized_files": normalized_count,
        "metadata_files": metadata_count,
        "output_dirs": {
            "markdown": NORMALIZED_OUTPUT_DIR,
            "metadata": METADATA_OUTPUT_DIR,
        },
    }

    print("=" * 60)
    print("파이프라인 완료")
    print("=" * 60)
    print(f"  수집 파일: {summary['total_files']}개")
    print(f"  전처리 완료: {summary['processed_files']}개")
    print(f"  정규화 완료 (Markdown): {summary['normalized_files']}개")
    print(f"  메타데이터 생성: {summary['metadata_files']}개")
    print()
    print(f"  출력 경로:")
    print(f"    - Markdown: {NORMALIZED_OUTPUT_DIR}")
    print(f"    - 메타데이터: {METADATA_OUTPUT_DIR}")

    # 메타데이터 요약 출력
    print()
    all_metadata = load_all_metadata(METADATA_OUTPUT_DIR)
    print_metadata_summary(all_metadata)

    return summary


if __name__ == "__main__":
    # 환경 변수 체크
    docs_dir = DOCS_DIR

    # 커맨드라인 인자로 경로 지정 가능
    if len(sys.argv) > 1:
        docs_dir = sys.argv[1]

    docs_path = Path(docs_dir)
    if not docs_path.exists():
        print(f"오류: 문서 디렉토리를 찾을 수 없습니다 - {docs_dir}")
        print(".env 파일의 DOCS_DIR 환경 변수를 확인하십시오.")
        sys.exit(1)

    result = run_pipeline(docs_dir)
