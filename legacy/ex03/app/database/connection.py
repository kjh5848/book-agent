import os
import psycopg2
import psycopg2.extras
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# DB_URL 가져오기 (PostgreSQL 전용)
# DB_URL 가져오기 (PostgreSQL 전용)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://metacoding:metacoding1234@localhost:5432/metacoding_db")

# SQLAlchemy Engine 생성
engine = create_engine(DATABASE_URL)

class PostgresConnectionWrapper:
    """psycopg2 연결을 직접 SQL 실행에 최적화된 형식으로 제공하는 래퍼"""
    def __init__(self, conn):
        self.conn = conn
        self.cursor_factory = psycopg2.extras.DictCursor

    def cursor(self):
        return self.conn.cursor(cursor_factory=self.cursor_factory)

    def execute(self, sql, params=None):
        cur = self.cursor()
        cur.execute(sql, params)
        return cur

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

def get_db_connection():
    """
    PostgreSQL 연결 객체를 반환하는 통합 함수.
    에이전트와 서비스들이 사용하는 메인 DB 진입점입니다.
    """
    return PostgresConnectionWrapper(engine.raw_connection())

def get_db():
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()
