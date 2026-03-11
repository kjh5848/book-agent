"""RAG 검색 도구 모듈 — ChromaDB 기반 문서 검색.

LangChain @tool 데코레이터로 ChromaDB 벡터 검색 함수를
LLM이 직접 호출 가능한 도구로 래핑합니다.
ChromaDB 벡터 DB가 구축되어 있어야 합니다. 미구축 시 RuntimeError가 발생합니다.

챕터 8.3: 통합 응답 전략 — 문서 검색 도구 정의
"""

import os
from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "company_docs")
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "3"))


def _search_chromadb(query: str, top_k: int) -> list[dict]:
    """ChromaDB에서 유사도 검색을 수행합니다.

    Args:
        query: 검색 쿼리 문자열
        top_k: 반환할 최대 문서 수

    Returns:
        검색 결과 딕셔너리 리스트 (source, content, score 포함)

    Raises:
        RuntimeError: ChromaDB 경로가 없거나 컬렉션이 없는 경우
    """

    # --- Input ---
    from pathlib import Path
    chroma_path = Path(CHROMA_PERSIST_DIR)

    # --- Process ---
    if not chroma_path.exists():
        raise RuntimeError(
            f"ChromaDB 경로가 없습니다: {chroma_path}\n"
            "CH06 예제를 먼저 실행하여 벡터 DB를 구축하십시오:\n"
            "  cd ../CH06_벡터DB구축 && python src/main.py"
        )

    import chromadb
    from chromadb.utils import embedding_functions

    client = chromadb.PersistentClient(path=str(chroma_path))
    embed_fn = embedding_functions.DefaultEmbeddingFunction()

    try:
        collection = client.get_collection(
            name=CHROMA_COLLECTION,
            embedding_function=embed_fn,
        )
    except Exception as e:
        raise RuntimeError(
            f"컬렉션 '{CHROMA_COLLECTION}'이 존재하지 않습니다.\n"
            "CH06 예제를 먼저 실행하여 벡터 DB를 구축하십시오:\n"
            "  cd ../CH06_벡터DB구축 && python src/main.py"
        ) from e

    results = collection.query(query_texts=[query], n_results=top_k)

    docs: list[dict] = []
    for i, (doc_text, metadata, distance) in enumerate(
        zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ):
        docs.append({
            "source": metadata.get("source", "unknown"),
            "content": doc_text,
            "score": round(1 - distance, 4),
        })

    # --- Output ---
    return docs


def _format_search_results(docs: list[dict]) -> str:
    """검색 결과를 LLM이 이해하기 쉬운 형식으로 포맷팅합니다.

    Args:
        docs: 검색 결과 딕셔너리 리스트

    Returns:
        포맷팅된 문자열
    """

    # --- Input ---
    if not docs:
        return "관련 사내 문서를 찾을 수 없습니다."

    # --- Process ---
    parts: list[str] = []
    for i, doc in enumerate(docs, start=1):
        source = doc.get("source", "unknown")
        content = doc.get("content", "")
        score = doc.get("score", 0.0)
        parts.append(f"[문서 {i}] 출처: {source} (유사도: {score:.2f})\n{content}")

    # --- Output ---
    return "\n\n".join(parts)


@tool
def search_company_docs(query: str) -> str:
    """회사 사내 문서에서 질문과 관련된 내용을 검색합니다.

    ChromaDB 벡터 DB에서 유사도 검색을 수행합니다.
    규정, 정책, 절차, 방법 등 비정형 정보를 찾을 때 사용합니다.

    Args:
        query: 검색할 내용 (예: '연차 신청 방법', 'VPN 사용 규정')

    Returns:
        관련 문서 내용이 포함된 문자열.
        출처 정보(문서명, 유사도 점수) 포함.

    Raises:
        RuntimeError: ChromaDB가 구축되지 않은 경우
    """

    # --- Input ---
    top_k = RAG_TOP_K

    # --- Process ---
    docs = _search_chromadb(query, top_k)
    print(f"  [RAG] ChromaDB 검색 완료: {len(docs)}건")

    # --- Output ---
    return _format_search_results(docs)


# ============================================================
# 도구 목록 (에이전트에 전달)
# ============================================================

RAG_TOOLS = [search_company_docs]
