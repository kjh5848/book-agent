"""
CH06 벡터 DB 구축 — 메인 파이프라인.

PDF 파일을 파싱하여 청킹, 임베딩, ChromaDB 저장, 검색까지
전 과정을 순서대로 실행합니다.

두 가지 파싱 모드를 지원합니다:
    규칙 기반 (기본): pdfplumber로 텍스트 추출 → fixed_size_chunk
    Vision LLM (--vision): PDF → 이미지 → LLM → Markdown → markdown_chunk

실행 방법:
    python src/main.py            # 규칙 기반 파싱
    python src/main.py --vision   # Vision LLM 파싱

사전 준비:
    1. Ollama 서버 실행: ollama serve
    2. 임베딩 모델 준비: ollama pull nomic-embed-text
    3. 환경 변수 설정: cp .env.example .env

데이터:
    data/docs/ 폴더에 부서별 PDF 파일이 포함되어 있습니다.
    (HR_취업규칙_v1.0.pdf, HR_정보보안서약서.pdf, OPS_신규서비스_런칭전략.pdf)
"""

import argparse
import glob
import os
import sys

from dotenv import load_dotenv

# 프로젝트 루트를 sys.path에 추가 (src/ 내부에서 임포트 가능하도록)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.chunker import compare_strategies, fixed_size_chunk, markdown_chunk
from src.embedder import embed_single, embed_texts, get_embedding_model
from src.extractor import (
    extract_text_pdfplumber,
    is_complex_layout,
    parse_filename_metadata,
)
from src.store import (
    add_documents,
    create_collection,
    get_client,
    get_collection_stats,
    search,
)
from src.vision_extractor import extract_pdf_to_markdown

load_dotenv()


def run_pipeline(pdf_paths: list[str], use_vision: bool = False) -> None:
    """PDF 파일 목록을 받아 벡터 DB 구축 파이프라인 전체를 실행합니다.

    5단계로 진행됩니다:
        [1/5] PDF 확인   — 파일 존재 여부 및 메타데이터 파싱
        [2/5] 파싱       — pdfplumber(규칙 기반) 또는 Vision LLM
        [3/5] 청킹       — fixed_size_chunk 또는 markdown_chunk
        [4/5] 임베딩     — Ollama REST API로 각 청크를 벡터로 변환
        [5/5] ChromaDB   — 저장 + 테스트 검색 3회 실행

    Args:
        pdf_paths: 처리할 PDF 파일 경로 리스트.
        use_vision: True이면 Vision LLM 파싱 모드를 사용합니다.
                    False이면 pdfplumber 규칙 기반 파싱을 사용합니다.

    Returns:
        None. 모든 진행 상황과 결과를 표준 출력으로 내보냅니다.

    Raises:
        FileNotFoundError: 지정된 PDF 파일이 존재하지 않을 때.
        ConnectionError: Ollama 서버에 연결할 수 없을 때.
        RuntimeError: 파이프라인 실행 중 오류가 발생했을 때.
    """
    mode_label = "Vision LLM" if use_vision else "규칙 기반 (pdfplumber)"
    print("=" * 65)
    print("  CH06 벡터 DB 구축 파이프라인")
    print(f"  파싱 모드: {mode_label}")
    print("=" * 65)

    # ------------------------------------------------------------------ #
    # [1/5] PDF 확인
    # ------------------------------------------------------------------ #
    print("\n[1/5] PDF 파일 확인 중...")

    # --- Input ---
    for pdf_path in pdf_paths:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(
                f"PDF 파일을 찾을 수 없습니다: {pdf_path}\n"
                "data/docs/ 폴더에 PDF 파일이 있는지 확인하십시오."
            )
        meta = parse_filename_metadata(pdf_path)
        print(
            f"  확인: {os.path.basename(pdf_path)} "
            f"[부서={meta['department']}, 문서명={meta['doc_name']}, 버전={meta['version']}]"
        )

    # --- Output ---
    print(f"  총 {len(pdf_paths)}개 PDF 파일 확인 완료.")

    # ------------------------------------------------------------------ #
    # [2/5] 파싱
    # ------------------------------------------------------------------ #
    print(f"\n[2/5] PDF 파싱 중... (모드: {mode_label})")

    # --- Input ---
    all_pages: list[dict] = []
    markdown_paths: dict[str, str] = {}  # PDF 경로 → Markdown 파일 경로

    # --- Process ---
    if not use_vision:
        # 규칙 기반: pdfplumber로 텍스트 추출
        for pdf_path in pdf_paths:
            pages = extract_text_pdfplumber(pdf_path)
            all_pages.extend(pages)

            table_count = sum(1 for p in pages if p.get("has_table", False))
            print(
                f"  완료: {os.path.basename(pdf_path)} "
                f"→ {len(pages)}페이지 추출 (표 포함 페이지: {table_count}개)"
            )

            # 레이아웃 복잡도 판단
            if pages and is_complex_layout(pages):
                print(
                    f"  [권장] {os.path.basename(pdf_path)}은 복잡한 레이아웃이 감지되었습니다. "
                    "--vision 플래그 사용을 고려하십시오."
                )
            elif not pages:
                print(
                    f"  [경고] {os.path.basename(pdf_path)}에서 텍스트를 추출하지 못했습니다. "
                    "이미지 기반 문서일 수 있으므로 --vision 플래그 사용을 권장합니다."
                )
    else:
        # Vision LLM: PDF → 이미지 → LLM → Markdown
        output_dir = os.path.join(_PROJECT_ROOT, "outputs", "markdown")
        for pdf_path in pdf_paths:
            md_path = extract_pdf_to_markdown(pdf_path, output_dir=output_dir)
            markdown_paths[pdf_path] = md_path

            # Markdown에서 임시 pages 생성 (청킹 비교용)
            with open(md_path, "r", encoding="utf-8") as f:
                md_text = f.read()
            source_name = os.path.basename(pdf_path)
            all_pages.append(
                {
                    "page": 1,
                    "text": md_text,
                    "source": source_name,
                    "has_table": True,
                }
            )

    # --- Output ---
    print(f"  파싱 완료: 총 {len(all_pages)}개 페이지/섹션")

    # ------------------------------------------------------------------ #
    # [3/5] 청킹
    # ------------------------------------------------------------------ #
    print("\n[3/5] 텍스트 청킹 중...")

    # --- Input ---
    chunks: list[dict] = []

    # --- Process ---
    if not use_vision:
        # 규칙 기반: fixed_size_chunk 사용
        chunks = fixed_size_chunk(all_pages, chunk_size=500, overlap=50)
        print(f"  Fixed-size 청킹 완료: {len(chunks)}개 청크 생성")

        # 청킹 전략 비교 출력 (첫 번째 PDF의 Markdown이 있으면 비교, 없으면 단일 출력)
        first_md_path = os.path.join(
            _PROJECT_ROOT, "outputs", "markdown",
            os.path.basename(pdf_paths[0]).replace(".pdf", ".md")
        ) if pdf_paths else ""
        compare_strategies(all_pages, first_md_path)
    else:
        # Vision LLM: markdown_chunk 사용
        for pdf_path in pdf_paths:
            md_path = markdown_paths.get(pdf_path, "")
            if not md_path or not os.path.exists(md_path):
                continue
            with open(md_path, "r", encoding="utf-8") as f:
                md_text = f.read()
            source_name = os.path.basename(pdf_path)
            pdf_chunks = markdown_chunk(md_text, source=source_name, max_chunk_size=500)
            chunks.extend(pdf_chunks)
            print(
                f"  Markdown 청킹: {source_name} → {len(pdf_chunks)}개 청크"
            )
        print(f"  전체 청킹 완료: {len(chunks)}개 청크 생성")

    # --- Output ---

    # ------------------------------------------------------------------ #
    # [4/5] 임베딩
    # ------------------------------------------------------------------ #
    print("\n[4/5] 임베딩 변환 중...")

    # --- Input ---
    embed_model = os.getenv("EMBED_MODEL", "nomic-embed-text")
    model_info = get_embedding_model(embed_model)
    print(f"  모델: {model_info['model']}, 예상 차원: {model_info['dimension']}")

    texts = [chunk["text"] for chunk in chunks]

    # --- Process ---
    embeddings = embed_texts(texts, model_name=embed_model)

    # --- Output ---
    if embeddings:
        actual_dim = len(embeddings[0])
        print(f"  실제 차원: {actual_dim}")

    # ------------------------------------------------------------------ #
    # [5/5] ChromaDB 저장 및 테스트 검색
    # ------------------------------------------------------------------ #
    print("\n[5/5] ChromaDB 저장 및 검색 테스트 중...")

    # --- Input ---
    persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./outputs/chroma_db")
    collection_name = os.getenv("COLLECTION_NAME", "rag_docs")
    # 상대 경로를 프로젝트 루트 기준으로 변환
    if not os.path.isabs(persist_dir):
        persist_dir = os.path.join(_PROJECT_ROOT, persist_dir.lstrip("./"))

    # --- Process ---
    client = get_client(persist_dir=persist_dir)
    collection = create_collection(client, name=collection_name)
    add_documents(collection, chunks, embeddings)

    # 컬렉션 통계 출력
    stats = get_collection_stats(collection)
    print(f"\n  컬렉션 통계:")
    print(f"    총 문서 수: {stats['total']}")
    by_dept = stats.get("by_department", {})
    if by_dept:
        print("    부서별 분포:")
        for dept, count in sorted(by_dept.items()):
            print(f"      {dept}: {count}개")

    # 테스트 검색 3회 실행
    test_queries = [
        ("연차 신청은 어떻게 하나요?", None),
        ("보안 USB 분실하면 어떻게 해야 해?", None),
        ("교육비 지원 한도가 얼마야?", None),
    ]

    print(f"\n  테스트 검색 ({len(test_queries)}회):")
    print("  " + "-" * 60)

    for i, (query, dept_filter) in enumerate(test_queries, start=1):
        filter_label = f"부서={dept_filter}" if dept_filter else "전체"
        print(f"\n  검색 {i}: '{query}' [{filter_label}]")

        query_embedding = embed_single(query, model_name=embed_model)
        results = search(collection, query_embedding=query_embedding, k=3, filter_dept=dept_filter)

        if not results:
            print("    검색 결과가 없습니다.")
            continue

        for rank, result in enumerate(results, start=1):
            meta = result["metadata"]
            source = meta.get("source", "N/A")
            dept = meta.get("department", "N/A")
            distance = result["distance"]
            preview = result["text"][:80].replace("\n", " ")
            print(f"    [{rank}] 거리={distance:.4f} | {source} | 부서={dept}")
            print(f"         {preview}...")

    # --- Output ---
    print("\n" + "=" * 65)
    print("  파이프라인 완료.")
    print(f"  저장 경로: {os.path.abspath(persist_dir)}")
    print("=" * 65)


def main() -> None:
    """argparse로 명령행 인수를 파싱하고 파이프라인을 실행합니다.

    --vision 플래그로 Vision LLM 모드를 선택합니다.
    data/ 폴더에 PDF 파일이 없으면 안내 메시지를 출력하고 종료합니다.

    Returns:
        None.
    """
    # --- Input ---
    parser = argparse.ArgumentParser(
        description="CH06 벡터 DB 구축 파이프라인",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "사용 예시:\n"
            "  python src/main.py             # 규칙 기반 파싱 (기본)\n"
            "  python src/main.py --vision    # Vision LLM 파싱\n"
            "\n"
            "사전 준비:\n"
            "  ollama serve                        # Ollama 서버 실행\n"
            "  ollama pull nomic-embed-text        # 임베딩 모델 준비\n"
        ),
    )
    parser.add_argument(
        "--vision",
        action="store_true",
        help="Vision LLM 모드로 실행합니다. PDF 페이지를 이미지로 변환 후 LLM이 Markdown으로 파싱합니다.",
    )
    args = parser.parse_args()

    # --- Process ---
    docs_dir = os.path.join(_PROJECT_ROOT, "data", "docs")

    # data/docs/ 하위 모든 부서 폴더에서 PDF 파일 자동 탐색
    pdf_files = sorted(glob.glob(os.path.join(docs_dir, "**", "*.pdf"), recursive=True))

    if not pdf_files:
        print("data/docs/ 폴더에 PDF 파일이 없습니다.")
        print(f"  탐색 경로: {docs_dir}")
        sys.exit(1)

    # --- Output ---
    run_pipeline(pdf_files, use_vision=args.vision)


if __name__ == "__main__":
    main()
