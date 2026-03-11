"""
CH07 RAG Q&A 엔진 — FastAPI 앱 진입점.

라우터 등록:
    /             → /admin/dashboard 리다이렉트
    /admin/qa/*   → Q&A REST API (qa_router)
    /admin/*      → HTML 페이지 (ui_router)
    /static/*     → 정적 파일

실행:
    python -m app.main
    uvicorn app.main:app --reload
"""

import os
import sys

from dotenv import load_dotenv

# --- Input ---
# 프로젝트 루트를 Python 경로에 추가
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 환경 변수 로드
load_dotenv()

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

# --- Process ---
# 라우터 임포트 (app 패키지 기준 절대 경로 사용)
from app.routers.ui import router as ui_router
from app.routers.qa import router as qa_router

STATIC_DIR = os.path.join(BASE_DIR, "static")

app = FastAPI(
    title="RAG Q&A 엔진",
    description="CH07 — ChromaDB 기반 사내 문서 RAG Q&A 서비스",
    version="1.0.0",
)

# 정적 파일 마운트
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 라우터 등록 (qa_router를 ui_router보다 먼저 등록하여 /admin/qa/query 우선 처리)
app.include_router(qa_router)
app.include_router(ui_router)


@app.get("/")
def root() -> RedirectResponse:
    """루트 접근 시 대시보드로 리다이렉트합니다."""
    return RedirectResponse(url="/admin/dashboard", status_code=302)


# --- Output ---
if __name__ == "__main__":
    import uvicorn

    print("RAG Q&A 엔진 서버 시작: http://127.0.0.1:8000")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
