"""MCP 스타일 DB 조회 도구 모듈.

LangChain @tool 데코레이터로 PostgreSQL 조회 함수를 LLM이
직접 호출 가능한 도구로 래핑합니다.
PostgreSQL 연결이 필요합니다. 미연결 시 RuntimeError가 발생합니다.

챕터 8.3: 통합 응답 전략 — DB 조회 도구 정의
"""

import os
import json
from typing import Any

from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()

# ============================================================
# DB 연결 설정
# ============================================================

DB_CONFIG: dict[str, Any] = {
    "host":     os.getenv("POSTGRES_HOST", "localhost"),
    "port":     int(os.getenv("POSTGRES_PORT", "5432")),
    "dbname":   os.getenv("POSTGRES_DB", "connecthr"),
    "user":     os.getenv("POSTGRES_USER", "admin"),
    "password": os.getenv("POSTGRES_PASSWORD", "password"),
}


def _get_db_connection():
    """PostgreSQL 연결 객체를 반환합니다.

    Returns:
        psycopg2 연결 객체

    Raises:
        RuntimeError: DB 연결 실패 시
    """

    # --- Process ---
    try:
        import psycopg2
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        raise RuntimeError(
            f"PostgreSQL에 연결할 수 없습니다: {e}\n"
            "다음 명령을 실행한 후 재시도하십시오:\n"
            "  docker-compose up -d\n"
            f"  (연결 정보: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']})"
        ) from e

    # --- Output ---
    # psycopg2 Connection 반환


# ============================================================
# MCP 스타일 도구 정의
# ============================================================

@tool
def get_employee_info(name: str) -> str:
    """직원 이름으로 직원 정보를 조회합니다.

    직원의 부서, 직급, 입사일, 기본 급여, 이메일 등
    인사 정보를 데이터베이스에서 가져옵니다.

    Args:
        name: 조회할 직원 이름 (예: '이서연')

    Returns:
        직원 정보가 담긴 JSON 문자열.
        직원이 없으면 오류 메시지 JSON.

    Raises:
        RuntimeError: PostgreSQL 연결 실패 시
    """

    # --- Input ---
    query = """
        SELECT id, name, department, position,
               hire_date::text, base_salary, email, is_active
        FROM employees
        WHERE name = %s
        LIMIT 1;
    """

    # --- Process ---
    from psycopg2.extras import RealDictCursor
    conn = _get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (name,))
            row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        return json.dumps(
            {"오류": f"'{name}' 직원을 찾을 수 없습니다."},
            ensure_ascii=False,
        )

    # --- Output ---
    return json.dumps(dict(row), ensure_ascii=False, default=str)


@tool
def get_leave_balance(employee_id: int) -> str:
    """직원 ID로 잔여 연차 정보를 조회합니다.

    지정한 직원의 총 연차일수, 사용일수, 잔여일수를
    데이터베이스에서 가져옵니다.
    직원 ID를 모르는 경우 먼저 get_employee_info로 직원 정보를 조회하십시오.

    Args:
        employee_id: 직원 고유 ID (정수)

    Returns:
        연차 잔액 정보 JSON 문자열 (총일수, 사용일수, 잔여일수).

    Raises:
        RuntimeError: PostgreSQL 연결 실패 시
    """

    # --- Input ---
    query = """
        SELECT
            e.name              AS 이름,
            lb.year             AS 연도,
            lb.total_days       AS 총_연차,
            lb.used_days        AS 사용_연차,
            (lb.total_days - lb.used_days) AS 잔여_연차
        FROM leave_balance lb
        JOIN employees e ON e.id = lb.employee_id
        WHERE lb.employee_id = %s
          AND lb.year = 2024
        ORDER BY lb.year DESC
        LIMIT 1;
    """

    # --- Process ---
    from psycopg2.extras import RealDictCursor
    conn = _get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (employee_id,))
            row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        return json.dumps(
            {"오류": f"직원 ID {employee_id}의 연차 정보가 없습니다."},
            ensure_ascii=False,
        )

    # --- Output ---
    return json.dumps(dict(row), ensure_ascii=False, default=str)


@tool
def get_department_sales(department: str, year: int, month: int) -> str:
    """특정 부서의 월별 매출 현황을 조회합니다.

    지정한 부서와 연도/월의 실제 매출, 목표 매출, 달성률을
    데이터베이스에서 가져옵니다.

    Args:
        department: 부서명 (예: '영업팀', '개발팀', '데이터팀')
        year: 조회 연도 (예: 2024)
        month: 조회 월 (1~12)

    Returns:
        매출 현황 JSON 문자열 (매출액, 목표액, 달성률).

    Raises:
        RuntimeError: PostgreSQL 연결 실패 시
    """

    # --- Input ---
    query = """
        SELECT
            department  AS 부서,
            year        AS 연도,
            month       AS 월,
            revenue     AS 매출액,
            target      AS 목표액,
            CASE
                WHEN target IS NOT NULL AND target > 0
                THEN ROUND((revenue / target * 100)::numeric, 1)
                ELSE NULL
            END AS 달성률
        FROM sales_monthly
        WHERE department = %s
          AND year = %s
          AND month = %s;
    """

    # --- Process ---
    from psycopg2.extras import RealDictCursor
    conn = _get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (department, year, month))
            row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        return json.dumps(
            {"오류": f"'{department}' {year}년 {month}월 매출 데이터가 없습니다."},
            ensure_ascii=False,
        )

    # --- Output ---
    return json.dumps(dict(row), ensure_ascii=False, default=str)


# ============================================================
# 도구 목록 (에이전트에 전달)
# ============================================================

DB_TOOLS = [get_employee_info, get_leave_balance, get_department_sales]
