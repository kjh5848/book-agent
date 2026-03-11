"""
FastMCP 서버 — PostgreSQL DB 도구 9개 등록.

MCPAgentService가 stdio 서브프로세스로 실행합니다.
각 도구는 app/database/crud.py 함수를 호출하고 결과를 JSON으로 반환합니다.

등록 도구:
    직원: list_employees, get_employee
    휴가: list_leaves, get_leave_balance, use_leave
    매출: list_sales, create_sale, get_sales_period, get_sales_by_dept

실행:
    python mcp/mcp_server.py
"""

import json
import os
import sys

# 프로젝트 루트 경로 추가 (app 패키지 임포트를 위해)
_MCP_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_MCP_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from dotenv import load_dotenv

load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))

from mcp.server.fastmcp import FastMCP

from app.database.connection import get_db_connection
from app.database import crud

# FastMCP 서버 인스턴스 생성
mcp = FastMCP("Company DB Assistant")


# ─── 직원 도구 ───────────────────────────────────────────────


@mcp.tool()
def list_employees() -> str:
    """
    전체 직원 목록을 조회합니다.

    Returns:
        str: 직원 정보 리스트 JSON 문자열 (id, name, dept, email, hire_date).
    """
    # --- Input ---
    # --- Process ---
    conn = get_db_connection()
    try:
        employees = crud.list_employees(conn)
        # --- Output ---
        return json.dumps(employees, ensure_ascii=False, indent=2)
    finally:
        conn.close()


@mcp.tool()
def get_employee(employee_id: int) -> str:
    """
    특정 직원의 상세 정보를 조회합니다.

    Args:
        employee_id: 조회할 직원 ID (정수).

    Returns:
        str: 직원 정보 JSON 문자열. 존재하지 않으면 에러 메시지.
    """
    # --- Input ---
    # --- Process ---
    conn = get_db_connection()
    try:
        employee = crud.get_employee(conn, employee_id)
        if not employee:
            return json.dumps({"error": f"직원 ID {employee_id}를 찾을 수 없습니다."}, ensure_ascii=False)
        # --- Output ---
        return json.dumps(employee, ensure_ascii=False, indent=2)
    finally:
        conn.close()


# ─── 휴가 도구 ───────────────────────────────────────────────


@mcp.tool()
def list_leaves() -> str:
    """
    전체 직원의 휴가 현황을 조회합니다.

    Returns:
        str: 휴가 현황 리스트 JSON 문자열 (직원명, 연도, 총/사용/잔여 일수).
    """
    # --- Input ---
    # --- Process ---
    conn = get_db_connection()
    try:
        leaves = crud.list_leaves(conn)
        # --- Output ---
        return json.dumps(leaves, ensure_ascii=False, indent=2)
    finally:
        conn.close()


@mcp.tool()
def get_leave_balance(employee_id: int) -> str:
    """
    특정 직원의 휴가 잔여 정보를 조회합니다.

    Args:
        employee_id: 조회할 직원 ID (정수).

    Returns:
        str: 휴가 잔여 정보 JSON 문자열 (총 일수, 사용 일수, 잔여 일수).
    """
    # --- Input ---
    # --- Process ---
    conn = get_db_connection()
    try:
        balance = crud.get_leave_by_employee(conn, employee_id)
        if not balance:
            return json.dumps(
                {"error": f"직원 ID {employee_id}의 휴가 정보를 찾을 수 없습니다."},
                ensure_ascii=False,
            )
        # --- Output ---
        return json.dumps(balance, ensure_ascii=False, indent=2)
    finally:
        conn.close()


@mcp.tool()
def use_leave(employee_id: int, days: float) -> str:
    """
    휴가 사용을 등록하고 잔여량을 차감합니다.

    Args:
        employee_id: 휴가를 사용할 직원 ID (정수).
        days: 사용할 휴가 일수 (소수점 허용, 예: 0.5).

    Returns:
        str: 업데이트된 휴가 정보 JSON 문자열. 잔여 부족 시 에러 메시지.
    """
    # --- Input ---
    # --- Process ---
    conn = get_db_connection()
    try:
        result = crud.use_leave(conn, employee_id, days)
        if not result:
            return json.dumps(
                {"error": f"직원 ID {employee_id}를 찾을 수 없습니다."},
                ensure_ascii=False,
            )
        # --- Output ---
        return json.dumps(result, ensure_ascii=False, indent=2)
    except ValueError as exc:
        return json.dumps({"error": str(exc)}, ensure_ascii=False)
    finally:
        conn.close()


# ─── 매출 도구 ───────────────────────────────────────────────


@mcp.tool()
def list_sales(limit: int = 10) -> str:
    """
    전체 매출 내역을 최신 순으로 조회합니다.

    Args:
        limit: 반환할 최대 건수 (기본값: 10, 최대 50).

    Returns:
        str: 매출 내역 리스트 JSON 문자열 (id, dept, amount, date, description).
    """
    # --- Input ---
    limit = min(max(1, limit), 50)
    # --- Process ---
    conn = get_db_connection()
    try:
        sales = crud.list_sales(conn, limit=limit)
        # --- Output ---
        return json.dumps(sales, ensure_ascii=False, indent=2)
    finally:
        conn.close()


@mcp.tool()
def create_sale(dept: str, amount: int, date: str, description: str = "") -> str:
    """
    새 매출 데이터를 등록합니다.

    Args:
        dept: 부서명 (예: 영업팀).
        amount: 매출 금액 (원 단위 정수).
        date: 매출 발생일 (YYYY-MM-DD 형식).
        description: 매출 설명 (선택값, 기본값: 빈 문자열).

    Returns:
        str: 생성된 매출 정보 JSON 문자열.
    """
    # --- Input ---
    desc_value = description if description else None
    # --- Process ---
    conn = get_db_connection()
    try:
        result = crud.create_sale(conn, dept, amount, date, desc_value)
        # --- Output ---
        return json.dumps(result, ensure_ascii=False, indent=2)
    finally:
        conn.close()


@mcp.tool()
def get_sales_period(start: str, end: str) -> str:
    """
    특정 기간의 매출 내역을 조회합니다.

    Args:
        start: 조회 시작일 (YYYY-MM-DD 형식).
        end: 조회 종료일 (YYYY-MM-DD 형식).

    Returns:
        str: 해당 기간 매출 내역 리스트 JSON 문자열.
    """
    # --- Input ---
    # --- Process ---
    conn = get_db_connection()
    try:
        sales = crud.get_sales_period(conn, start, end)
        # --- Output ---
        return json.dumps(sales, ensure_ascii=False, indent=2)
    finally:
        conn.close()


@mcp.tool()
def get_sales_by_dept(dept_name: str) -> str:
    """
    부서별 매출 집계 결과를 조회합니다.

    Args:
        dept_name: 조회할 부서명 (예: 영업팀, 마케팅팀, 개발팀, 기술지원팀).

    Returns:
        str: {dept, total_amount, count} 집계 결과 JSON 문자열.
    """
    # --- Input ---
    # --- Process ---
    conn = get_db_connection()
    try:
        result = crud.get_sales_by_dept(conn, dept_name)
        # --- Output ---
        return json.dumps(result, ensure_ascii=False, indent=2)
    finally:
        conn.close()


# ─── 서버 실행 ───────────────────────────────────────────────

if __name__ == "__main__":
    print("[MCP Server] 시작 — Company DB Assistant (도구 9개)", file=sys.stderr)
    mcp.run(transport="stdio")
