"""
Q&A REST API 라우터.

엔드포인트:
    POST /admin/qa/query  → 질문 처리 (인텐트 라우팅 → 벡터 검색 → LLM 답변)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.qa_service import qa_service

router = APIRouter(prefix="/admin/qa", tags=["qa"])


class QueryRequest(BaseModel):
    """질문 요청 스키마."""

    query: str


@router.post("/query")
async def query_qa(request: QueryRequest) -> dict:
    """
    사용자 질문을 처리하여 RAG 기반 답변을 반환합니다.

    처리 흐름:
        1. qa_service.hybrid_search(query) → 인텐트 라우팅 후 벡터 검색
        2. qa_service.get_ai_answer(query, results) → LLM 답변 생성

    Args:
        request: 질문 문자열을 담은 요청 객체.

    Returns:
        dict: {
            "query": 원본 질문,
            "answer": LLM 생성 답변,
            "route": 라우팅 결과 ("unstructured" | "hybrid"),
            "unstructured_data": 벡터 검색 결과 리스트
        }

    Raises:
        HTTPException: 검색 또는 LLM 호출 중 오류 발생 시 500 반환.
    """
    # --- Input ---
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="질문이 비어 있습니다. 질문을 입력하십시오.")

    # --- Process ---
    try:
        search_results = qa_service.hybrid_search(query)
        answer = qa_service.get_ai_answer(query, search_results)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"질문 처리 중 오류가 발생했습니다: {str(exc)}",
        ) from exc

    # --- Output ---
    return {
        "query": query,
        "answer": answer,
        "route": search_results["route"],
        "unstructured_data": search_results["unstructured"],
    }
