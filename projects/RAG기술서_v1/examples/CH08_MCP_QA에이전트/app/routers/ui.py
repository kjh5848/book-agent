"""
HTML 페이지 라우터 — Jinja2 템플릿 렌더링.

엔드포인트:
    GET /admin/dashboard  — 메인 대시보드 (ChromaDB + PostgreSQL 통계)
    GET /admin/qa         — RAG 채팅 화면
    GET /admin/agent      — MCP Agent 채팅 화면
"""

import os

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database.connection import get_db_connection
from app.database.crud import count_employees, sum_sales

# 템플릿 디렉토리 설정
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_TEMPLATES_DIR = os.path.join(_BASE_DIR, "templates")

templates = Jinja2Templates(directory=_TEMPLATES_DIR)
router = APIRouter(tags=["UI"])


@router.get("/admin/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    """
    메인 대시보드 페이지를 렌더링합니다.

    ChromaDB 문서 수와 PostgreSQL 직원 수·매출 합계를 조회하여
    dashboard.html 템플릿에 전달합니다.
    조회 실패 시 각 통계값은 0으로 대체합니다.

    Args:
        request: FastAPI Request 객체.

    Returns:
        HTMLResponse: 렌더링된 대시보드 HTML 페이지.
    """
    # --- Input ---
    # vector_service는 순환 임포트 방지를 위해 지연 임포트
    from app.services.vector_service import vector_service

    # --- Process ---
    doc_count = vector_service.get_doc_count()

    employee_count = 0
    sales_total = 0
    try:
        conn = get_db_connection()
        try:
            employee_count = count_employees(conn)
            sales_total = sum_sales(conn)
        finally:
            conn.close()
    except Exception:
        pass

    context = {
        "request": request,
        "doc_count": doc_count,
        "employee_count": employee_count,
        "sales_total": sales_total,
    }

    # --- Output ---
    return templates.TemplateResponse("dashboard.html", context)


@router.get("/admin/qa", response_class=HTMLResponse)
async def qa_page(request: Request) -> HTMLResponse:
    """
    RAG 채팅 화면을 렌더링합니다.

    Args:
        request: FastAPI Request 객체.

    Returns:
        HTMLResponse: 렌더링된 Q&A 채팅 HTML 페이지.
    """
    # --- Input ---
    # --- Process ---
    # --- Output ---
    return templates.TemplateResponse("qa.html", {"request": request})


@router.get("/admin/agent", response_class=HTMLResponse)
async def agent_page(request: Request) -> HTMLResponse:
    """
    MCP Agent 채팅 화면을 렌더링합니다.

    Args:
        request: FastAPI Request 객체.

    Returns:
        HTMLResponse: 렌더링된 MCP Agent 채팅 HTML 페이지.
    """
    # --- Input ---
    # --- Process ---
    # --- Output ---
    return templates.TemplateResponse("agent.html", {"request": request})
