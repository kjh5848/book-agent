"""
CH06 VectorDB 구축 파이프라인 메인 오케스트레이터.

Step 1 (Python 파싱) → Step 2 (Vision LLM 파싱) → Step 3 (임베딩 + ChromaDB 저장)
세 단계를 순서대로 또는 선택적으로 실행합니다.

실행 예시:
    # 전체 파이프라인 실행
    python src/main.py

    # Step 1만 실행 (Python 파싱 테스트)
    python src/main.py --step 1

    # Step 1 + Step 3 실행 (Vision LLM 없이)
    python src/main.py --step 1 --step 3

    # Vision LLM URL 변경
    python src/main.py --ollama-url http://192.168.1.10:11434

    # 문서 디렉토리 변경
    python src/main.py --docs-dir ./custom_docs
"""

import argparse
import sys
import time
from pathlib import Path

# src/ 디렉토리를 파이썬 경로에 추가 (모듈 임포트 지원)
sys.path.insert(0, str(Path(__file__).parent))

from chunker import chunk_all_documents, DEFAULT_CHUNK_SIZE, DEFAULT_OVERLAP
from extractor import extract_all_from_directory
from store import (
    DEFAULT_CHROMA_DIR,
    DEFAULT_COLLECTION_NAME,
    DEFAULT_EMBEDDING_MODEL,
    store_chunks_to_chroma,
)
from vision_extractor import DEFAULT_OLLAMA_URL, DEFAULT_VISION_MODEL, extract_with_vision

# 기본 경로 설정
BASE_DIR = Path(__file__).parent.parent
DEFAULT_DOCS_DIR = str(BASE_DIR / "data" / "docs")
DEFAULT_PAGES_DIR = str(BASE_DIR / "data" / "markdown")


# =====================================================================
# === INPUT ===
# docs_dir: 문서 디렉토리 경로 (data/docs/)
# steps: 실행할 Step 번호 리스트 ([1], [2], [3], [1,2,3])
# ollama_url: Vision LLM Ollama 서버 URL
# =====================================================================


def step1_python_parsing(docs_dir: str) -> list[dict]:
    """Step 1: Python 라이브러리로 문서 텍스트를 추출합니다.

    pypdf, python-docx, openpyxl을 사용하여 docs_dir 내의 모든
    PDF, DOCX, XLSX 파일에서 텍스트를 추출합니다.

    Python 파싱의 한계:
    - 이미지 기반 PDF: 텍스트를 거의 추출하지 못합니다.
    - 복잡한 다단 레이아웃: 텍스트 순서가 뒤섞일 수 있습니다.
    - 표 안의 이미지: 추출 불가합니다.
    이러한 한계는 Step 2(Vision LLM)에서 보완합니다.

    Args:
        docs_dir: 문서 파일이 저장된 디렉토리 경로

    Returns:
        문서 추출 결과 딕셔너리 리스트
    """
    print("\n" + "=" * 60)
    print("Step 1: Python 파싱 — 형식별 텍스트 추출")
    print("=" * 60)
    print(f"문서 디렉토리: {docs_dir}\n")

    # === PROCESS ===
    start_time = time.time()
    results = extract_all_from_directory(docs_dir)
    elapsed = time.time() - start_time

    # === OUTPUT ===
    print(f"\nStep 1 완료: {len(results)}개 문서 추출 ({elapsed:.1f}초)")

    # 추출 결과 요약 출력
    print("\n[추출 결과 요약]")
    for r in results:
        text_length = len(r["full_text"])
        page_count = len(r["pages"])
        print(f"  {r['file_name']}: {page_count}페이지, {text_length}자")

    return results


def step2_vision_parsing(
    docs_dir: str,
    pages_dir: str,
    ollama_url: str,
    vision_model: str,
) -> list[dict]:
    """Step 2: Vision LLM(LLaVA)으로 PDF 문서를 심층 분석합니다.

    docs_dir 내의 PDF 파일만 대상으로 Vision LLM 분석을 수행합니다.
    각 페이지를 PNG 이미지로 변환한 후 LLaVA 모델로 분석하여
    텍스트, 메타데이터(제목, 부서), 이미지 캡션을 추출합니다.

    Vision LLM이 실행되지 않은 경우 Python 파싱으로 자동 폴백합니다.

    Args:
        docs_dir: 문서 파일이 저장된 디렉토리 경로
        pages_dir: PDF 페이지 이미지를 저장할 디렉토리 경로
        ollama_url: Ollama 서버 URL
        vision_model: Vision LLM 모델명 (예: llava:13b)

    Returns:
        Vision LLM 분석 결과 딕셔너리 리스트
        (폴백 시 Python 파싱 결과 포함)
    """
    print("\n" + "=" * 60)
    print("Step 2: Vision LLM 파싱 — PDF 이미지 분석")
    print("=" * 60)
    print(f"Ollama URL: {ollama_url}")
    print(f"Vision 모델: {vision_model}")
    print(f"페이지 이미지 저장 경로: {pages_dir}\n")

    # === PROCESS ===
    docs_path = Path(docs_dir)
    pdf_files = sorted(docs_path.rglob("*.pdf"))

    if not pdf_files:
        print("PDF 파일이 없습니다. Step 2를 건너뜁니다.")
        return []

    print(f"총 {len(pdf_files)}개 PDF 파일을 Vision LLM으로 분석합니다.")

    start_time = time.time()
    results = []
    for pdf_path in pdf_files:
        result = extract_with_vision(
            pdf_path=pdf_path,
            pages_output_dir=pages_dir,
            ollama_url=ollama_url,
            vision_model=vision_model,
        )
        results.append(result)

    elapsed = time.time() - start_time

    # === OUTPUT ===
    print(f"\nStep 2 완료: {len(results)}개 PDF 분석 ({elapsed:.1f}초)")

    # 분석 방법 요약
    vision_count = sum(1 for r in results if r.get("parse_method") == "vision")
    fallback_count = len(results) - vision_count
    print(f"  Vision LLM 성공: {vision_count}개")
    print(f"  Python 폴백: {fallback_count}개")

    return results


def step3_embed_and_store(
    python_results: list[dict],
    vision_results: list[dict],
    chroma_dir: str,
    collection_name: str,
    embedding_model_name: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> dict:
    """Step 3: 추출 결과를 청킹 후 임베딩하여 ChromaDB에 저장합니다.

    Step 1(Python 파싱)과 Step 2(Vision LLM 파싱) 결과를 통합하여
    중복 없이 최선의 파싱 결과를 사용합니다.
    - PDF: Vision LLM 결과 우선 (폴백 포함)
    - DOCX, XLSX: Python 파싱 결과 사용

    청킹 후 ko-sroberta-multitask 임베딩 모델로 벡터를 생성하고
    ChromaDB에 영속 저장합니다.

    Args:
        python_results: Step 1 추출 결과 리스트
        vision_results: Step 2 추출 결과 리스트 (비어 있을 수 있음)
        chroma_dir: ChromaDB 저장 디렉토리 경로
        collection_name: ChromaDB 컬렉션명
        embedding_model_name: 임베딩 모델 HuggingFace ID
        chunk_size: 텍스트 청크 최대 문자 수
        overlap: 청크 간 오버랩 문자 수

    Returns:
        store_chunks_to_chroma() 반환값 딕셔너리
    """
    print("\n" + "=" * 60)
    print("Step 3: 임베딩 + ChromaDB 저장")
    print("=" * 60)
    print(f"청크 크기: {chunk_size}자, 오버랩: {overlap}자")
    print(f"임베딩 모델: {embedding_model_name}")
    print(f"ChromaDB 저장 경로: {chroma_dir}\n")

    # === PROCESS: 파싱 결과 통합 ===
    # Vision LLM 분석한 PDF 파일명 세트
    vision_file_names = {r["file_name"] for r in vision_results}

    # Python 결과에서 PDF는 Vision 결과로 대체, DOCX/XLSX는 그대로 사용
    combined_results = []
    for r in python_results:
        if r["file_type"] == "pdf" and r["file_name"] in vision_file_names:
            # Vision 결과로 대체 (더 풍부한 정보 포함)
            pass
        else:
            combined_results.append(r)

    combined_results.extend(vision_results)

    print(f"통합 결과: {len(combined_results)}개 문서")

    # === PROCESS: 청킹 ===
    print("\n청킹 중...")
    all_chunks = chunk_all_documents(combined_results, chunk_size, overlap)

    if not all_chunks:
        print("생성된 청크가 없습니다. 문서가 비어 있는지 확인하십시오.")
        sys.exit(1)

    # === PROCESS: ChromaDB 저장 ===
    start_time = time.time()
    store_result = store_chunks_to_chroma(
        chunks=all_chunks,
        chroma_dir=chroma_dir,
        collection_name=collection_name,
        embedding_model_name=embedding_model_name,
    )
    elapsed = time.time() - start_time

    # === OUTPUT ===
    print(f"\nStep 3 완료 ({elapsed:.1f}초)")
    print(f"  처리 청크 수: {store_result['total_chunks']}개")
    print(f"  컬렉션 총 문서 수: {store_result['collection_count']}개")
    print(f"  ChromaDB 위치: {store_result['chroma_dir']}")

    return store_result


def parse_arguments() -> argparse.Namespace:
    """CLI 인수를 파싱합니다.

    Returns:
        파싱된 인수 네임스페이스
    """
    parser = argparse.ArgumentParser(
        description="CH06 VectorDB 구축 파이프라인 — 문서를 파싱, 청킹, 임베딩하여 ChromaDB에 저장합니다.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
실행 예시:
  python src/main.py                     # 전체 파이프라인 (Step 1+2+3)
  python src/main.py --step 1            # Python 파싱만 테스트
  python src/main.py --step 1 3          # Vision LLM 없이 (Step 1 + Step 3)
  python src/main.py --step 2 3          # Vision LLM 분석 + 저장
  python src/main.py --no-vision         # Vision LLM 비활성화 (Step 1 + Step 3)
        """,
    )

    parser.add_argument(
        "--step",
        type=int,
        nargs="+",
        choices=[1, 2, 3],
        default=[1, 2, 3],
        help="실행할 Step 번호 (기본값: 1 2 3 — 전체 실행)",
    )
    parser.add_argument(
        "--docs-dir",
        type=str,
        default=DEFAULT_DOCS_DIR,
        help=f"문서 디렉토리 경로 (기본값: {DEFAULT_DOCS_DIR})",
    )
    parser.add_argument(
        "--pages-dir",
        type=str,
        default=DEFAULT_PAGES_DIR,
        help=f"페이지 이미지 저장 경로 (기본값: {DEFAULT_PAGES_DIR})",
    )
    parser.add_argument(
        "--chroma-dir",
        type=str,
        default=str(BASE_DIR / "data" / "chroma_db"),
        help="ChromaDB 저장 경로",
    )
    parser.add_argument(
        "--collection",
        type=str,
        default=DEFAULT_COLLECTION_NAME,
        help=f"ChromaDB 컬렉션명 (기본값: {DEFAULT_COLLECTION_NAME})",
    )
    parser.add_argument(
        "--embedding-model",
        type=str,
        default=DEFAULT_EMBEDDING_MODEL,
        help=f"임베딩 모델 HuggingFace ID (기본값: {DEFAULT_EMBEDDING_MODEL})",
    )
    parser.add_argument(
        "--ollama-url",
        type=str,
        default=DEFAULT_OLLAMA_URL,
        help=f"Ollama 서버 URL (기본값: {DEFAULT_OLLAMA_URL})",
    )
    parser.add_argument(
        "--vision-model",
        type=str,
        default=DEFAULT_VISION_MODEL,
        help=f"Vision LLM 모델명 (기본값: {DEFAULT_VISION_MODEL})",
    )
    parser.add_argument(
        "--no-vision",
        action="store_true",
        help="Vision LLM 비활성화 (Step 2 건너뜀, Step 1+3만 실행)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help=f"텍스트 청크 최대 문자 수 (기본값: {DEFAULT_CHUNK_SIZE})",
    )
    parser.add_argument(
        "--overlap",
        type=int,
        default=DEFAULT_OVERLAP,
        help=f"청크 간 오버랩 문자 수 (기본값: {DEFAULT_OVERLAP})",
    )

    return parser.parse_args()


def main() -> None:
    """CH06 VectorDB 구축 파이프라인 메인 진입점.

    1. argparse로 실행 옵션 파싱
    2. 선택된 Step 순서대로 실행
    3. 최종 결과 요약 출력
    """
    args = parse_arguments()

    # --no-vision 플래그 처리: Step 2를 제외한 [1, 3]으로 변경
    if args.no_vision and 2 in args.step:
        args.step = [s for s in args.step if s != 2]
        print("[Vision LLM 비활성화] Step 2를 건너뜁니다.")

    steps_to_run = sorted(set(args.step))

    print("\n" + "=" * 60)
    print("커넥트HR VectorDB 구축 파이프라인 시작")
    print("=" * 60)
    print(f"실행 Step: {steps_to_run}")
    print(f"문서 디렉토리: {args.docs_dir}")

    pipeline_start = time.time()

    python_results: list[dict] = []
    vision_results: list[dict] = []

    # === PROCESS: Step 1 — Python 파싱 ===
    if 1 in steps_to_run:
        python_results = step1_python_parsing(docs_dir=args.docs_dir)

    # === PROCESS: Step 2 — Vision LLM 파싱 ===
    if 2 in steps_to_run:
        vision_results = step2_vision_parsing(
            docs_dir=args.docs_dir,
            pages_dir=args.pages_dir,
            ollama_url=args.ollama_url,
            vision_model=args.vision_model,
        )

    # === PROCESS: Step 3 — 임베딩 + ChromaDB 저장 ===
    if 3 in steps_to_run:
        # Step 1 결과 없이 Step 3만 실행하려면 파싱 먼저 수행
        if not python_results and not vision_results:
            print("\nStep 3 실행 전 문서 파싱이 필요합니다. Step 1을 자동으로 실행합니다.")
            python_results = step1_python_parsing(docs_dir=args.docs_dir)

        step3_embed_and_store(
            python_results=python_results,
            vision_results=vision_results,
            chroma_dir=args.chroma_dir,
            collection_name=args.collection,
            embedding_model_name=args.embedding_model,
            chunk_size=args.chunk_size,
            overlap=args.overlap,
        )

    # === OUTPUT: 파이프라인 완료 요약 ===
    total_elapsed = time.time() - pipeline_start
    print("\n" + "=" * 60)
    print(f"파이프라인 완료! (총 소요 시간: {total_elapsed:.1f}초)")
    print("=" * 60)

    if 3 in steps_to_run:
        print("\n다음 단계: CLI 검색으로 색인 품질을 검증하십시오.")
        print("  python src/cli_search.py")
        print("  python src/cli_search.py --query '연차 사용 규정'")


if __name__ == "__main__":
    main()
