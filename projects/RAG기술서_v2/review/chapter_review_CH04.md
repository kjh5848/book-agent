# CH04 베이스 시스템 확보 — 독자 리뷰 보고서

> 작성일: 2026-02-26 | 리뷰 방식: 학생 입장 직접 따라하기 | 챕터 컨셉: DB 스키마 분석 + MCP 개념 체험

---

## 1. 챕터 개요

| 항목 | 내용 |
|------|------|
| 학습 목표 | 사내 DB 스키마 분석 + FastAPI CRUD API + MCP 패턴 체험 |
| 전제 조건 | Docker (PostgreSQL), Python venv, CH03 완료 |
| 실행 단계 수 | 5단계 (docker-compose → schema → CRUD API → MCP demo) |
| 실제 소요 시간 | 약 20~30분 |

## 2. 환경 점검 결과

| 항목 | 상태 | 비고 |
|------|------|------|
| Python 버전 | PASS | 3.14.3 |
| Docker | FAIL | 미설치 - PostgreSQL 컨테이너 실행 불가 |
| psycopg2 | 설치 필요 | requirements.txt에 포함 |
| FastAPI | 설치 필요 | requirements.txt에 포함 |

## 3. 단계별 실행 결과

### STEP 1: docker-compose up -d

**원고 지시:** PostgreSQL 컨테이너 시작 및 샘플 데이터 적재

**결과:** SKIP (Docker 미설치)

**비고:** 챕터에 pgAdmin 사용 팁이 포함되어 있어 DB 시각화 방법까지 안내함. 좋은 추가 정보.

---

### STEP 2: schema_viewer.py 실행

**원고 지시:** `python src/main.py schema`

**예제 코드 검증:**
- `src/schema_viewer.py`의 `fetch_table_list` 함수: 챕터 발췌와 100% 일치
- 4개 테이블 구조(employees, leave_requests, leave_balance, sales_monthly) 설명 일치

**결과:** SKIP (DB 의존), PASS (코드 검증)

---

### STEP 3: FastAPI CRUD 서버

**원고 지시:** `uvicorn src.crud_api:app --reload --port 8000`

**예제 코드 검증:**
- `src/crud_api.py`의 `/leave-balance/{employee_id}` 엔드포인트 발췌: 일치
- 엔드포인트 목록 5개 (GET /health, /employees, /employees/{id}, /leave-balance/{id}, /sales/summary): 일치

**결과:** SKIP (DB 의존), PASS (코드 검증)

---

### STEP 4: MCP 데모

**원고 지시:** `python src/main.py mcp`

**예제 코드 검증:**
- `src/mcp_intro.py`의 `@tool get_leave_balance` 함수: 챕터 발췌와 일치
- 도구 3개 (get_employee_info, get_leave_balance, get_department_sales): 정의 확인

**결과:** SKIP (DB 의존), PASS (코드 검증)

---

## 4. 챕터 원고 품질 평가

| 항목 | 점수 (5점) | 근거 |
|------|----------|------|
| 설명 충분성 | 5 | 스키마가 왜 AI 에이전트 설계의 출발점인지, CRUD API가 왜 필요한지 충분히 설명 |
| Why 설명 | 5 | LLM이 직접 SQL 실행하면 안 되는 이유, MCP의 필요성 모두 설명 |
| 실행 재현성 | 3 | Docker 없으면 실습 전체가 막힘. Docker 없는 대안 없음 |
| 코드 발췌 정확성 | 5 | schema_viewer, crud_api, mcp_intro 발췌 모두 실제 코드와 일치 |
| 오류 대응 안내 | 4 | 트러블슈팅 표 제공. Docker 미설치 경우만 "Docker Desktop 설치" 안내 |
| 분량 적절성 | 4 | 전반적으로 적절하나 MCP 개념 설명이 빠르게 넘어가는 느낌 |
| **총점** | **26/30** | |

## 5. 발견된 문제점

1. **Docker 의존성 강함**: 이 챕터의 모든 실습이 Docker/PostgreSQL 의존. Docker 없는 환경에서 완전히 막힘.
2. **MCP 개념 다소 빠름**: 4.4절에서 MCP를 처음 소개하는데, 개념 설명이 다소 빠르게 CH08로 넘김. 더 많은 예시 코드가 있으면 좋겠음.
3. **Docker 데이터 준비 시간**: 샘플 데이터 15건 자동 적재 과정에서 schema.sql 실행 확인 방법이 명확하지 않음.

## 6. 학생 한 줄 평

> "이서연과 박민준이 함께 DB 스키마를 파악하는 스토리가 자연스럽게 코드 학습으로 이어지지만, Docker 없는 환경에서는 실습 자체가 불가능해 사전 준비 요구사항을 더 강조해야 합니다."

## 7. 개선 제안

- Docker 없는 환경을 위한 SQLite 기반 Mock DB 대안 제공
- MCP 4.4절에 더 많은 예시 코드와 실행 결과 추가
- schema.sql 적재 완료 확인 명령어 추가 (`docker exec -it ... psql -c "\dt"`)
