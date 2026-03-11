"""
Q&A REST API 라우터.

엔드포인트:
    POST /admin/qa/query  — RAG 하이브리드 검색 + LLM 답변
    POST /admin/qa/agent  — MCP Agent 모드 실행
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.qa_service import qa_service

router = APIRouter(tags=["QA API"])


class QueryRequest(BaseModel):
    """Q&A 질의 요청 모델.

    Attributes:
        query: 사용자 질의 문자열.
    """

    query: str


@router.post("/admin/qa/query")
async def query_qa(request: QueryRequest) -> dict:
    """
    RAG 하이브리드 검색으로 질문에 답변합니다.

    인텐트를 분류하여 ChromaDB 벡터 검색 후 LLM 답변을 생성합니다.

    Args:
        request: 질의 문자열을 담은 QueryRequest 객체.

    Returns:
        dict: {
            "query": 원본 질의,
            "answer": LLM 생성 답변,
            "route": 인텐트 라우팅 결과 (unstructured | hybrid),
            "unstructured_data": [{"content", "source", "score"}] 검색 결과 리스트
        }

    Raises:
        HTTPException: 검색 또는 LLM 호출 중 오류 발생 시 500 반환.
    """
    # --- Input ---
    query_text = request.query.strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="질의 내용이 비어 있습니다.")

    # --- Process ---
    try:
        search_results = qa_service.hybrid_search(query_text)
        answer = qa_service.get_ai_answer(query_text, search_results)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Q&A 처리 중 오류가 발생했습니다: {exc}",
        ) from exc

    # --- Output ---
    return {
        "query": query_text,
        "answer": answer,
        "route": search_results.get("route", "hybrid"),
        "unstructured_data": search_results.get("unstructured", []),
    }


@router.post("/admin/qa/agent")
async def query_agent(request: QueryRequest) -> dict:
    """
    MCP Agent 모드로 질문에 답변합니다.

    FastMCP 서버를 서브프로세스로 실행하고 ReAct Agent를 통해
    PostgreSQL DB 도구를 호출하여 답변을 생성합니다.

    Args:
        request: 질의 문자열을 담은 QueryRequest 객체.

    Returns:
        dict: {
            "query": 원본 질의,
            "answer": 최종 답변 문자열,
            "steps": [{"tool", "input", "output"}] 도구 사용 기록,
            "mode": "mcp_agent"
        }

    Raises:
        HTTPException: Agent 실행 중 오류 발생 시 500 반환.
    """
    # --- Input ---
    query_text = request.query.strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="질의 내용이 비어 있습니다.")

    # --- Process ---
    try:
        from app.services.mcp_agent_service import mcp_agent_service

        result = mcp_agent_service.run_agent(query_text)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"MCP Agent 실행 중 오류가 발생했습니다: {exc}",
        ) from exc

    # --- Output ---
    return {
        "query": query_text,
        "answer": result.get("answer", ""),
        "steps": result.get("steps", []),
        "mode": "mcp_agent",
    }
