# 환경 세팅 가이드 (CH04)
# pip install fastapi uvicorn psycopg2-binary sqlalchemy

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(title="안티그래비티 사내 시스템 API (임시)")

# --- [1. 가짜 데이터베이스(Mock DB) 생성] ---
# 실제로는 PostgreSQL과 연결(SQLAlchemy)되지만, 초보자 실습을 위해 In-Memory로 선언
MOCK_EMPLOYEES = [
    {"id": 1, "name": "김대리", "department": "개발팀", "vacation_days_left": 5},
    {"id": 2, "name": "박과장", "department": "영업팀", "vacation_days_left": 12},
]

MOCK_SALES = [
    {"month": "2026-01", "team": "영업팀", "revenue": 50000000},
    {"month": "2026-02", "team": "영업팀", "revenue": 75000000},
]

# --- [2. Pydantic 스키마 정의] ---
class Employee(BaseModel):
    id: int
    name: str
    department: str
    vacation_days_left: int

class SalesRank(BaseModel):
    month: str
    team: str
    revenue: int

# --- [3. API 엔드포인트 구현 (직원, 휴가, 매출)] ---

@app.get("/", tags=["기본"])
def read_root():
    return {"message": "정상적으로 베이스 시스템 API가 구동되었습니다!"}

@app.get("/api/employees", response_model=List[Employee], tags=["인사"])
def get_all_employees():
    """사내 모든 직원의 정보를 조회합니다."""
    return MOCK_EMPLOYEES

@app.get("/api/vacation/{emp_name}", tags=["인사"])
def get_vacation_by_name(emp_name: str):
    """특정 직원의 남은 연차 개수를 조회합니다."""
    for emp in MOCK_EMPLOYEES:
        if emp["name"] == emp_name:
            return {"name": emp["name"], "vacation_days_left": emp["vacation_days_left"]}
    
    return {"error": "해당 직원을 찾을 수 없습니다."}

@app.get("/api/sales", tags=["매출"])
def get_recent_sales():
    """최근 사내 매출 정보를 조회합니다."""
    return MOCK_SALES

# 서버 실행 방법
# uvicorn anti_v1_book.examples.ch04_fastapi_db.main:app --reload
