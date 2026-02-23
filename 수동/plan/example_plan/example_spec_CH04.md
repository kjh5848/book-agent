# CH04 예제 코드 명세 — 베이스 시스템 확보

## 1. 프로젝트 유형
인프라·설명 챕터. `rag-infra` 베이스 레포 구조. CH08까지 공통으로 사용하는 PostgreSQL + FastAPI 기반 인프라.

## 2. 디렉토리 구조

```
CH04_베이스시스템확보/
├── README.md
├── docker-compose.yml        ← PostgreSQL 16 + FastAPI + pgAdmin
├── .env.example
├── init/
│   └── 01_schema_and_data.sql  ← DDL + 샘플 데이터
├── app/
│   ├── __init__.py
│   ├── main.py               ← FastAPI 앱 진입점
│   ├── database.py           ← SQLAlchemy 엔진 + 세션
│   ├── models.py             ← ORM 모델 (Employee, Leave, Sale)
│   ├── schemas.py            ← Pydantic 스키마
│   └── routers/
│       ├── __init__.py
│       ├── employees.py      ← /employees CRUD
│       ├── leaves.py         ← /leaves CRUD
│       └── sales.py          ← /sales CRUD
└── requirements.txt
```

## 3. 파일별 함수 명세

### `init/01_schema_and_data.sql`

```sql
-- 테이블 3개
CREATE TABLE employees (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  department VARCHAR(100),
  annual_leave_days INTEGER DEFAULT 15,
  used_leave_days INTEGER DEFAULT 0
);

CREATE TABLE leaves (
  id SERIAL PRIMARY KEY,
  employee_id INTEGER REFERENCES employees(id),
  start_date DATE,
  end_date DATE,
  reason TEXT,
  status VARCHAR(20) DEFAULT 'pending'  -- pending/approved/rejected
);

CREATE TABLE sales (
  id SERIAL PRIMARY KEY,
  employee_id INTEGER REFERENCES employees(id),
  department VARCHAR(100),
  amount DECIMAL(12,2),
  sale_date DATE,
  quarter VARCHAR(10)   -- '2024-Q1' 형식
);

-- 샘플 데이터: 직원 5명, 연차 기록 10건, 매출 기록 20건
```

### `app/models.py`
ORM 모델 3개: Employee, Leave, Sale (위 DDL과 1:1 대응)

### `app/routers/employees.py`
```
GET  /employees           -> List[EmployeeResponse]  직원 전체 조회
GET  /employees/{id}      -> EmployeeResponse         직원 단건 조회
GET  /employees/{id}/leave-balance -> dict            잔여 연차 조회 (MCP Tool에서 호출)
```

### `app/routers/leaves.py`
```
GET  /leaves              -> List[LeaveResponse]      연차 전체 조회
POST /leaves              -> LeaveResponse            연차 신청
PUT  /leaves/{id}/status  -> LeaveResponse            연차 승인/반려
```

### `app/routers/sales.py`
```
GET  /sales               -> List[SaleResponse]       매출 전체 조회
GET  /sales/summary       -> dict                     부서별/분기별 매출 합계 (MCP Tool에서 호출)
```

## 4. 실행 시나리오

```bash
# 1단계: 환경 설정
cp .env.example .env

# 2단계: 전체 인프라 구동 (PostgreSQL + FastAPI 동시 시작)
docker-compose up -d

# 3단계: API 동작 확인
curl http://localhost:8000/employees
curl http://localhost:8000/employees/1/leave-balance
curl http://localhost:8000/sales/summary

# 4단계: pgAdmin 접속 (선택)
# http://localhost:5050 → DB 스키마 시각적 확인
```

**기대 결과**:
- `GET /employees` → 직원 5명 목록 JSON 반환
- `GET /employees/1/leave-balance` → `{"employee_id": 1, "name": "김철수", "remaining_days": 5}`
- `GET /sales/summary` → 부서별 분기별 매출 집계

## 5. 의존성

```
# requirements.txt
fastapi>=0.111.0
uvicorn[standard]>=0.30.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.9
pydantic>=2.7.0
python-dotenv>=1.0.0
```

## 6. .env.example

```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=rag_db
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=rag_password
```

## 7. docker-compose.yml 서비스 구성

| 서비스 | 이미지 | 포트 | 역할 |
|--------|--------|------|------|
| postgres | postgres:16-alpine | 5432 | 메인 DB |
| fastapi | python:3.11-slim (build) | 8000 | CRUD API |
| pgadmin | dpage/pgadmin4 | 5050 | DB 관리 UI (선택) |

init/01_schema_and_data.sql은 postgres 컨테이너 최초 실행 시 자동 실행.
