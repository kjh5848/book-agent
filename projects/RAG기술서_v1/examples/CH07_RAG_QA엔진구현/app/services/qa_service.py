"""
RAG Q&A 오케스트레이터 서비스.

인텐트 라우팅 → 벡터 검색 → LLM 답변 생성 전체 파이프라인을 조율합니다.
정형 데이터(DB) 없이 비정형 문서(ChromaDB) 검색만 사용합니다.

CH08 확장 포인트:
    - db_service.py 추가 (SQLite SQL 조회)
    - agent_service.py 추가 (Tool Calling Agent)
    - hybrid_search()에 structured 경로 추가
"""

from typing import Any

from app.services.llm_service import llm_service
from app.services.vector_service import vector_service


class QAService:
    """RAG Q&A 파이프라인 오케스트레이터."""

    def __init__(self) -> None:
        """QAService를 초기화합니다."""
        print("[QAService] 오케스트레이터 초기화 완료.")

    def hybrid_search(self, query: str) -> dict[str, Any]:
        """
        인텐트 라우팅을 적용한 문서 검색을 수행합니다.

        LLM이 질문을 분석하여 검색 전략을 결정합니다.
        CH07에서는 비정형 문서(ChromaDB) 검색만 지원합니다.

        Args:
            query: 사용자 질문 문자열.

        Returns:
            dict: {
                "query"       : 원본 질문,
                "unstructured": 벡터 검색 결과 리스트,
                "route"       : 라우팅 결과 ("unstructured" | "hybrid")
            }
        """
        # --- Input ---
        print(f"[QAService] 질문 수신: {query[:50]}...")

        # --- Process ---
        # 1. 인텐트 분류
        analysis = llm_service.classify_intent(query)
        route = analysis.get("route", "hybrid")
        print(f"[QAService] 라우팅 결정: {route} (사유: {analysis.get('reason', '-')})")

        # CH07은 비정형 문서 검색만 지원
        # route가 "structured"로 분류되어도 unstructured 검색으로 대체
        if route == "structured":
            print("[QAService] structured 라우팅 → unstructured로 대체 (CH07 지원 범위)")
            route = "hybrid"

        unstructured: list[dict[str, Any]] = []
        if route in ("unstructured", "hybrid"):
            unstructured = vector_service.search_unstructured(query)

        # --- Output ---
        return {
            "query": query,
            "unstructured": unstructured,
            "route": route,
        }

    def get_ai_answer(self, query: str, search_results: dict[str, Any]) -> str:
        """
        검색 결과로 컨텍스트를 구성하고 LLM 답변을 생성합니다.

        Args:
            query         : 사용자 질문 문자열.
            search_results: hybrid_search() 반환값.

        Returns:
            str: LLM이 생성한 답변 문자열.
        """
        # --- Input ---
        unstructured_docs = search_results.get("unstructured", [])

        # --- Process ---
        context_parts: list[str] = []

        if unstructured_docs:
            context_parts.append("[사내 문서 내용]")
            for doc in unstructured_docs:
                source = doc.get("source", "알 수 없음")
                content = doc.get("content", "")
                context_parts.append(f"- {content} (출처: {source})")
        else:
            context_parts.append("[관련 문서를 찾지 못했습니다. 일반 지식으로 답변합니다.]")

        context_text = "\n".join(context_parts)

        # --- Output ---
        return llm_service.generate_answer(query, context_text)


# 싱글톤 인스턴스
qa_service = QAService()
