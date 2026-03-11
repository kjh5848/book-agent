"""CrossEncoder ReRanker 및 Hybrid Search 모듈입니다.

1차 검색 결과를 CrossEncoder로 재순위화하고,
벡터 검색과 BM25 키워드 검색을 결합한 Hybrid Search를 제공합니다.
"""

import os
import logging
import math
from typing import Any

import chromadb
from rank_bm25 import BM25Okapi
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# --- 상수 ---
RERANKER_MODEL: str = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
EMBED_MODEL: str = os.getenv("EMBED_MODEL", "nomic-embed-text")
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


def rerank_with_cross_encoder(
    query: str,
    documents: list[str],
    top_k: int = 3,
) -> list[dict[str, Any]]:
    """CrossEncoder로 1차 검색 결과를 재순위화합니다.

    sentence-transformers의 CrossEncoder 모델을 사용하여 쿼리-문서 쌍별 점수를
    계산하고 점수 내림차순으로 정렬하여 상위 top_k개를 반환합니다.

    Args:
        query: 사용자 검색 질의 문자열
        documents: 1차 검색에서 반환된 문서 텍스트 리스트 (k=10 권장)
        top_k: 최종 반환할 문서 수 (기본값: 3)

    Returns:
        점수 내림차순으로 정렬된 딕셔너리 리스트::

            [{"text": str, "score": float}]

    Raises:
        ImportError: sentence-transformers 패키지가 설치되지 않은 경우
        RuntimeError: CrossEncoder 모델 로딩 실패 시
    """
    # --- Input ---
    if not documents:
        logger.warning("재순위화할 문서가 없습니다.")
        return []

    if not query.strip():
        raise ValueError("검색 쿼리가 비어 있습니다. 질문을 입력하십시오.")

    # --- Process ---
    try:
        from sentence_transformers import CrossEncoder
    except ImportError as exc:
        raise ImportError(
            "sentence-transformers 패키지가 설치되지 않았습니다. "
            "'pip install sentence-transformers' 명령어로 설치하십시오."
        ) from exc

    try:
        model = CrossEncoder(RERANKER_MODEL)
    except Exception as exc:
        raise RuntimeError(
            f"CrossEncoder 모델({RERANKER_MODEL}) 로딩에 실패했습니다: {exc}\n"
            "인터넷 연결을 확인하거나 .env의 RERANKER_MODEL 값을 점검하십시오."
        ) from exc

    pairs = [(query, doc) for doc in documents]
    scores: list[float] = model.predict(pairs).tolist()

    scored_docs = [
        {"text": doc, "score": float(score)}
        for doc, score in zip(documents, scores)
    ]
    scored_docs.sort(key=lambda x: x["score"], reverse=True)

    # --- Output ---
    return scored_docs[:top_k]


def _normalize_scores(scores: list[float]) -> list[float]:
    """점수 리스트를 0~1 범위로 정규화합니다.

    Args:
        scores: 정규화할 점수 리스트

    Returns:
        0~1 범위로 정규화된 점수 리스트. 모든 값이 동일하면 균등 분배합니다.
    """
    # --- Input ---
    if not scores:
        return []

    # --- Process ---
    min_s = min(scores)
    max_s = max(scores)
    if max_s == min_s:
        return [1.0 / len(scores)] * len(scores)

    # --- Output ---
    return [(s - min_s) / (max_s - min_s) for s in scores]


def hybrid_search(
    query: str,
    collection: chromadb.Collection,
    k: int = 3,
    alpha: float = 0.5,
) -> list[dict[str, Any]]:
    """벡터 유사도 검색과 BM25 키워드 검색을 결합하여 검색 품질을 향상시킵니다.

    alpha 가중치로 벡터 검색 점수와 BM25 점수를 가중 합산하여 최종 순위를
    결정합니다. alpha=1.0이면 순수 벡터 검색, alpha=0.0이면 순수 BM25 검색입니다.

    Args:
        query: 사용자 검색 질의 문자열
        collection: 검색 대상 ChromaDB 컬렉션 객체
        k: 최종 반환할 상위 문서 수 (기본값: 3)
        alpha: 벡터 검색 가중치 (0.0 ~ 1.0). BM25 가중치는 1-alpha입니다.

    Returns:
        가중 합산 점수 내림차순으로 정렬된 딕셔너리 리스트::

            [{"text": str, "metadata": dict, "score": float}]

    Raises:
        ValueError: alpha가 0~1 범위를 벗어난 경우
        RuntimeError: 검색 실행 실패 시
    """
    # --- Input ---
    if not 0.0 <= alpha <= 1.0:
        raise ValueError(f"alpha 값은 0.0~1.0 범위여야 합니다. 입력값: {alpha}")

    if not query.strip():
        raise ValueError("검색 쿼리가 비어 있습니다. 질문을 입력하십시오.")

    total_docs = collection.count()
    if total_docs == 0:
        logger.warning("컬렉션이 비어 있습니다. 문서를 먼저 인덱싱하십시오.")
        return []

    fetch_k = min(max(k * 4, 10), total_docs)

    # --- Process ---
    # 1. 벡터 검색 (ChromaDB)
    try:
        vector_results = collection.query(
            query_texts=[query],
            n_results=fetch_k,
            include=["documents", "metadatas", "distances"],
        )
    except Exception as exc:
        raise RuntimeError(
            f"ChromaDB 벡터 검색 중 오류가 발생했습니다: {exc}\n"
            "Ollama 임베딩 서버가 실행 중인지 확인하십시오."
        ) from exc

    vector_docs: list[str] = vector_results["documents"][0]
    vector_distances: list[float] = vector_results["distances"][0]
    vector_metadatas: list[dict] = vector_results.get("metadatas", [[{}] * len(vector_docs)])[0]

    # 거리를 유사도 점수로 변환 (거리가 작을수록 유사도 높음)
    vector_scores = [1.0 / (1.0 + d) for d in vector_distances]
    norm_vector_scores = _normalize_scores(vector_scores)

    # 2. BM25 키워드 검색
    tokenized_corpus = [doc.split() for doc in vector_docs]
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = query.split()
    bm25_raw_scores: list[float] = bm25.get_scores(tokenized_query).tolist()
    norm_bm25_scores = _normalize_scores(bm25_raw_scores)

    # 3. 가중 합산
    combined: list[dict[str, Any]] = []
    for i, doc in enumerate(vector_docs):
        combined_score = alpha * norm_vector_scores[i] + (1.0 - alpha) * norm_bm25_scores[i]
        combined.append({
            "text": doc,
            "metadata": vector_metadatas[i] if i < len(vector_metadatas) else {},
            "score": round(combined_score, 4),
        })

    combined.sort(key=lambda x: x["score"], reverse=True)

    # --- Output ---
    return combined[:k]
