# CH04 베이스 시스템 확보

> AI 업무 비서 구축: RAG + MCP 실전 가이드 - 4장 실습 코드

## 목적 및 학습 목표

- PostgreSQL + FastAPI 기반 인프라를 Docker Compose 한 명령으로 구동하는 방법을 익힙니다.
- 직원(employees), 연차(leaves), 매출(sales) 테이블의 스키마와 관계를 이해합니다.
- CRUD API 엔드포인트의 요청/응답 형식을 Swagger UI로 직접 확인합니다.
- 이 인프라는 5장부터 8장까지 모든 실습의 공통 백엔드로 사용됩니다.

## 전체 구조

```mermaidrm test-category.js test-coupang.js test-redirect.js
graph TD
    A[docker-compose up] --> B[postgres:16-alpine\n포트 5432]
    A --> C[FastAPI CRUD 서버\n포트 8000]
    B --> D[init/01_schema_and_data.sql\n테이블 생성 + 샘플 데이터]
    C --> E[GET /employees]
    C --> F[GET /leaves]
    C --> G[GET /sales/summary]
    C --> H[Swagger UI\nlocalhost:8000/docs]
```

## 디렉토리 구조

```
CH04_베이스시스템확보/
├── README.md
├── docker-compose.yml          ← PostgreSQL 16 + FastAPI 서비스 정의
├── Dockerfile                  ← FastAPI 컨테이너 빌드 설정
├── .env.example                ← 환경 변수 템플릿
├── requirements.txt            ← Python 의존성 (버전 고정)
├── init/
│   └── 01_schema_and_data.sql  ← DDL + 샘플 데이터 (자동 실행)
└── app/
    ├── __init__.py
    ├── main.py                 ← FastAPI 앱 진입점
    ├── database.py             ← SQLAlchemy 엔진 + 세션
    ├── models.py               ← ORM 모델 (Employee, Leave, Sale)
    ├── schemas.py              ← Pydantic v2 스키마
    └── routers/
        ├── __init__.py
        ├── employees.py        ← /employees CRUD
        ├── leaves.py           ← /leaves CRUD
        └── sales.py            ← /sales 조회 + 집계
```

## 실행 환경

- Docker 24.0+
- Docker Compose V2 (`docker compose` 또는 `docker-compose`)
- curl 또는 웹 브라우저 (API 테스트용)

## 사전 준비

Docker가 실행 중인지 확인합니다.

```bash
docker --version
docker compose version
```

## 설치 및 실행

### 1단계 — 환경 변수 설정

저장소 루트 폴더로 이동한 뒤 환경 변수 파일을 복사합니다.

```bash
cp .env.example .env
```

`.env` 파일의 기본값을 그대로 사용해도 실습에 문제가 없습니다.

### 2단계 — 전체 인프라 구동

Docker Compose로 PostgreSQL과 FastAPI를 백그라운드에서 실행합니다.

```bash
docker-compose up -d
```

최초 실행 시 이미지를 다운로드하고 빌드하므로 2~5분 정도 소요될 수 있습니다.

### 3단계 — 서비스 상태 확인

두 컨테이너가 모두 `Up` 상태인지 확인합니다.

```bash
docker-compose ps
```

### macOS / Linux — API 동작 확인

```bash
# 직원 전체 조회
curl http://localhost:8000/employees

# 특정 직원 조회
curl http://localhost:8000/employees/1

# 직원 잔여 연차 조회
curl http://localhost:8000/employees/1/leave-balance

# 연차 전체 조회
curl http://localhost:8000/leaves

# 매출 전체 조회
curl http://localhost:8000/sales

# 부서별 분기별 매출 합계
curl http://localhost:8000/sales/summary
```

### Windows (PowerShell) — API 동작 확인

```powershell
# 직원 전체 조회
Invoke-RestMethod -Uri "http://localhost:8000/employees"

# 직원 잔여 연차 조회
Invoke-RestMethod -Uri "http://localhost:8000/employees/1/leave-balance"

# 부서별 분기별 매출 합계
Invoke-RestMethod -Uri "http://localhost:8000/sales/summary"
```

## API 엔드포인트 목록

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/` | 서버 상태 확인 |
| GET | `/health` | 헬스체크 |
| GET | `/employees` | 직원 전체 조회 |
| GET | `/employees/{id}` | 직원 단건 조회 |
| GET | `/employees/{id}/leave-balance` | 직원 잔여 연차 조회 |
| GET | `/leaves` | 연차 전체 조회 |
| POST | `/leaves` | 연차 신청 |
| PUT | `/leaves/{id}/status` | 연차 승인/반려 |
| GET | `/sales` | 매출 전체 조회 |
| GET | `/sales/summary` | 부서별/분기별 매출 합계 |

Swagger UI에서 모든 엔드포인트를 직접 테스트할 수 있습니다.

```
http://localhost:8000/docs
```

<!-- [캡처 사진 삽입 위치: 브라우저에서 localhost:8000/docs 를 열었을 때의 Swagger UI 전체 화면] -->

## 예상 결과

### GET /employees

<!-- [캡처 사진 삽입 위치: curl http://localhost:8000/employees 터미널 전체 출력 화면] -->

```json
[
  {"id": 1, "name": "김철수", "department": "영업부", "annual_leave_days": 15, "used_leave_days": 10},
  {"id": 2, "name": "이영희", "department": "인사부", "annual_leave_days": 15, "used_leave_days": 8},
  {"id": 3, "name": "박민준", "department": "개발부", "annual_leave_days": 15, "used_leave_days": 0},
  {"id": 4, "name": "최수정", "department": "마케팅부", "annual_leave_days": 15, "used_leave_days": 5},
  {"id": 5, "name": "정대현", "department": "영업부", "annual_leave_days": 15, "used_leave_days": 3}
]
```

### GET /employees/1/leave-balance

<!-- [캡처 사진 삽입 위치: curl http://localhost:8000/employees/1/leave-balance 터미널 출력 화면] -->

```json
{
  "employee_id": 1,
  "name": "김철수",
  "annual_leave_days": 15,
  "used_leave_days": 10,
  "remaining_days": 5
}
```

> **주의**: 위 출력은 실제 실행 결과를 그대로 복사한 것입니다. 독자의 터미널 출력과 한 글자씩 비교하여 디버깅하십시오.

### GET /sales/summary

<!-- [캡처 사진 삽입 위치: curl http://localhost:8000/sales/summary 터미널 출력 화면] -->

```json
{
  "결과": [
    {"department": "개발부", "quarter": "2025-Q2", "total_amount": 7700000.0},
    {"department": "마케팅부", "quarter": "2024-Q4", "total_amount": 24600000.0},
    {"department": "마케팅부", "quarter": "2025-Q1", "total_amount": 25300000.0},
    {"department": "영업부", "quarter": "2024-Q4", "total_amount": 15800000.0},
    {"department": "영업부", "quarter": "2025-Q1", "total_amount": 14000000.0},
    {"department": "영업부", "quarter": "2025-Q2", "total_amount": 5600000.0},
    {"department": "인사부", "quarter": "2025-Q2", "total_amount": 2700000.0}
  ]
}
```

## 샘플 데이터 설명

### 직원 (5명)

| id | 이름 | 부서 | 연차 부여 | 연차 사용 | 잔여 |
|----|------|------|----------|----------|------|
| 1 | 김철수 | 영업부 | 15일 | 10일 | **5일** |
| 2 | 이영희 | 인사부 | 15일 | 8일 | 7일 |
| 3 | 박민준 | 개발부 | 15일 | 0일 | 15일 |
| 4 | 최수정 | 마케팅부 | 15일 | 5일 | 10일 |
| 5 | 정대현 | 영업부 | 15일 | 3일 | 12일 |

### 연차 신청 (10건)

- 승인(approved) 7건, 대기(pending) 2건, 반려(rejected) 1건

### 매출 기록 (20건)

- 기간: 2024-Q4, 2025-Q1, 2025-Q2
- 부서: 영업부, 마케팅부, 인사부, 개발부

## 종료

서비스를 종료합니다.

```bash
# 컨테이너만 종료 (데이터 유지)
docker-compose down

# 컨테이너 + 볼륨 모두 삭제 (데이터 초기화)
docker-compose down -v
```

## 자주 묻는 질문

**Q. `docker-compose up` 후 FastAPI가 바로 응답하지 않습니다.**
A. PostgreSQL의 헬스체크 통과 후 FastAPI가 시작됩니다. 약 15~30초 대기 후 다시 시도하십시오.

**Q. `connection refused` 오류가 발생합니다.**
A. `docker-compose ps` 명령으로 두 컨테이너가 모두 `Up` 상태인지 확인하십시오.

**Q. 데이터를 초기 상태로 되돌리고 싶습니다.**
A. `docker-compose down -v` 후 `docker-compose up -d` 를 실행하면 SQL 파일이 다시 자동으로 실행됩니다.
