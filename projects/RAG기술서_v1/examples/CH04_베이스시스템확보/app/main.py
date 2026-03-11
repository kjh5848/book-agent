"""
main.py
=======
FastAPI 애플리케이션 진입점입니다.

이 서버는 PostgreSQL에 저장된 직원/연차/매출 데이터를 REST API로 제공합니다.
docker-compose up -d 실행 후 http://localhost:8000/docs 에서 Swagger UI를 확인할 수 있습니다.
"""

from fastapi import FastAPI

from app.routers import employees, leaves, sales

# --- Input ---
# 애플리케이션 메타데이터 설정

app = FastAPI(
    title="RAG 기반 AI 업무 비서 — 베이스 CRUD API",
    description=(
        "AI 업무 비서 구축: RAG + MCP 실전 가이드 4장 베이스 시스템.\n\n"
        "직원(employees), 연차(leaves), 매출(sales) 데이터를 "
        "조회·생성·수정하는 REST API를 제공합니다."
    ),
    version="1.0.0",
    contact={
        "name": "RAG + MCP 실전 가이드",
    },
)

# --- Process ---
# 라우터 등록: 각 도메인별 라우터를 앱에 포함시킵니다.
app.include_router(employees.router)
app.include_router(leaves.router)
app.include_router(sales.router)


# --- Output ---
@app.get("/", summary="루트 — 서버 상태 확인", tags=["health"])
def root() -> dict:
    """
    서버 동작 여부를 확인하는 헬스체크 엔드포인트입니다.

    Returns:
        dict: 서버 상태 메시지
    """
    return {
        "status": "ok",
        "message": "RAG 베이스 CRUD API가 정상 실행 중입니다.",
        "docs": "http://localhost:8000/docs",
    }


@app.get("/health", summary="헬스체크", tags=["health"])
def health_check() -> dict:
    """
    컨테이너 오케스트레이터(docker-compose)가 호출하는 헬스체크 엔드포인트입니다.

    Returns:
        dict: {"status": "healthy"}
    """
    return {"status": "healthy"}
