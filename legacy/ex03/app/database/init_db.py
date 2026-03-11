import random
import os
import sys
from datetime import datetime, timedelta

# 패키지 내 상대 경로 임포트가 어렵다면 절대 경로 추가
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from database.connection import get_db_connection

def init_db():
    print("🚀 PostgreSQL 데이터베이스 초기화 시작...")
    conn = get_db_connection()
    cursor = conn.cursor()

    # 기존 테이블 삭제 (초기화용)
    cursor.execute('DROP TABLE IF EXISTS sales CASCADE')
    cursor.execute('DROP TABLE IF EXISTS leave_balance CASCADE')
    cursor.execute('DROP TABLE IF EXISTS employees CASCADE')

    # 1. 직원 테이블 (employees)
    cursor.execute('''
    CREATE TABLE employees (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        dept TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        hire_date TEXT NOT NULL
    )
    ''')

    # 2. 휴가 테이블 (leave_balance)
    cursor.execute('''
    CREATE TABLE leave_balance (
        id SERIAL PRIMARY KEY,
        employee_id INTEGER,
        year INTEGER NOT NULL,
        total REAL NOT NULL,
        used REAL DEFAULT 0,
        remaining REAL NOT NULL,
        FOREIGN KEY (employee_id) REFERENCES employees (id)
    )
    ''')

    # 3. 매출 테이블 (sales)
    cursor.execute('''
    CREATE TABLE sales (
        id SERIAL PRIMARY KEY,
        dept TEXT NOT NULL,
        amount INTEGER NOT NULL,
        date TEXT NOT NULL,
        description TEXT
    )
    ''')

    print("✅ 테이블 생성 완료: employees, leave_balance, sales")

    # --- 샘플 데이터 삽입 ---
    departments = ['인사팀', '개발팀', '영업팀', '마케팅팀', '기술지원팀']
    names = ['홍길동', '이민수', '박지은', '최동훈', '정소연', '한지형', '윤준호', '송미경', '조현우', '강민주']

    # 1. 직원 데이터
    employees_data = []
    for i, name in enumerate(names):
        dept = random.choice(departments)
        email = f"user{i+1}@metacoding.com"
        hire_date = (datetime.now() - timedelta(days=random.randint(300, 2000))).strftime('%Y-%m-%d')
        employees_data.append((name, dept, email, hire_date))

    cursor.executemany('INSERT INTO employees (name, dept, email, hire_date) VALUES (%s, %s, %s, %s)', employees_data)
    print(f"✅ 직원 데이터 {len(employees_data)}건 생성")

    # 2. 휴가 데이터
    cursor.execute('SELECT id FROM employees')
    emp_ids = [row[0] for row in cursor.fetchall()]

    leave_data = []
    for emp_id in emp_ids:
        total = 15.0
        used = float(random.randint(0, 10))
        remaining = total - used
        year = 2024
        leave_data.append((emp_id, year, total, used, remaining))

    cursor.executemany('INSERT INTO leave_balance (employee_id, year, total, used, remaining) VALUES (%s, %s, %s, %s, %s)', leave_data)
    print(f"✅ 휴가 데이터 {len(leave_data)}건 생성")

    # 3. 매출 데이터
    sales_data = []
    for _ in range(30):
        dept = random.choice(departments)
        amount = random.randint(100, 5000) * 10000
        date = (datetime.now() - timedelta(days=random.randint(0, 90))).strftime('%Y-%m-%d')
        desc = f"{dept} {random.choice(['Q1 프로젝트', '유지보수 계약', '신규 라이선스', '컨설팅'])} 수입"
        sales_data.append((dept, amount, date, desc))

    cursor.executemany('INSERT INTO sales (dept, amount, date, description) VALUES (%s, %s, %s, %s)', sales_data)
    print(f"✅ 매출 데이터 {len(sales_data)}건 생성")

    conn.commit()
    conn.close()
    print("🚀 PostgreSQL 데이터베이스 초기화 완료")

if __name__ == "__main__":
    init_db()
