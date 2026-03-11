"""
PostgreSQL DB 초기화 스크립트.

테이블 생성 및 샘플 데이터 삽입을 수행합니다.

실행:
    python -m app.database.init_db
"""

import os
import sys
from datetime import date, timedelta
import random

from dotenv import load_dotenv

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
load_dotenv()

from app.database.connection import get_db_connection


def init_db() -> None:
    """
    PostgreSQL 테이블 생성 + 샘플 데이터 삽입.

    테이블:
        employees     (id, name, dept, email, hire_date)
        leave_balance (id, employee_id, year, total, used, remaining)
        sales         (id, dept, amount, date, description)

    샘플:
        - 직원 10명 (인사팀/개발팀/영업팀/마케팅팀/기술지원팀)
        - 직원별 휴가 (연 15일, 0~10일 사용)
        - 매출 30건 (최근 90일)

    실행:
        python -m app.database.init_db
    """
    # --- Input ---
    print("=" * 55)
    print("  CH08 PostgreSQL DB 초기화")
    print("=" * 55)

    conn = get_db_connection()

    try:
        # --- Process: 테이블 생성 ---
        print("\n[1/3] 테이블 생성 중...")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id        SERIAL PRIMARY KEY,
                name      VARCHAR(50)  NOT NULL,
                dept      VARCHAR(50)  NOT NULL,
                email     VARCHAR(100) UNIQUE NOT NULL,
                hire_date DATE         NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS leave_balance (
                id          SERIAL PRIMARY KEY,
                employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
                year        INTEGER NOT NULL,
                total       INTEGER NOT NULL DEFAULT 15,
                used        NUMERIC(4,1) NOT NULL DEFAULT 0,
                remaining   NUMERIC(4,1) NOT NULL DEFAULT 15
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id          SERIAL PRIMARY KEY,
                dept        VARCHAR(50)  NOT NULL,
                amount      BIGINT       NOT NULL,
                date        DATE         NOT NULL,
                description TEXT
            )
        """)

        conn.commit()
        print("  테이블 생성 완료 (employees, leave_balance, sales)")

        # --- Process: 기존 데이터 확인 후 삽입 ---
        conn.execute("SELECT COUNT(*) AS cnt FROM employees")
        row = conn.fetchone()
        if row and row["cnt"] > 0:
            print("\n  이미 샘플 데이터가 존재합니다. 초기화를 건너뜁니다.")
            print("  데이터를 초기화하려면 테이블을 삭제 후 재실행하십시오.")
            return

        print("\n[2/3] 직원 및 휴가 데이터 삽입 중...")

        employees = [
            ("홍길동", "인사팀",   "hong@company.com",   "2020-03-02"),
            ("김철수", "개발팀",   "kim@company.com",    "2019-07-15"),
            ("이영희", "영업팀",   "lee@company.com",    "2021-01-10"),
            ("박민준", "마케팅팀", "park@company.com",   "2022-05-20"),
            ("최지원", "기술지원팀","choi@company.com",  "2018-11-01"),
            ("정수아", "개발팀",   "jung@company.com",   "2023-02-14"),
            ("강동현", "영업팀",   "kang@company.com",   "2020-08-03"),
            ("윤서연", "마케팅팀", "yoon@company.com",   "2021-10-25"),
            ("임재현", "인사팀",   "lim@company.com",    "2022-12-01"),
            ("한소희", "기술지원팀","han@company.com",   "2019-04-22"),
        ]

        current_year = date.today().year
        used_days = [5, 3, 8, 0, 10, 2, 7, 4, 1, 6]

        for i, (name, dept, email, hire_date) in enumerate(employees):
            conn.execute(
                "INSERT INTO employees (name, dept, email, hire_date) VALUES (%s, %s, %s, %s) RETURNING id",
                (name, dept, email, hire_date),
            )
            emp_row = conn.fetchone()
            emp_id = emp_row["id"]

            used = used_days[i]
            remaining = 15 - used
            conn.execute(
                "INSERT INTO leave_balance (employee_id, year, total, used, remaining) VALUES (%s, %s, %s, %s, %s)",
                (emp_id, current_year, 15, used, remaining),
            )

        conn.commit()
        print(f"  직원 {len(employees)}명 및 휴가 데이터 삽입 완료")

        # --- Process: 매출 데이터 삽입 ---
        print("\n[3/3] 매출 데이터 삽입 중...")

        depts = ["영업팀", "마케팅팀", "개발팀", "기술지원팀"]
        descriptions = [
            "신규 계약 체결",
            "갱신 계약",
            "프로젝트 납품",
            "컨설팅 수수료",
            "유지보수 계약",
            "제품 판매",
        ]

        today = date.today()
        random.seed(42)

        for i in range(30):
            dept = depts[i % len(depts)]
            amount = random.randint(100, 5000) * 10000
            sale_date = today - timedelta(days=random.randint(0, 89))
            description = descriptions[i % len(descriptions)]
            conn.execute(
                "INSERT INTO sales (dept, amount, date, description) VALUES (%s, %s, %s, %s)",
                (dept, amount, sale_date, description),
            )

        conn.commit()
        print("  매출 30건 삽입 완료")

        # --- Output ---
        print("\n" + "=" * 55)
        print("  DB 초기화 완료!")
        print("  서버 실행: python -m app.main")
        print("=" * 55)

    except Exception as exc:
        conn.rollback()
        print(f"\n오류 발생: {exc}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
