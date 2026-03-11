"""
FastAPI 애플리케이션 메인 모듈.

웹 채팅 UI와 REST API를 제공한다.
정적 파일(CSS, JS)과 Jinja2 템플릿을 서빙하며,
/api/chat 엔드포인트로 RAG Q&A 기능을 제공한다.
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트를 파이썬 경로에 추가 (python app/main.py 직접 실행 지원)
sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.chat_api import router as chat_router

load_dotenv()

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent

app = FastAPI(
    title="메타코딩 RAG Q&A 엔진",
    description="CH07 - LCEL 기반 RAG 체인 + 멀티턴 채팅 UI",
    version="1.0.0",
)

# 정적 파일 마운트
app.mount(
    "/static",
    StaticFiles(directory=str(PROJECT_ROOT / "static")),
    name="static",
)

# Jinja2 템플릿 설정
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "templates"))

# API 라우터 등록
app.include_router(chat_router)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """
    루트 경로 요청을 채팅 페이지로 리디렉션한다.

    Args:
        request: FastAPI Request 객체

    Returns:
        채팅 페이지 HTML 응답
    """
    return templates.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "active_page": "chat",
            "page_title": "RAG Q&A 채팅",
            "page_subtitle": "사내 문서 기반 AI 질의응답 시스템",
        },
    )


@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request) -> HTMLResponse:
    """
    채팅 UI 페이지를 렌더링한다.

    Args:
        request: FastAPI Request 객체

    Returns:
        chat.html 기반 HTML 응답
    """
    return templates.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "active_page": "chat",
            "page_title": "RAG Q&A 채팅",
            "page_subtitle": "사내 문서에 대해 무엇이든 질문해 보세요.",
        },
    )


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    서버 상태 확인 엔드포인트.

    Returns:
        {"status": "ok"} 딕셔너리
    """
    return {"status": "ok", "service": "CH07 RAG Q&A 엔진"}


if __name__ == "__main__":
    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    port = int(os.getenv("FASTAPI_PORT", "8000"))
    print(f"[INFO] 서버 시작: http://{host}:{port}")
    print("[INFO] 채팅 UI: http://localhost:8000/chat")
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
    )
