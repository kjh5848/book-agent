"""
HTML 페이지 라우터 — Jinja2 템플릿 렌더링.

제공 페이지:
    /admin/dashboard  → 시스템 상태 대시보드 (ChromaDB 문서 수, 모델 정보)
    /admin/qa         → 채팅 Q&A 화면
"""

import os

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

templates = Jinja2Templates(directory=TEMPLATES_DIR)
router = APIRouter(prefix="/admin", tags=["ui"])


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    """
    메인 대시보드 화면을 렌더링합니다.

    ChromaDB 연결 상태와 문서 수, 사용 중인 LLM/임베딩 모델 정보를 표시합니다.

    Args:
        request: FastAPI 요청 객체 (Jinja2 템플릿에 전달).

    Returns:
        HTMLResponse: dashboard.html 렌더링 결과.
    """
    # --- Input ---
    from app.services.vector_service import vector_service

    # --- Process ---
    doc_count = 0
    db_status = "연결 끊김"
    try:
        if vector_service.vector_db is not None:
            collection = vector_service.vector_db._collection
            doc_count = collection.count()
            db_status = "정상"
    except Exception:
        db_status = "오류"

    llm_provider = os.getenv("LLM_PROVIDER", "ollama").upper()
    llm_model = os.getenv("LLM_MODEL_NAME", "deepseek-r1:1.5b")
    embed_model = os.getenv("EMBED_MODEL", "nomic-embed-text")
    chroma_dir = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")

    # --- Output ---
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "active_page": "dashboard",
            "doc_count": doc_count,
            "db_status": db_status,
            "llm_provider": llm_provider,
            "llm_model": llm_model,
            "embed_model": embed_model,
            "chroma_dir": chroma_dir,
        },
    )


@router.get("/qa", response_class=HTMLResponse)
async def qa_page(request: Request) -> HTMLResponse:
    """
    채팅 Q&A 화면을 렌더링합니다.

    Args:
        request: FastAPI 요청 객체 (Jinja2 템플릿에 전달).

    Returns:
        HTMLResponse: qa.html 렌더링 결과.
    """
    return templates.TemplateResponse(
        "qa.html",
        {
            "request": request,
            "active_page": "qa",
        },
    )
