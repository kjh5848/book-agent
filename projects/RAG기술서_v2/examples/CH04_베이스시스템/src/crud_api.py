"""
FastAPI CRUD API 서버 — 커넥트HR 베이스 시스템

사내 PostgreSQL DB에 대한 REST API 엔드포인트를 제공합니다.
LLM이 직접 SQL을 실행하는 대신 이 API를 통해 허용된 작업만 수행합니다.

엔드포인트:
    GET  /employees              — 전체 직원 목록 조회
    GET  /employees/{id}         — 특정 직원 상세 조회
    GET  /leave-balance/{emp_id} — 직원 연차 잔액 조회
    GET  /sales/summary          — 부서별 매출 요약 조회
    GET  /health                 — 서버 상태 확인

실행 방법:
    uvicorn src.crud_api:app --reload --port 8000

챕터 4.3: CRUD API 구조 이해
"""

import os
import sys
from contextlib import asynccontextmanager
from datetime import date
from typing import Any, AsyncGenerator, Optional

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

# 환경 변수 로딩
load_dotenv()


# ============================================================
# 상수 및 DB 설정
# ============================================================

DB_CONFIG: dict[str, Any] = {
    "host":     os.getenv("POSTGRES_HOST", "localhost"),
    "port":     int(os.getenv("POSTGRES_PORT", "5432")),
    "dbname":   os.getenv("POSTGRES_DB", "connecthr"),
    "user":     os.getenv("POSTGRES_USER", "admin"),
    "password": os.getenv("POSTGRES_PASSWORD", "password"),
}


# ============================================================
# Pydantic 응답 모델 (v2)
# ============================================================

class EmployeeResponse(BaseModel):
    """직원 정보 응답 모델."""

    id:          int
    name:        str
    department:  str
    hire_date:   date
    base_salary: float
    email:       Optional[str] = None
    is_active:   bool

    model_config = {"from_attributes": True}


class LeaveBalanceResponse(BaseModel):
    """연차 잔액 응답 모델."""

    employee_id:    int
    employee_name:  str
    year:           int
    total_days:     float
    used_days:      float
    remaining_days: float = Field(description="잔여 연차 일수 (total - used)")

    model_config = {"from_attributes": True}


class SalesSummaryResponse(BaseModel):
    """매출 요약 응답 모델."""

    department:          str
    year:                int
    month:               int
    revenue:             float
    target:              Optional[float] = None
    achievement_rate:    Optional[float] = Field(
        default=None, description="목표 달성률 (%)"
    )

    model_config = {"from_attributes": True}


class HealthResponse(BaseModel):
    """서버 상태 응답 모델."""

    status:   str
    database: str
    message:  str


# ============================================================
# DB 연결 유틸리티
# ============================================================

def get_connection() -> psycopg2.extensions.connection:
    """PostgreSQL 커넥션을 생성하여 반환합니다.

    Returns:
        psycopg2 커넥션 객체

    Raises:
        HTTPException: DB 연결 실패 시 503 반환
    """
    try:
        return psycopg2.connect(**DB_CONFIG)
    except psycopg2.OperationalError as e:
        raise HTTPException(
            status_code=503,
            detail=(
                f"데이터베이스 연결에 실패했습니다. "
                f"docker-compose up -d 명령으로 PostgreSQL을 먼저 실행하십시오. "
                f"(원인: {e})"
            ),
        )


# ============================================================
# FastAPI 앱 초기화
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """애플리케이션 시작/종료 시 DB 연결 상태를 확인합니다.

    Args:
        app: FastAPI 애플리케이션 인스턴스

    Raises:
        SystemExit: DB 연결 불가 시 서버 시작 중단
    """
    # --- 시작 시 DB 연결 확인 ---
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.close()
        print("[시작] 커넥트HR CRUD API 서버가 시작되었습니다.")
        print(f"       DB: {DB_CONFIG['dbname']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}")
        print("       Swagger UI: http://localhost:8000/docs")
    except psycopg2.OperationalError as e:
        print("[경고] PostgreSQL 연결 불가. docker-compose up -d 를 먼저 실행하십시오.")
        print(f"       원인: {e}")

    yield  # 서버 실행

    # --- 종료 시 ---
    print("[종료] 커넥트HR CRUD API 서버가 종료되었습니다.")


app = FastAPI(
    title="커넥트HR CRUD API",
    description=(
        "사내 HR 데이터베이스(직원/휴가/매출)에 대한 REST API.\n"
        "LLM 에이전트가 이 API를 통해 DB를 안전하게 조회합니다."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ============================================================
# 엔드포인트
# ============================================================

@app.get("/health", response_model=HealthResponse, tags=["시스템"])
def health_check() -> HealthResponse:
    """서버 및 데이터베이스 연결 상태를 확인합니다.

    Returns:
        서버 상태 정보 (status, database, message)
    """
    # --- Input ---
    # (파라미터 없음)

    # --- Process ---
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
        conn.close()
        db_status = "connected"
        message = "정상 동작 중입니다."
    except HTTPException:
        db_status = "disconnected"
        message = "데이터베이스 연결 오류."

    # --- Output ---
    return HealthResponse(
        status="ok" if db_status == "connected" else "error",
        database=db_status,
        message=message,
    )


@app.get("/employees", response_model=list[EmployeeResponse], tags=["직원"])
def list_employees(
    department: Optional[str] = Query(default=None, description="부서명으로 필터링"),
    is_active:  Optional[bool] = Query(default=True,  description="재직 여부 필터 (기본: 재직자만)"),
) -> list[EmployeeResponse]:
    """직원 목록을 조회합니다.

    Args:
        department: 부서명 필터 (예: '개발팀'). None이면 전체 조회.
        is_active:  재직 여부 필터. True면 재직자만, False면 퇴직자만, None이면 전체.

    Returns:
        직원 정보 리스트
    """
    # --- Input ---
    conditions: list[str] = []
    params: list[Any] = []

    if is_active is not None:
        conditions.append("is_active = %s")
        params.append(is_active)
    if department:
        conditions.append("department = %s")
        params.append(department)

    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    query = f"""
        SELECT id, name, department, hire_date, base_salary, email, is_active
        FROM employees
        {where_clause}
        ORDER BY department, name;
    """

    # --- Process ---
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
    finally:
        conn.close()

    # --- Output ---
    return [EmployeeResponse(**dict(row)) for row in rows]


@app.get("/employees/{employee_id}", response_model=EmployeeResponse, tags=["직원"])
def get_employee(employee_id: int) -> EmployeeResponse:
    """특정 직원의 상세 정보를 조회합니다.

    Args:
        employee_id: 직원 고유 ID

    Returns:
        직원 상세 정보

    Raises:
        HTTPException: 직원을 찾을 수 없을 경우 404 반환
    """
    # --- Input ---
    query = """
        SELECT id, name, department, hire_date, base_salary, email, is_active
        FROM employees
        WHERE id = %s;
    """

    # --- Process ---
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (employee_id,))
            row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {employee_id}인 직원을 찾을 수 없습니다."
        )

    # --- Output ---
    return EmployeeResponse(**dict(row))


@app.get("/leave-balance/{employee_id}", response_model=LeaveBalanceResponse, tags=["휴가"])
def get_leave_balance(
    employee_id: int,
    year: int = Query(default=2025, description="조회 연도"),
) -> LeaveBalanceResponse:
    """특정 직원의 연차 잔액을 조회합니다.

    Args:
        employee_id: 직원 고유 ID
        year:        조회 연도 (기본값: 2025)

    Returns:
        연차 잔액 정보 (total_days, used_days, remaining_days 포함)

    Raises:
        HTTPException: 직원 또는 연차 데이터를 찾을 수 없을 경우 404 반환
    """
    # --- Input ---
    query = """
        SELECT
            lb.employee_id,
            e.name AS employee_name,
            lb.year,
            lb.total_days,
            lb.used_days,
            (lb.total_days - lb.used_days) AS remaining_days
        FROM leave_balance lb
        JOIN employees e ON e.id = lb.employee_id
        WHERE lb.employee_id = %s
          AND lb.year = %s;
    """

    # --- Process ---
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (employee_id, year))
            row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"직원 ID {employee_id}의 {year}년 연차 정보를 찾을 수 없습니다. "
                "직원 ID와 연도를 확인하십시오."
            ),
        )

    # --- Output ---
    return LeaveBalanceResponse(**dict(row))


@app.get("/sales/summary", response_model=list[SalesSummaryResponse], tags=["매출"])
def get_sales_summary(
    year:       Optional[int] = Query(default=None, description="조회 연도 (예: 2025)"),
    month:      Optional[int] = Query(default=None, description="조회 월 (1~12)"),
    department: Optional[str] = Query(default=None, description="부서명 필터"),
) -> list[SalesSummaryResponse]:
    """부서별 월별 매출 요약을 조회합니다.

    Args:
        year:       조회 연도. None이면 전체 연도.
        month:      조회 월 (1~12). None이면 전체 월.
        department: 부서명 필터. None이면 전체 부서.

    Returns:
        매출 요약 리스트 (달성률 포함)

    Raises:
        HTTPException: month 파라미터가 1~12 범위를 벗어날 경우 400 반환
    """
    # --- Input ---
    if month is not None and not (1 <= month <= 12):
        raise HTTPException(
            status_code=400,
            detail=f"month 파라미터는 1에서 12 사이여야 합니다. (입력값: {month})"
        )

    conditions: list[str] = []
    params: list[Any] = []

    if year:
        conditions.append("year = %s")
        params.append(year)
    if month:
        conditions.append("month = %s")
        params.append(month)
    if department:
        conditions.append("department = %s")
        params.append(department)

    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    query = f"""
        SELECT
            department,
            year,
            month,
            revenue,
            target,
            CASE
                WHEN target IS NOT NULL AND target > 0
                THEN ROUND((revenue / target * 100)::numeric, 1)
                ELSE NULL
            END AS achievement_rate
        FROM sales_monthly
        {where_clause}
        ORDER BY year DESC, month DESC, department;
    """

    # --- Process ---
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
    finally:
        conn.close()

    # --- Output ---
    return [SalesSummaryResponse(**dict(row)) for row in rows]
