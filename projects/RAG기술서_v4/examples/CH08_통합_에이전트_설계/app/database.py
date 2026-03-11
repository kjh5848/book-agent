"""데이터베이스 연결 모듈.

PostgreSQL 연결을 관리한다.
정형 데이터 조회를 위해 PostgreSQL 연결은 필수이다.

IPO 패턴:
  Input  - 환경 변수 (POSTGRES_HOST, PORT, DB, USER, PASSWORD)
  Process - psycopg2 연결 시도, 실패 시 None 반환
  Output - DB 연결 객체 또는 None
"""

from __future__ import annotations

import os
from typing import Optional

# ---------------------------------------------------------------------------
# 1. 연결 설정
# ---------------------------------------------------------------------------

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "rag_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "rag_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "rag_password")

DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)


# ---------------------------------------------------------------------------
# 2. 연결 래퍼 클래스
# ---------------------------------------------------------------------------

class _DbConnectionWrapper:
    """psycopg2 연결 객체를 DictCursor와 함께 래핑한다."""

    def __init__(self, conn) -> None:
        """연결 객체를 초기화한다."""
        self._conn = conn

    def execute(self, sql: str, params: tuple = ()) -> list[dict]:
        """SQL을 실행하고 딕셔너리 리스트를 반환한다."""
        import psycopg2.extras
        cur = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params)
        rows = [dict(row) for row in cur.fetchall()]
        cur.close()
        return rows

    def close(self) -> None:
        """연결을 종료한다."""
        self._conn.close()


# ---------------------------------------------------------------------------
# 3. 연결 함수
# ---------------------------------------------------------------------------

def get_db_connection() -> _DbConnectionWrapper:
    """PostgreSQL 연결을 반환한다. 실패 시 SystemExit을 발생시킨다.

    Returns:
        _DbConnectionWrapper 인스턴스.

    Raises:
        SystemExit: DB 연결에 실패한 경우.
    """
    try:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=5)
        return _DbConnectionWrapper(conn)
    except Exception as e:
        raise SystemExit(f"PostgreSQL 연결 실패: {e}\n.env 파일의 POSTGRES_* 설정을 확인하세요.") from e


def get_db_connection_safe() -> Optional[_DbConnectionWrapper]:
    """PostgreSQL 연결을 시도하고 실패 시 None을 반환한다.

    connect_timeout=3으로 빠른 실패를 보장한다.

    Returns:
        _DbConnectionWrapper 인스턴스 또는 None (연결 실패 시).
    """
    try:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=3)  # ①
        return _DbConnectionWrapper(conn)
    except Exception:
        return None  # ② 연결 실패
