"""채팅 API 라우터.

FastAPI 라우터로 채팅 UI 서빙과 POST /api/chat 엔드포인트를 제공한다.
ConnectHRAgent(use_agent=True) 또는 단순 RAG 검색(use_agent=False)을 지원한다.
CH09에서는 응답 캐시 연동이 추가되었다.

IPO 패턴:
  Input  - ChatRequest(query, use_agent)
  Process - ConnectHRAgent.run() 또는 search_documents 직접 호출 (캐시 우선)
  Output - ChatResponse(answer, query_type, mode, steps)
"""

from __future__ import annotations

import sys
import os
from typing import Any, Optional

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# 1. 라우터 및 템플릿 설정
# ---------------------------------------------------------------------------

router = APIRouter()

# 템플릿 경로 (app/ 기준으로 ../templates/)
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(_BASE_DIR, "templates"))


# ---------------------------------------------------------------------------
# 2. 요청/응답 모델
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    """채팅 요청 모델."""

    query: str = Field(..., description="사용자 질문 문자열")
    use_agent: bool = Field(default=True, description="통합 에이전트 사용 여부")


class EvidenceItem(BaseModel):
    """답변 근거 항목."""

    text: str = Field(default="", description="근거 텍스트")
    image_url: str = Field(default="", description="캡처 이미지 URL")
    source: str = Field(default="", description="출처 문서명")
    page: str = Field(default="", description="페이지 번호")
    table_data: dict = Field(default_factory=dict, description="DB 조회 데이터 (정형)")
    query: str = Field(default="", description="SQL 쿼리 (정형)")


class ChatResponse(BaseModel):
    """채팅 응답 모델."""

    query: str = Field(..., description="원본 질문")
    answer: str = Field(..., description="최종 답변")
    query_type: str = Field(default="unstructured", description="질문 유형: structured|unstructured|hybrid")
    mode: str = Field(default="agent", description="처리 모드: agent|rag")
    structured_data: dict = Field(default_factory=dict, description="DB 조회 결과")
    unstructured_data: list = Field(default_factory=list, description="문서 검색 결과")
    evidence: list[EvidenceItem] = Field(default_factory=list, description="답변 근거")
    steps: list = Field(default_factory=list, description="에이전트 중간 단계")


# ---------------------------------------------------------------------------
# 3. 싱글턴 관리
# ---------------------------------------------------------------------------

_agent_instance: Optional[Any] = None
_router_instance: Optional[Any] = None


def _get_agent() -> Any:
    """ConnectHRAgent 싱글턴을 반환한다."""
    global _agent_instance
    if _agent_instance is None:
        # sys.path에 src/ 추가
        src_path = os.path.join(_BASE_DIR, "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        from src.agent_config import get_agent
        _agent_instance = get_agent()
    return _agent_instance


def _get_router() -> Any:
    """QueryRouter 싱글턴을 반환한다."""
    global _router_instance
    if _router_instance is None:
        src_path = os.path.join(_BASE_DIR, "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        from src.router import QueryRouter
        _router_instance = QueryRouter()
    return _router_instance


# ---------------------------------------------------------------------------
# 4. 근거 수집 헬퍼
# ---------------------------------------------------------------------------

def _collect_evidence(query: str, query_type: str) -> list[EvidenceItem]:
    """질문에 대한 답변 근거를 수집한다."""
    try:
        from tuning.evidence_pipeline import retrieve_with_evidence, format_evidence_response

        result = retrieve_with_evidence(query, query_type=query_type)
        formatted = format_evidence_response(result)

        items = []
        for ev in formatted.get("evidence", []):
            items.append(EvidenceItem(
                text=ev.get("text", ""),
                image_url=ev.get("image_url", ""),
                source=ev.get("source", ""),
                page=str(ev.get("page", "")),
                table_data=ev.get("table_data", {}),
                query=ev.get("query", ""),
            ))
        return items
    except Exception:
        return []


# ---------------------------------------------------------------------------
# 5. 엔드포인트 정의
# ---------------------------------------------------------------------------

@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request) -> HTMLResponse:
    """채팅 UI 페이지를 반환한다.

    Args:
        request: FastAPI Request 객체.

    Returns:
        chat.html 렌더링 결과.
    """
    return templates.TemplateResponse("chat.html", {"request": request})


@router.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(body: ChatRequest) -> ChatResponse:
    """사용자 질문을 처리하고 답변을 반환한다.

    use_agent=True이면 IntegratedAgent를 사용하고,
    False이면 search_documents 도구만 직접 호출한다.

    Args:
        body: ChatRequest (query, use_agent).

    Returns:
        ChatResponse (answer, query_type, structured_data, unstructured_data, steps).
    """
    src_path = os.path.join(_BASE_DIR, "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    if body.use_agent:
        # ① 통합 에이전트 모드 (캐시 연동)
        try:
            agent = _get_agent()  # ①
            result = agent.run(body.query)

            # 근거 수집
            evidence = _collect_evidence(body.query, result.get("route", "unstructured"))

            return ChatResponse(
                query=body.query,
                answer=result.get("output", "답변을 생성하지 못했습니다."),
                query_type=result.get("route", "unstructured"),
                mode="agent",
                evidence=evidence,
                steps=result.get("intermediate_steps", []),
            )
        except Exception as e:
            return ChatResponse(
                query=body.query,
                answer=f"에이전트 처리 중 오류가 발생했습니다: {e}",
                mode="agent",
            )
    else:
        # ② 단순 RAG 모드 (문서 검색만)
        try:
            from src.tools.search_documents import search_documents
            from src.router import QueryRouter

            query_router = _get_router()  # ②
            query_type = query_router.classify_query(body.query)

            search_result = search_documents.invoke({"query": body.query})  # ③
            docs = search_result if isinstance(search_result, list) else []

            # 간단한 컨텍스트 조합 응답
            if docs:
                context = "\n\n".join(d["content"] for d in docs)
                answer = f"관련 문서에서 찾은 내용:\n\n{context}"
            else:
                answer = "관련 문서를 찾지 못했습니다."

            return ChatResponse(
                query=body.query,
                answer=answer,
                query_type=query_type,
                mode="rag",
                unstructured_data=docs,
            )
        except Exception as e:
            return ChatResponse(
                query=body.query,
                answer=f"RAG 검색 중 오류가 발생했습니다: {e}",
                mode="rag",
            )
