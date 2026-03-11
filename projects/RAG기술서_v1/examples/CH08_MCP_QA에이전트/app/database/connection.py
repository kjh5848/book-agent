"""
PostgreSQL 연결 모듈.

psycopg2 + SQLAlchemy Engine을 함께 사용합니다.
SQLAlchemy는 Engine 획득에만 사용하고,
실제 쿼리는 psycopg2 DictCursor로 직접 실행합니다.

환경 변수:
    DATABASE_URL: PostgreSQL 연결 URL
        기본값: postgresql://company:company1234@localhost:5432/company_db
"""

import os

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://company:company1234@localhost:5432/company_db",
)

engine = create_engine(DATABASE_URL)


class PostgresConnectionWrapper:
    """psycopg2 연결을 DictCursor 기반으로 래핑합니다.

    Attributes:
        conn: psycopg2 연결 객체.
        cursor: DictCursor 커서 객체.
    """

    def __init__(self, conn: psycopg2.extensions.connection) -> None:
        """
        psycopg2 연결과 DictCursor를 초기화합니다.

        Args:
            conn: psycopg2 연결 객체.
        """
        self.conn = conn
        self.cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def execute(self, query: str, params: tuple | None = None) -> None:
        """
        SQL 쿼리를 실행합니다.

        Args:
            query: 실행할 SQL 문자열.
            params: 바인딩 파라미터 튜플 (기본값: None).
        """
        # --- Input ---
        # --- Process ---
        self.cursor.execute(query, params)
        # --- Output ---

    def fetchall(self) -> list[dict]:
        """
        이전 쿼리 결과 전체를 딕셔너리 리스트로 반환합니다.

        Returns:
            list[dict]: 조회된 행의 딕셔너리 리스트.
        """
        # --- Input ---
        # --- Process ---
        rows = self.cursor.fetchall()
        # --- Output ---
        return [dict(row) for row in rows]

    def fetchone(self) -> dict | None:
        """
        이전 쿼리 결과에서 첫 번째 행을 딕셔너리로 반환합니다.

        Returns:
            dict | None: 첫 번째 행의 딕셔너리, 결과 없으면 None.
        """
        # --- Input ---
        # --- Process ---
        row = self.cursor.fetchone()
        # --- Output ---
        return dict(row) if row else None

    def commit(self) -> None:
        """현재 트랜잭션을 커밋합니다."""
        self.conn.commit()

    def rollback(self) -> None:
        """현재 트랜잭션을 롤백합니다."""
        self.conn.rollback()

    def close(self) -> None:
        """커서와 연결을 닫습니다."""
        self.cursor.close()
        self.conn.close()


def get_db_connection() -> PostgresConnectionWrapper:
    """
    SQLAlchemy raw_connection()을 PostgresConnectionWrapper로 반환합니다.

    Returns:
        PostgresConnectionWrapper: DictCursor 기반 PostgreSQL 연결 래퍼.

    Raises:
        Exception: PostgreSQL 연결에 실패한 경우.
    """
    # --- Input ---
    # --- Process ---
    try:
        raw_conn = engine.raw_connection()
        # --- Output ---
        return PostgresConnectionWrapper(raw_conn)
    except Exception as exc:
        raise Exception(
            f"PostgreSQL 연결에 실패했습니다. "
            f"docker-compose up -d 명령으로 컨테이너를 실행하십시오. 오류: {exc}"
        ) from exc
