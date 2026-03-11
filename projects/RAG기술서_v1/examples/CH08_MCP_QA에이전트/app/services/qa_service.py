"""
RAG Q&A 오케스트레이터 서비스.

인텐트 분류 → 벡터 검색 → LLM 답변 생성의 하이브리드 RAG 파이프라인을 조율합니다.
"""

from app.services.llm_service import llm_service
from app.services.vector_service import vector_service


class QAService:
    """RAG 하이브리드 검색 오케스트레이터.

    llm_service의 인텐트 분류 결과에 따라 vector_service를 통해
    비정형 문서를 검색하고 LLM 답변을 생성합니다.
    """

    def hybrid_search(self, query: str) -> dict:
        """
        인텐트 라우팅 후 벡터 검색을 수행합니다.

        Args:
            query: 사용자 질의 문자열.

        Returns:
            dict: {
                "query": 원본 질의,
                "unstructured": [{"content", "source", "score"}] 벡터 검색 결과,
                "route": 인텐트 분류 결과 (unstructured | hybrid)
            }
        """
        # --- Input ---
        intent = llm_service.classify_intent(query)
        route = intent.get("route", "hybrid")

        # --- Process ---
        unstructured_results = vector_service.search_unstructured(query, k=3)

        # --- Output ---
        return {
            "query": query,
            "unstructured": unstructured_results,
            "route": route,
        }

    def get_ai_answer(self, query: str, search_results: dict) -> str:
        """
        검색 결과를 컨텍스트로 구성하여 LLM 답변을 생성합니다.

        Args:
            query: 사용자 질의 문자열.
            search_results: hybrid_search()의 반환값.

        Returns:
            str: LLM이 생성한 한국어 답변 문자열.
        """
        # --- Input ---
        unstructured = search_results.get("unstructured", [])

        # --- Process ---
        context_parts = []

        if unstructured:
            context_parts.append("[사내 문서 검색 결과]")
            for i, item in enumerate(unstructured, 1):
                source = item.get("source", "알 수 없음")
                content = item.get("content", "")
                context_parts.append(f"{i}. [{source}]\n{content}")

        if not context_parts:
            context_parts.append("관련 문서를 찾지 못했습니다.")

        context = "\n\n".join(context_parts)

        # --- Output ---
        return llm_service.generate_answer(query, context)


# 싱글톤 인스턴스
qa_service = QAService()
