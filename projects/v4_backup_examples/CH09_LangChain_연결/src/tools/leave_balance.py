"""
CH09 LangChain 연결 전략 — 휴가 잔여 조회 도구.

@tool 데코레이터를 사용하여 LangChain Agent에서 호출 가능한 도구를 정의합니다.
PostgreSQL 연결이 없을 경우 모의(mock) 데이터로 동작합니다.
"""

import os
import logging
from typing import Union

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# --- 모의 데이터 (DB 없이 테스트 가능) ---
MOCK_EMPLOYEES: list[dict] = [
    {"id": 1, "name": "김민준", "dept": "인사팀"},
    {"id": 2, "name": "이서연", "dept": "영업팀"},
    {"id": 3, "name": "박지호", "dept": "개발팀"},
    {"id": 4, "name": "최수아", "dept": "마케팅팀"},
    {"id": 5, "name": "정우진", "dept": "영업팀"},
]

MOCK_LEAVE_BALANCE: list[dict] = [
    {"employee_id": 1, "total": 15.0, "used": 5.0, "remaining": 10.0},
    {"employee_id": 2, "total": 15.0, "used": 8.5, "remaining": 6.5},
    {"employee_id": 3, "total": 15.0, "used": 2.0, "remaining": 13.0},
    {"employee_id": 4, "total": 15.0, "used": 12.0, "remaining": 3.0},
    {"employee_id": 5, "total": 15.0, "used": 0.0, "remaining": 15.0},
]


def _query_from_db(employee_name: str) -> Union[dict, str]:
    """PostgreSQL에서 휴가 잔여 정보를 조회합니다.

    Args:
        employee_name: 조회할 직원 이름

    Returns:
        직원 휴가 정보 딕셔너리 또는 오류 문자열
    """
    try:
        import psycopg2
        import psycopg2.extras

        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            dbname=os.getenv("POSTGRES_DB", "connect_hr"),
            user=os.getenv("POSTGRES_USER", "connect_hr"),
            password=os.getenv("POSTGRES_PASSWORD", "connect_hr_pass"),
        )
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # ① 직원 ID 조회
        cursor.execute("SELECT id, dept FROM employees WHERE name = %s", (employee_name,))
        emp_row = cursor.fetchone()
        if not emp_row:
            conn.close()
            return f"직원 '{employee_name}'을(를) 찾을 수 없습니다."

        emp_id = emp_row["id"]
        dept = emp_row["dept"]

        # ② 휴가 잔여 조회
        cursor.execute(
            "SELECT total, used, remaining FROM leave_balance WHERE employee_id = %s",
            (emp_id,),
        )
        leave_row = cursor.fetchone()
        conn.close()

        if not leave_row:
            return f"'{employee_name}' 님의 휴가 정보가 존재하지 않습니다."

        return {
            "employee_name": employee_name,
            "dept": dept,
            "total_leaves": float(leave_row["total"]),
            "used_leaves": float(leave_row["used"]),
            "remaining_leaves": float(leave_row["remaining"]),
        }

    except Exception as exc:
        logger.warning("PostgreSQL 연결 실패, 모의 데이터 사용: %s", exc)
        return None  # 모의 데이터 경로로 폴백


def _query_from_mock(employee_name: str) -> Union[dict, str]:
    """모의 데이터에서 휴가 잔여 정보를 조회합니다.

    Args:
        employee_name: 조회할 직원 이름

    Returns:
        직원 휴가 정보 딕셔너리 또는 오류 문자열
    """
    # ① 직원 검색
    target_emp = next(
        (e for e in MOCK_EMPLOYEES if e["name"] == employee_name), None
    )
    if not target_emp:
        return f"직원 '{employee_name}'을(를) 찾을 수 없습니다. (조회 가능: {[e['name'] for e in MOCK_EMPLOYEES]})"

    # ② 휴가 잔여 검색
    leave = next(
        (lb for lb in MOCK_LEAVE_BALANCE if lb["employee_id"] == target_emp["id"]),
        None,
    )
    if not leave:
        return f"'{employee_name}' 님의 휴가 정보가 존재하지 않습니다."

    return {
        "employee_name": employee_name,
        "dept": target_emp["dept"],
        "total_leaves": leave["total"],
        "used_leaves": leave["used"],
        "remaining_leaves": leave["remaining"],
    }


# --- INPUT ---
@tool
def get_leave_balance(employee_name: str) -> Union[dict, str]:
    """특정 직원의 휴가 잔여일 및 사용 내역을 조회합니다.

    직원 이름을 입력하면 해당 직원의 총 휴가 일수, 사용한 휴가 일수,
    남은 휴가 일수를 반환합니다.

    Args:
        employee_name: 조회할 직원의 이름 (예: "김민준")

    Returns:
        직원 이름, 부서, 총 휴가, 사용 휴가, 잔여 휴가가 담긴 딕셔너리.
        직원을 찾을 수 없으면 오류 메시지 문자열을 반환합니다.
    """
    # --- PROCESS ---
    logger.info("[get_leave_balance] 조회 대상: %s", employee_name)

    # DB 조회 시도 → 실패 시 모의 데이터로 폴백
    result = _query_from_db(employee_name)
    if result is None:
        result = _query_from_mock(employee_name)

    # --- OUTPUT ---
    logger.info("[get_leave_balance] 결과: %s", result)
    return result
