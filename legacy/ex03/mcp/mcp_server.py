"""
MCP Server: 사내 DB 도구를 LLM에게 제공하는 MCP 서버
FastMCP를 사용하여 직원, 휴가, 매출 관리 도구를 등록합니다.
"""
import sys
import os
from typing import Optional, List, Dict, Any

# 프로젝트 루트 → app 패키지 접근을 위한 경로 설정
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from mcp.server.fastmcp import FastMCP
from app.database.connection import get_db_connection
from app.database import crud

# ──────────────────────────────
# MCP 서버 인스턴스 생성
# ──────────────────────────────
mcp = FastMCP("Company DB Assistant")


# ═══════════════════════════════
# 1. 직원 관리 도구 (Employee)
# ═══════════════════════════════
@mcp.tool()
def list_employees() -> List[Dict[str, Any]]:
    """전체 직원 목록을 조회합니다."""
    conn = get_db_connection()
    try:
        return crud.list_employees(conn)
    finally:
        conn.close()


@mcp.tool()
def get_employee(employee_id: int) -> Dict[str, Any]:
    """특정 직원의 상세 정보를 조회합니다."""
    conn = get_db_connection()
    try:
        result = crud.get_employee(conn, employee_id)
        return result if result else {"error": "직원을 찾을 수 없습니다."}
    finally:
        conn.close()


@mcp.tool()
def create_employee(name: str, dept: str, email: str, hire_date: str) -> Dict[str, Any]:
    """신규 직원을 등록합니다."""
    conn = get_db_connection()
    try:
        return crud.create_employee(conn, name, dept, email, hire_date)
    finally:
        conn.close()


@mcp.tool()
def update_employee(
    employee_id: int,
    name: Optional[str] = None,
    dept: Optional[str] = None,
    email: Optional[str] = None,
    hire_date: Optional[str] = None,
) -> Dict[str, Any]:
    """직원 정보를 수정합니다."""
    conn = get_db_connection()
    try:
        result = crud.update_employee(conn, employee_id, name, dept, email, hire_date)
        return result if result else {"error": "직원을 찾을 수 없습니다."}
    finally:
        conn.close()


@mcp.tool()
def delete_employee(employee_id: int) -> Dict[str, Any]:
    """직원을 삭제합니다."""
    conn = get_db_connection()
    try:
        ok = crud.delete_employee(conn, employee_id)
        return {"deleted": ok}
    finally:
        conn.close()


# ═══════════════════════════════
# 2. 휴가 관리 도구 (Leave)
# ═══════════════════════════════
@mcp.tool()
def list_leaves() -> List[Dict[str, Any]]:
    """전체 직원의 휴가 현황을 조회합니다."""
    conn = get_db_connection()
    try:
        return crud.list_leaves(conn)
    finally:
        conn.close()


@mcp.tool()
def get_leave_balance(employee_id: int) -> Dict[str, Any]:
    """특정 직원의 잔여 휴가를 조회합니다."""
    conn = get_db_connection()
    try:
        result = crud.get_leave_by_employee(conn, employee_id)
        return result if result else {"error": "휴가 정보를 찾을 수 없습니다."}
    finally:
        conn.close()


@mcp.tool()
def use_leave(employee_id: int, days: float) -> Dict[str, Any]:
    """휴가 사용을 등록하고 잔여량을 자동 차감합니다."""
    conn = get_db_connection()
    try:
        result = crud.use_leave(conn, employee_id, days)
        return result if result else {"error": "휴가 정보를 찾을 수 없거나 오류가 발생했습니다."}
    finally:
        conn.close()


# ═══════════════════════════════
# 3. 매출 관리 도구 (Sales)
# ═══════════════════════════════
@mcp.tool()
def list_sales(limit: int = 50) -> List[Dict[str, Any]]:
    """전체 매출 내역을 조회합니다."""
    conn = get_db_connection()
    try:
        return crud.list_sales(conn, limit)
    finally:
        conn.close()


@mcp.tool()
def create_sale(dept: str, amount: int, date: str, description: Optional[str] = None) -> Dict[str, Any]:
    """매출 데이터를 입력합니다."""
    conn = get_db_connection()
    try:
        return crud.create_sale(conn, dept, amount, date, description)
    finally:
        conn.close()


@mcp.tool()
def get_sales_period(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """특정 기간별 매출을 조회합니다. 날짜 형식: YYYY-MM-DD"""
    conn = get_db_connection()
    try:
        return crud.get_sales_period(conn, start_date, end_date)
    finally:
        conn.close()


@mcp.tool()
def get_sales_by_dept(dept_name: str) -> Dict[str, Any]:
    """부서별 매출 집계 결과를 조회합니다."""
    conn = get_db_connection()
    try:
        return crud.get_sales_by_dept(conn, dept_name)
    finally:
        conn.close()


# ──────────────────────────────
# 서버 실행
# ──────────────────────────────
if __name__ == "__main__":
    mcp.run()
