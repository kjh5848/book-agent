# CH04 베이스 시스템 확보 — 실습 보고서

> 작성일: 2026-02-26 | 환경: macOS Darwin 25.3.0 | Python 3.14.3 | 실습자: 학생 관점 검토

---

## 1. 실습 개요

| 항목 | 내용 |
|------|------|
| 챕터 | CH04 베이스 시스템 확보 |
| 핵심 기술 | PostgreSQL 16 (Docker), FastAPI, psycopg2, MCP @tool 패턴 |
| 실습 목표 | DB 스키마 분석 + FastAPI CRUD API + MCP 개념 체험 |
| 예상 소요 시간 | 약 20~30분 |
| 실제 소요 시간 | 약 15분 (코드 정적 분석, Docker SKIP) |

---

## 2. 환경 설정

### 2-1. 필수 조건 확인

| 항목 | 요구사항 | 실제 버전/상태 | 결과 |
|------|---------|--------------|------|
| Python | 3.11+ | 3.14.3 | PASS |
| Docker | 실행 중 | 미설치 | FAIL (SKIP) |
| Ollama | 선택 (MCP 데모용) | 실행 중 | PASS |
| psycopg2 | 설치 필요 | requirements.txt 포함 | PASS (정적) |

### 2-2. 의존성 설치

**명령어:**
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

**결과:**
```
requirements.txt 주요 패키지: psycopg2-binary, fastapi, uvicorn,
                             python-dotenv, sqlalchemy
결과: PASS (정적 분석)
```

> 설치된 주요 패키지: 약 30개 | 결과: PASS (정적 분석)

---

## 3. 단계별 실습

### STEP 1: Docker Compose로 PostgreSQL 구동

**명령어:**
```bash
docker-compose up -d
```

**실행 결과:**
```
Error: Docker 미설치 환경에서 실행 불가
```

**결과:** SKIP (Docker 미설치)
> README에 PostgreSQL Healthy 확인 방법 안내. pgAdmin 접속 팁도 포함.

---

### STEP 2: DB 스키마 분석

**명령어:**
```bash
python src/main.py schema
```

**결과:** SKIP (DB 의존), PASS (코드 검증)
> `src/schema_viewer.py`의 `fetch_table_list()`: 챕터 발췌와 일치. 4개 테이블 구조(employees, leave_requests, leave_balance, sales_monthly) 코드 정의 확인.

---

### STEP 3: FastAPI CRUD 서버 실행

**명령어:**
```bash
uvicorn src.crud_api:app --reload --port 8000
```

**결과:** SKIP (DB 의존), PASS (코드 검증)
> 5개 엔드포인트 (GET /health, /employees, /employees/{id}, /leave-balance/{id}, /sales/summary) 코드 구현 확인.

---

### STEP 4: MCP 데모 실행

**명령어:**
```bash
python src/main.py mcp
```

**결과:** SKIP (DB 의존), PASS (코드 검증)
> `src/mcp_intro.py`의 `@tool get_leave_balance` 함수 챕터 발췌와 일치. 도구 3개 정의 확인.

---

## 4. 기능 검증

### API 엔드포인트 테스트

| 엔드포인트 | 요청 | 응답 코드 | 결과 |
|-----------|------|---------|------|
| GET /health | curl localhost:8000/health | 200 | SKIP (DB 없음) |
| GET /employees | curl localhost:8000/employees | 200 | SKIP (DB 없음) |
| GET /leave-balance/1 | curl localhost:8000/leave-balance/1 | 200 | SKIP (DB 없음) |

### 핵심 기능 시나리오

| 시나리오 | 입력 | 기대 출력 | 실제 출력 | 결과 |
|---------|------|---------|---------|------|
| 스키마 조회 | python src/main.py schema | 4개 테이블 정보 | SKIP (DB 없음) | SKIP |
| MCP 도구 호출 | get_leave_balance(1) | 연차 잔액 조회 | SKIP (DB 없음) | SKIP |

---

## 5. 오류 해결 내역

| # | 오류 내용 | 원인 | 해결 방법 | 결과 |
|---|---------|------|---------|------|
| 1 | 모든 DB 관련 기능 SKIP | Docker 미설치 | Docker Desktop 설치 필요 | 미해결(환경 제한) |

---

## 6. 종합 평가

### 점수표

| 평가 항목 | 점수 (5점 만점) | 근거 |
|---------|--------------|------|
| 환경 설정 난이도 | 2 | Docker 없으면 실습 전체 막힘. SQLite 대안 없음 |
| 실행 성공률 | 1 | 4단계 중 0단계 성공 (Docker 필수). 코드 검증만 가능 |
| 코드 이해도 | 5 | schema_viewer, crud_api, mcp_intro 모두 docstring 완비. IPO 패턴 일관 적용 |
| 문서화 품질 | 4 | README에 실행 예시, pgAdmin 팁, 파일 구조 포함. Docker 없는 대안 미제공 |
| **총점** | **12/20** | FAIR |

### 학생 의견

> "DB 스키마 분석부터 FastAPI API 구성, MCP 도구 개념까지 실제 업무 환경을 잘 시뮬레이션한 챕터이나, Docker가 없으면 어떤 단계도 실제로 실행할 수 없어 실습 가치가 급격히 떨어집니다. SQLite 기반 Mock DB를 제공하거나 Docker 설치를 챕터 진입 조건으로 더 강하게 강조해야 합니다."

### 개선 제안

- SQLite 기반 Mock DB 옵션 제공 (Docker 없이 기본 동작 확인 가능)
- MCP 4.4절 설명에 실행 가능한 예시 코드 추가 (DB 없이 도구 패턴만 체험)
- schema.sql 적재 완료 확인 명령어 추가 (`docker exec -it ... psql -c "\dt"`)
