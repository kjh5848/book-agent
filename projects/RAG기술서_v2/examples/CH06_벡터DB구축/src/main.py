"""CH06 벡터 DB 구축 메인 실행 파일.

표준화된 사내 문서를 ChromaDB에 저장하고 검색하는 전체 파이프라인을 실행합니다.

파이프라인 단계:
    1단계: 문서 추출 (extractor.py)
    2단계: 청킹 (chunker.py)
    3단계: 임베딩 (embedder.py)
    4단계: ChromaDB 저장 (store.py)
    5단계: 검색 테스트
"""

import os
import sys
import time
from pathlib import Path

# 현재 디렉토리(src/)를 모듈 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

from chunker import Chunk, chunk_document, compare_strategies
from embedder import embed_chunks
from extractor import extract_all
from store import ChromaStore


# .env 파일 로드 (src/ 상위 디렉토리 기준)
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"환경 변수 로드: {env_path}")
else:
    print(f"[정보] .env 파일이 없습니다. 기본값을 사용합니다.")
    print(f"  .env 파일 위치: {env_path}")


# --- 설정 ---
BASE_DIR = Path(__file__).parent.parent
SAMPLE_DOCS_DIR = str(BASE_DIR / "data" / "sample_docs")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(BASE_DIR / "outputs" / "chroma_db"))
COLLECTION_NAME = "connecthr_docs"

# 청킹 설정
CHUNK_STRATEGY = "fixed"       # "fixed" 또는 "semantic"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# 검색 테스트 쿼리
SEARCH_QUERIES = [
    "연차 휴가는 몇 일 발생하나요?",
    "재택근무 규정이 어떻게 되나요?",
    "비밀번호 정책은 무엇인가요?",
]


def print_section(title: str) -> None:
    """섹션 구분선과 제목을 출력합니다.

    Args:
        title: 출력할 섹션 제목
    """
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def run_pipeline() -> None:
    """벡터 DB 구축 전체 파이프라인을 실행합니다.

    1단계부터 5단계까지 순서대로 실행하며 각 단계의 소요 시간을 출력합니다.

    Raises:
        SystemExit: 필수 단계(추출, 청킹, 임베딩, 저장) 실패 시 프로그램을 종료합니다.
    """

    total_start = time.time()
    print("\n" + "=" * 60)
    print("  CH06: 벡터 DB 구축 파이프라인")
    print("  커넥트HR 사내 문서 ChromaDB 저장 및 검색 테스트")
    print("=" * 60)

    # =============================================
    # 1단계: 문서 추출
    # =============================================
    print_section("1단계: 문서 추출")
    step_start = time.time()

    # --- Input ---
    print(f"문서 디렉토리: {SAMPLE_DOCS_DIR}")

    try:
        # --- Process ---
        documents = extract_all(SAMPLE_DOCS_DIR)

        # --- Output ---
        if not documents:
            print("오류: 추출된 문서가 없습니다.")
            print(f"  {SAMPLE_DOCS_DIR} 디렉토리에 .txt 또는 .pdf 파일이 있는지 확인하십시오.")
            sys.exit(1)

        step_elapsed = time.time() - step_start
        print(f"\n1단계 완료: {len(documents)}개 문서 추출 ({step_elapsed:.2f}초)")
        for doc in documents:
            print(f"  - {doc['source']}: {len(doc['content'])}자")

    except FileNotFoundError as e:
        print(f"오류: {e}")
        sys.exit(1)

    # =============================================
    # 2단계: 청킹
    # =============================================
    print_section("2단계: 청킹 (문서 분할)")
    step_start = time.time()

    # --- Input ---
    print(f"전략: {CHUNK_STRATEGY} | 크기: {CHUNK_SIZE}자 | 오버랩: {CHUNK_OVERLAP}자")

    # --- Process ---
    all_chunks: list[Chunk] = []
    for doc in documents:
        chunks = chunk_document(
            text=doc["content"],
            source=doc["source"],
            strategy=CHUNK_STRATEGY,
            chunk_size=CHUNK_SIZE,
            overlap=CHUNK_OVERLAP,
        )
        all_chunks.extend(chunks)
        print(f"  {doc['source']}: {len(chunks)}개 청크")

    # --- Output ---
    if not all_chunks:
        print("오류: 청크가 생성되지 않았습니다.")
        sys.exit(1)

    step_elapsed = time.time() - step_start
    avg_size = sum(len(c.text) for c in all_chunks) / len(all_chunks)
    print(f"\n2단계 완료: 총 {len(all_chunks)}개 청크 생성 ({step_elapsed:.2f}초)")
    print(f"  평균 청크 크기: {avg_size:.1f}자")

    # 청킹 전략 비교 (첫 번째 문서만)
    print("\n[참고] 첫 번째 문서의 청킹 전략 비교:")
    compare_strategies(documents[0]["content"], source=documents[0]["source"])

    # =============================================
    # 3단계: 임베딩
    # =============================================
    print_section("3단계: 임베딩 (벡터 변환)")
    step_start = time.time()

    # --- Input ---
    print(f"임베딩 모델: Ollama nomic-embed-text (연결 실패 시 sentence-transformers fallback)")
    print(f"임베딩 대상: {len(all_chunks)}개 청크")

    # --- Process ---
    try:
        embeddings = embed_chunks(all_chunks)
    except (RuntimeError, ValueError) as e:
        print(f"오류: 임베딩 실패\n{e}")
        sys.exit(1)

    # --- Output ---
    step_elapsed = time.time() - step_start
    dim = len(embeddings[0]) if embeddings else 0
    print(f"\n3단계 완료: {len(embeddings)}개 벡터 생성, {dim}차원 ({step_elapsed:.2f}초)")

    # =============================================
    # 4단계: ChromaDB 저장
    # =============================================
    print_section("4단계: ChromaDB 저장")
    step_start = time.time()

    # --- Input ---
    print(f"저장 경로: {CHROMA_PERSIST_DIR}")
    print(f"컬렉션 이름: {COLLECTION_NAME}")

    # --- Process ---
    try:
        store = ChromaStore(persist_dir=CHROMA_PERSIST_DIR)
        store.create_collection(COLLECTION_NAME)

        # 문서별 메타데이터 구성
        metadatas = [{"doc_type": chunk.metadata.get("doc_type", "txt")} for chunk in all_chunks]
        saved_count = store.add_documents(all_chunks, embeddings, metadatas)

    except (RuntimeError, OSError) as e:
        print(f"오류: ChromaDB 저장 실패\n{e}")
        sys.exit(1)

    # --- Output ---
    step_elapsed = time.time() - step_start
    print(f"\n4단계 완료: {saved_count}개 청크 저장 ({step_elapsed:.2f}초)")
    store.get_collection_stats()

    # =============================================
    # 5단계: 검색 테스트
    # =============================================
    print_section("5단계: 검색 테스트")
    step_start = time.time()

    # --- Input ---
    print(f"테스트 쿼리 {len(SEARCH_QUERIES)}개로 검색 결과를 확인합니다.")
    print()

    # --- Process ---
    query_chunks = [
        Chunk(text=q, index=i, source="query", strategy="fixed")
        for i, q in enumerate(SEARCH_QUERIES)
    ]

    try:
        query_embeddings = embed_chunks(query_chunks)
    except (RuntimeError, ValueError) as e:
        print(f"오류: 쿼리 임베딩 실패\n{e}")
        sys.exit(1)

    # --- Output ---
    for i, (query, q_embedding) in enumerate(zip(SEARCH_QUERIES, query_embeddings)):
        print(f"[쿼리 {i + 1}] {query}")
        print("-" * 50)

        try:
            results = store.search(
                query=query,
                query_embedding=q_embedding,
                n_results=3,
            )
        except RuntimeError as e:
            print(f"  검색 오류: {e}")
            continue

        if not results:
            print("  검색 결과가 없습니다.")
        else:
            for rank, result in enumerate(results, 1):
                similarity_pct = result["similarity"] * 100
                print(f"  {rank}위 | 유사도: {similarity_pct:.1f}% | 출처: {result['source']}")
                # 텍스트 미리보기 (최대 120자)
                preview = result["text"][:120].replace("\n", " ")
                print(f"      {preview}...")
        print()

    step_elapsed = time.time() - step_start
    print(f"5단계 완료: 검색 테스트 ({step_elapsed:.2f}초)")

    # =============================================
    # 최종 요약
    # =============================================
    total_elapsed = time.time() - total_start
    print_section("파이프라인 완료")
    print(f"총 소요 시간     : {total_elapsed:.2f}초")
    print(f"처리된 문서 수   : {len(documents)}개")
    print(f"생성된 청크 수   : {len(all_chunks)}개")
    print(f"저장된 벡터 수   : {saved_count}개")
    print(f"임베딩 차원      : {dim}차원")
    print(f"ChromaDB 경로    : {CHROMA_PERSIST_DIR}")
    print()
    print("이서연: '세상에, 진짜 찾아오네요!'")
    print("김도현: '이제 절반 왔어. 다음은 이 검색 결과를 LLM과 연결하면 돼.'")


if __name__ == "__main__":
    run_pipeline()
