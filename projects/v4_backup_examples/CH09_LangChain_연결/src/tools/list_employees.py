"""
CH09 LangChain 연결 전략 — 직원 목록 조회 도구.

@tool 데코레이터를 사용하여 LangChain Agent에서 호출 가능한 도구를 정의합니다.
부서별 직원 목록을 PostgreSQL 또는 모의 데이터에서 조회합니다.
"""

import os
import logging
from typing import Optional, Union

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# --- 모의 데이터 (DB 없이 테스트 가능) ---
MOCK_EMPLOYEES: list[dict] = [
    {"id": 1, "name": "김민준", "dept": "인사팀", "email": "minjun@company.com", "hire_date": "2022-03-01"},
    {"id": 2, "name": "이서연", "dept": "영업팀", "email": "seoyeon@company.com", "hire_date": "2021-07-15"},
    {"id": 3, "name": "박지호", "dept": "개발팀", "email": "jiho@company.com", "hire_date": "2023-01-10"},
    {"id": 4, "name": "최수아", "dept": "마케팅팀", "email": "sua@company.com", "hire_date": "2020-11-01"},
    {"id": 5, "name": "정우진", "dept": "영업팀", "email": "woojin@company.com", "hire_date": "2022-06-20"},
    {"id": 6, "name": "한예린", "dept": "개발팀", "email": "yerin@company.com", "hire_date": "2023-09-01"},
    {"id": 7, "name": "오동현", "dept": "인사팀", "email": "donghyun@company.com", "hire_date": "2019-04-15"},
]


def _query_from_db(dept: Optional[str] = None) -> Union[list[dict], None]:
    """PostgreSQL에서 직원 목록을 조회합니다.

    Args:
        dept: 조회할 부서명. None이면 전체 직원 목록을 반환합니다.

    Returns:
        직원 정보 딕셔너리 목록 또는 None (연결 실패 시)
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

        if dept:
            # ① 부서 필터 적용
            cursor.execute(
                "SELECT id, name, dept, email, hire_date FROM employees WHERE dept = %s ORDER BY id",
                (dept,),
            )
        else:
            # ② 전체 직원 조회
            cursor.execute(
                "SELECT id, name, dept, email, hire_date FROM employees ORDER BY id"
            )

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    except Exception as exc:
        logger.warning("PostgreSQL 연결 실패, 모의 데이터 사용: %s", exc)
        return None


def _query_from_mock(dept: Optional[str] = None) -> Union[list[dict], str]:
    """모의 데이터에서 직원 목록을 조회합니다.

    Args:
        dept: 조회할 부서명. None이면 전체 직원 목록을 반환합니다.

    Returns:
        직원 정보 딕셔너리 목록 또는 오류 문자열
    """
    if dept:
        # ① 부서 필터 적용
        filtered = [e for e in MOCK_EMPLOYEES if dept in e["dept"]]
        if not filtered:
            available_depts = list({e["dept"] for e in MOCK_EMPLOYEES})
            return f"'{dept}' 부서를 찾을 수 없습니다. 존재하는 부서: {available_depts}"
        return filtered

    # ② 전체 직원 반환
    return MOCK_EMPLOYEES


# --- INPUT ---
@tool
def list_employees(dept: Optional[str] = None) -> Union[list[dict], str]:
    """직원 목록을 조회합니다.

    부서명을 지정하면 해당 부서의 직원만, 지정하지 않으면 전체 직원 목록을 반환합니다.
    각 직원의 이름, 소속 부서, 이메일, 입사일 정보가 포함됩니다.

    Args:
        dept: 조회할 부서명 (예: "영업팀", "인사팀"). None이면 전체 직원을 조회합니다.

    Returns:
        직원 정보 딕셔너리 목록. 부서를 찾을 수 없으면 오류 메시지 문자열을 반환합니다.
    """
    # --- PROCESS ---
    logger.info("[list_employees] 조회 대상 부서: %s", dept or "전체")

    # DB 조회 시도 → 실패 시 모의 데이터로 폴백
    result = _query_from_db(dept)
    if result is None:
        result = _query_from_mock(dept)

    # --- OUTPUT ---
    count = len(result) if isinstance(result, list) else 0
    logger.info("[list_employees] 조회된 직원 수: %d", count)
    return result
