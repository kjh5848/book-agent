"""
샘플 데이터 적재 스크립트 — 커넥트HR 베이스 시스템

Docker Compose로 PostgreSQL을 실행하면 schema.sql이 자동 적재됩니다.
이 스크립트는 추가 샘플 데이터를 수동으로 재적재하거나
데이터를 초기화할 때 사용합니다.

실행 방법:
    python scripts/seed_data.py

챕터 4.1: 사내 시스템 git clone으로 확보
"""

import os
import sys

import psycopg2
from dotenv import load_dotenv

# 프로젝트 루트를 PYTHONPATH에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

load_dotenv()


# ============================================================
# DB 설정
# ============================================================

DB_CONFIG = {
    "host":     os.getenv("POSTGRES_HOST", "localhost"),
    "port":     int(os.getenv("POSTGRES_PORT", "5432")),
    "dbname":   os.getenv("POSTGRES_DB", "connecthr"),
    "user":     os.getenv("POSTGRES_USER", "admin"),
    "password": os.getenv("POSTGRES_PASSWORD", "password"),
}

# schema.sql 경로
SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "..", "docs", "schema.sql")


# ============================================================
# 적재 함수
# ============================================================

def load_schema_sql(conn: psycopg2.extensions.connection) -> None:
    """schema.sql 파일을 읽어 PostgreSQL에 실행합니다.

    Args:
        conn: psycopg2 커넥션 객체

    Raises:
        FileNotFoundError: schema.sql 파일이 없을 경우
        psycopg2.Error: SQL 실행 오류
    """
    # --- Input ---
    schema_path = os.path.abspath(SCHEMA_FILE)
    if not os.path.exists(schema_path):
        raise FileNotFoundError(
            f"schema.sql 파일을 찾을 수 없습니다: {schema_path}"
        )

    with open(schema_path, "r", encoding="utf-8") as f:
        sql = f.read()

    # --- Process ---
    print(f"[진행] schema.sql 적재 중: {schema_path}")
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()

    # --- Output ---
    print("[완료] schema.sql 적재 완료")


def verify_data(conn: psycopg2.extensions.connection) -> None:
    """적재된 샘플 데이터 건수를 검증하고 출력합니다.

    Args:
        conn: psycopg2 커넥션 객체
    """
    # --- Input ---
    tables = ["employees", "leave_requests", "leave_balance", "sales_monthly"]

    # --- Process / Output ---
    print("\n[검증] 적재된 데이터 확인:")
    with conn.cursor() as cur:
        for table in tables:
            cur.execute(f'SELECT COUNT(*) FROM "{table}";')
            count = cur.fetchone()[0]
            print(f"  - {table}: {count:>3}건")


# ============================================================
# 진입점
# ============================================================

def main() -> None:
    """샘플 데이터 적재 메인 함수.

    PostgreSQL에 연결하여 schema.sql을 실행하고
    적재된 데이터 건수를 검증합니다.
    """
    print("커넥트HR 샘플 데이터 적재를 시작합니다...")
    print(f"대상 DB: {DB_CONFIG['dbname']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print()

    # DB 연결
    try:
        conn = psycopg2.connect(**DB_CONFIG)
    except psycopg2.OperationalError as e:
        print("[오류] PostgreSQL 연결 실패.")
        print(f"       원인: {e}")
        print("       docker-compose up -d 를 먼저 실행하십시오.")
        sys.exit(1)

    try:
        load_schema_sql(conn)
        verify_data(conn)
    finally:
        conn.close()

    print("\n[완료] 샘플 데이터 적재가 완료되었습니다.")


if __name__ == "__main__":
    main()
