"""
CH09 LangChain 연결 전략 — 직원 목록 조회 도구.

@tool 데코레이터를 사용하여 LangChain Agent에서 호출 가능한 도구를 정의합니다.
PostgreSQL에서 부서별 직원 목록을 조회합니다 (docker-compose up -d 필요).
"""

import os
import logging
from typing import Optional, Union

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

_DB_ERROR_MSG = (
    "PostgreSQL에 연결할 수 없습니다. "
    "docker-compose up -d 로 DB를 시작한 후 다시 시도하십시오."
)


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

        db_url = os.getenv("DATABASE_URL", "")
        if not db_url:
            host = os.getenv("POSTGRES_HOST", "localhost")
            port = os.getenv("POSTGRES_PORT", "5432")
            db = os.getenv("POSTGRES_DB", "rag_db")
            user = os.getenv("POSTGRES_USER", "rag_user")
            password = os.getenv("POSTGRES_PASSWORD", "")
            db_url = f"postgresql://{user}:{password}@{host}:{port}/{db}"

        conn = psycopg2.connect(db_url, connect_timeout=3)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        if dept:
            # ① 부서 필터 적용
            cursor.execute(
                "SELECT emp_no, name, department, position, hire_date FROM employees WHERE department LIKE %s ORDER BY name",
                (f"%{dept}%",),
            )
        else:
            # ② 전체 직원 조회
            cursor.execute(
                "SELECT emp_no, name, department, position, hire_date FROM employees ORDER BY department, name"
            )

        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    except Exception as exc:
        logger.warning("PostgreSQL 연결 실패: %s", exc)
        return None


# --- INPUT ---
@tool
def list_employees(dept: Optional[str] = None) -> Union[list[dict], dict]:
    """직원 목록을 조회합니다.

    부서명을 지정하면 해당 부서의 직원만, 지정하지 않으면 전체 직원 목록을 반환합니다.
    각 직원의 이름, 소속 부서, 직급, 입사일 정보가 포함됩니다.

    Args:
        dept: 조회할 부서명 (예: "영업부", "인사부"). None이면 전체 직원을 조회합니다.

    Returns:
        직원 정보 딕셔너리 목록. DB 연결 실패 시 오류 딕셔너리를 반환합니다.
    """
    # --- PROCESS ---
    logger.info("[list_employees] 조회 대상 부서: %s", dept or "전체")

    # DB 조회 시도
    result = _query_from_db(dept)
    if result is None:
        return {"error": _DB_ERROR_MSG, "employees": [], "count": 0}

    # --- OUTPUT ---
    count = len(result)
    logger.info("[list_employees] 조회된 직원 수: %d", count)
    return result
