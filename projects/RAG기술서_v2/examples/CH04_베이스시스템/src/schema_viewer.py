"""
DB 스키마 분석 도구 — 커넥트HR PostgreSQL 스키마 탐색기

PostgreSQL에 연결하여 테이블 목록, 컬럼 구조, 제약조건,
레코드 수를 출력하고 스키마 요약 리포트를 생성합니다.

챕터 4.2: 데이터베이스 스키마 분석
"""

import os
import sys
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from tabulate import tabulate

# 환경 변수 로딩
load_dotenv()


# ============================================================
# 상수
# ============================================================
DB_CONFIG = {
    "host":     os.getenv("POSTGRES_HOST", "localhost"),
    "port":     int(os.getenv("POSTGRES_PORT", "5432")),
    "dbname":   os.getenv("POSTGRES_DB", "connecthr"),
    "user":     os.getenv("POSTGRES_USER", "admin"),
    "password": os.getenv("POSTGRES_PASSWORD", "password"),
}

# 스키마 요약 리포트 출력 경로
REPORT_PATH = os.path.join(os.path.dirname(__file__), "..", "outputs", "schema_report.txt")


# ============================================================
# DB 연결
# ============================================================

def create_connection() -> psycopg2.extensions.connection:
    """PostgreSQL 데이터베이스에 연결하고 커넥션 객체를 반환합니다.

    Returns:
        psycopg2 커넥션 객체

    Raises:
        SystemExit: 연결 실패 시 에러 메시지 출력 후 종료
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.OperationalError as e:
        print("[오류] PostgreSQL 연결에 실패했습니다.")
        print(f"       호스트: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        print(f"       DB명:   {DB_CONFIG['dbname']}")
        print(f"       원인:   {e}")
        print()
        print("[해결 방법] docker-compose up -d 명령어로 PostgreSQL을 먼저 실행하십시오.")
        sys.exit(1)


# ============================================================
# 스키마 조회 함수
# ============================================================

def fetch_table_list(conn: psycopg2.extensions.connection) -> list[str]:
    """현재 데이터베이스의 public 스키마 테이블 목록을 반환합니다.

    Args:
        conn: psycopg2 커넥션 객체

    Returns:
        테이블명 문자열 리스트 (알파벳 순 정렬)
    """
    # --- Input ---
    query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """

    # --- Process ---
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()

    # --- Output ---
    return [row[0] for row in rows]


def fetch_column_info(
    conn: psycopg2.extensions.connection, table_name: str
) -> list[dict[str, Any]]:
    """지정 테이블의 컬럼 이름, 데이터 타입, 기본값, Null 허용 여부를 반환합니다.

    Args:
        conn: psycopg2 커넥션 객체
        table_name: 조회할 테이블 이름

    Returns:
        컬럼 정보 딕셔너리 리스트. 각 딕셔너리 키:
            - column_name: 컬럼명
            - data_type: 데이터 타입
            - column_default: 기본값
            - is_nullable: Null 허용 여부 ('YES'/'NO')
    """
    # --- Input ---
    query = """
        SELECT
            column_name,
            data_type,
            column_default,
            is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = %s
        ORDER BY ordinal_position;
    """

    # --- Process ---
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, (table_name,))
        rows = cur.fetchall()

    # --- Output ---
    return [dict(row) for row in rows]


def fetch_constraint_info(
    conn: psycopg2.extensions.connection, table_name: str
) -> list[dict[str, Any]]:
    """지정 테이블의 제약조건(PK, FK, UNIQUE, CHECK) 정보를 반환합니다.

    Args:
        conn: psycopg2 커넥션 객체
        table_name: 조회할 테이블 이름

    Returns:
        제약조건 딕셔너리 리스트. 각 딕셔너리 키:
            - constraint_name: 제약조건명
            - constraint_type: 제약조건 유형
            - column_name: 해당 컬럼명
    """
    # --- Input ---
    query = """
        SELECT
            tc.constraint_name,
            tc.constraint_type,
            kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
           AND tc.table_schema    = kcu.table_schema
        WHERE tc.table_schema = 'public'
          AND tc.table_name   = %s
        ORDER BY tc.constraint_type, kcu.column_name;
    """

    # --- Process ---
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, (table_name,))
        rows = cur.fetchall()

    # --- Output ---
    return [dict(row) for row in rows]


def fetch_row_count(
    conn: psycopg2.extensions.connection, table_name: str
) -> int:
    """지정 테이블의 전체 레코드 수를 반환합니다.

    Args:
        conn: psycopg2 커넥션 객체
        table_name: 조회할 테이블 이름

    Returns:
        레코드(행) 수
    """
    # --- Input / Process ---
    # 테이블명은 파라미터 바인딩 불가 → SQL 식별자 이스케이프 사용
    with conn.cursor() as cur:
        cur.execute(
            f'SELECT COUNT(*) FROM "{table_name}";'
        )
        result = cur.fetchone()

    # --- Output ---
    return result[0] if result else 0


# ============================================================
# 리포트 출력
# ============================================================

def print_table_schema(
    conn: psycopg2.extensions.connection, table_name: str
) -> str:
    """단일 테이블의 스키마 정보를 콘솔에 출력하고 문자열로 반환합니다.

    Args:
        conn: psycopg2 커넥션 객체
        table_name: 분석할 테이블 이름

    Returns:
        테이블 스키마 리포트 문자열
    """
    # --- Input ---
    columns     = fetch_column_info(conn, table_name)
    constraints = fetch_constraint_info(conn, table_name)
    row_count   = fetch_row_count(conn, table_name)

    # --- Process ---
    lines: list[str] = []

    # 테이블 헤더
    separator = "=" * 60
    lines.append(separator)
    lines.append(f"  테이블: {table_name}  (레코드 수: {row_count:,}건)")
    lines.append(separator)

    # 컬럼 정보
    col_headers = ["컬럼명", "데이터 타입", "기본값", "Null 허용"]
    col_rows = [
        [
            c["column_name"],
            c["data_type"],
            c["column_default"] or "-",
            c["is_nullable"],
        ]
        for c in columns
    ]
    lines.append(tabulate(col_rows, headers=col_headers, tablefmt="simple"))

    # 제약조건 정보
    if constraints:
        lines.append("")
        lines.append("[ 제약조건 ]")
        cst_headers = ["제약조건명", "유형", "컬럼"]
        cst_rows = [
            [c["constraint_name"], c["constraint_type"], c["column_name"]]
            for c in constraints
        ]
        lines.append(tabulate(cst_rows, headers=cst_headers, tablefmt="simple"))

    lines.append("")
    report_section = "\n".join(lines)

    # 콘솔 출력
    print(report_section)

    # --- Output ---
    return report_section


def generate_schema_report(conn: psycopg2.extensions.connection) -> str:
    """전체 데이터베이스 스키마 요약 리포트를 생성하고 파일로 저장합니다.

    Args:
        conn: psycopg2 커넥션 객체

    Returns:
        생성된 리포트 전문 문자열
    """
    # --- Input ---
    tables = fetch_table_list(conn)

    # --- Process ---
    report_lines: list[str] = [
        "============================================================",
        " 커넥트HR 데이터베이스 스키마 분석 리포트",
        f" 총 테이블 수: {len(tables)}개",
        "============================================================",
        "",
    ]

    for table in tables:
        section = print_table_schema(conn, table)
        report_lines.append(section)

    report_lines.append("============================================================")
    report_lines.append(" 분석 완료")
    report_lines.append("============================================================")

    full_report = "\n".join(report_lines)

    # 결과 파일 저장
    outputs_dir = os.path.dirname(REPORT_PATH)
    os.makedirs(outputs_dir, exist_ok=True)

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(full_report)

    # --- Output ---
    return full_report


# ============================================================
# 진입점
# ============================================================

def main() -> None:
    """스키마 분석 도구 메인 함수.

    PostgreSQL에 연결하여 전체 스키마를 분석하고
    outputs/schema_report.txt 파일로 저장합니다.
    """
    print("커넥트HR 데이터베이스 스키마 분석을 시작합니다...\n")

    conn = create_connection()
    try:
        generate_schema_report(conn)
        print(f"\n리포트가 저장되었습니다: {REPORT_PATH}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
