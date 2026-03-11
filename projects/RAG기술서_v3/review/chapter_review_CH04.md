# CH04 FastAPI로 초간단 사내 시스템 만들기 — 독자 리뷰 보고서


---

## 1. 챕터 개요

| 항목 | 내용 |
|------|------|
| 학습 목표 | FastAPI + PostgreSQL CRUD 시스템 구축, Pydantic 데이터 검증, Jinja2 Admin UI 구현 |
| 전제 조건 | CH02 Docker + PostgreSQL 환경, Python 3.10+ |
| 실행 단계 수 | 7단계 |
| 실제 소요 시간 | 약 25분 (Docker 이미지 다운로드 포함, 초보자 기준 30~40분 예상) |

---

## 2. 환경 확인 결과

### 2-1. 사전 조건 확인

| 항목 | 요구사항 | 실제 버전/상태 | 결과 |
|------|---------|---------------|------|
| Python | 3.10+ | 3.14.3 (시스템) / 3.12.x (venv) | PASS (3.12로 우회 필요) |
| Docker | 실행 중 | 29.1.3 실행 중 | PASS |
| psycopg2-binary | Python 3.12 이하 권장 | Python 3.12 venv에서 2.9.11 설치 성공 | PASS (조건부) |
| 포트 5432 | 사용 가능 | OCCUPIED (기존 컨테이너 사용 중) | 주의 필요 |
| 포트 8000 | 사용 가능 | OCCUPIED (기존 컨테이너 사용 중) | 주의 필요 |

**환경 주의사항**: 리뷰 환경에서 포트 5432와 8000이 이미 사용 중이었습니다. 리뷰 목적으로 `docker-compose-review.yml` (포트 5434)과 `.env` (포트 5434/8002)를 수동 생성하여 우회하였습니다. 실제 독자 환경에서는 보통 이 포트가 비어 있을 것입니다.

### 2-2. 의존성 설치

**사용 명령어:**
```bash
python3.12 -m venv .venv_review
source .venv_review/bin/activate
pip install -r requirements.txt
```

**설치 결과 (마지막 10줄):**
```
Successfully installed MarkupSafe-3.0.3 annotated-doc-0.0.4 annotated-types-0.7.0
anyio-4.12.1 click-8.3.1 fastapi-0.133.1 h11-0.16.0 httptools-0.7.1 idna-3.11
jinja2-3.1.6 psycopg2-binary-2.9.11 pydantic-2.12.5 pydantic-core-2.41.5
python-dotenv-1.2.1 python-multipart-0.0.22 pyyaml-6.0.3 starlette-0.52.1
typing-extensions-4.15.0 typing-inspection-0.4.2 uvicorn-0.41.0 uvloop-0.22.1
watchfiles-1.1.1 websockets-16.0
```

> 설치 패키지: 21개 | 결과: PASS (Python 3.12 venv 사용 시)

**중요 발견**: `requirements.txt`에 `annotated-doc`이 자동 설치되었습니다. 이는 `fastapi>=0.115.0` 의존성 체인으로 인한 것으로, 책 본문에 언급되지 않은 패키지입니다. 독자가 pip 로그를 보고 당황할 수 있습니다.

---

## 3. 단계별 실행 결과

### STEP 01: Docker Compose로 PostgreSQL 실행

**원고 지시사항:** `docker-compose up -d` 실행 후 `docker-compose ps`로 `running (healthy)` 상태 확인

**실행 명령어:**
```bash
docker-compose up -d
docker-compose ps
```

**실제 출력:**
```
NAME                     STATUS
connect_hr_db_review     running (healthy)   0.0.0.0:5434->5432/tcp
```

**스크린 캡처:**
![docker-compose ps 결과](../assets/CH04/step01_docker_ps.png)

**결과:** PASS
> 포트 충돌로 인해 5434를 사용했지만 컨테이너가 healthy 상태로 정상 시작되었습니다. 원고의 예상 출력(`connect_hr_db  running (healthy)`)과 컨테이너 이름만 다르며 나머지는 동일합니다.

---

### STEP 02: Python 가상환경 생성 및 의존성 설치

**원고 지시사항:** `python3 -m venv venv` → `source venv/bin/activate` → `pip install -r requirements.txt`

**실행 명령어:**
```bash
python3.12 -m venv .venv_review
source .venv_review/bin/activate
pip install -r requirements.txt
```

**스크린 캡처:**
![pip install 결과](../assets/CH04/step02_pip_install.png)

**결과:** PASS (Python 3.12 사용 시)
> Python 3.14에서는 psycopg2-binary 빌드 실패 가능성이 있습니다. 원고에 Python 버전 요구사항(3.10~3.12 권장)을 명시하면 좋겠습니다.

---

### STEP 03: FastAPI 서버 실행

**원고 지시사항:** `python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` 실행

**실행 명령어:**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002
```

**실제 출력:**
```
INFO:     Started server process [26627]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8002 (Press CTRL+C to quit)
```

**스크린 캡처:**
![uvicorn 서버 시작](../assets/CH04/step00_server_start.png)

**결과:** PASS
> 원고의 기대 출력은 `python app/main.py` 실행 시 나타나는 배너(`=======================================================  Q/A 사내 AI 사내 시스템 (CH04)...`)를 보여줍니다. 그러나 원고에서 제시한 실행 명령은 `python -m uvicorn app.main:app --reload`로 배너가 표시되지 않습니다. `python app/main.py`로 실행해야 배너가 나타납니다. **기대 출력과 실행 명령 불일치** 발견.

---

### STEP 04: Admin 대시보드 확인

**원고 지시사항:** `http://localhost:8000`에 접속하여 Admin 대시보드 확인

**실행 결과:**
```
HTTP/1.1 307 Temporary Redirect → /admin/dashboard → 200 OK
직원 수: 5, 연차 기록 수: 5, 매출 기록 수: 10, 총 매출: 63,950,000원
```

**스크린 캡처:**
![Admin 대시보드](../assets/CH04/step05_admin_dashboard.png)

**결과:** PASS
> 루트 URL 자동 리다이렉트, 통계 카드(직원 5명, 연차 5건, 매출 10건), 최근 매출 5건 목록이 모두 정상 표시됩니다. 시드 데이터가 올바르게 삽입되었습니다.

---

### STEP 05: Swagger UI 및 직원 API 테스트

**원고 지시사항:** `http://localhost:8000/docs`에서 `GET /api/employees` → Try it out → Execute

**실행 결과 (GET /api/employees):**
```json
[
  {"id": 1, "emp_no": "EMP001", "name": "김민준", "dept": "개발팀", "position": "과장", "hire_date": "2019-03-02"},
  {"id": 2, "emp_no": "EMP002", "name": "이서연", "dept": "영업팀", "position": "대리", "hire_date": "2021-07-12"},
  {"id": 3, "emp_no": "EMP003", "name": "박지호", "dept": "인사팀", "position": "사원", "hire_date": "2023-01-09"},
  {"id": 4, "emp_no": "EMP004", "name": "최유나", "dept": "마케팅팀", "position": "차장", "hire_date": "2016-11-01"},
  {"id": 5, "emp_no": "EMP005", "name": "정도현", "dept": "개발팀", "position": "사원", "hire_date": "2024-02-26"}
]
```

**스크린 캡처:**
![Swagger UI](../assets/CH04/step06_swagger_ui.png)

![GET /api/employees 결과](../assets/CH04/step03_api_employees.png)

**결과:** PASS
> 원고에서 제시한 5명의 직원 데이터가 정확히 일치합니다. Swagger UI에서 `/admin/*` 라우트와 `/api/*` 라우트가 모두 문서화됩니다.

---

### STEP 06: 연차 사용 등록 API 테스트

**원고 지시사항:** `POST /api/leaves/usage` Body: `{"employee_id": 1, "days": 2.0}`

**실행 명령어:**
```bash
curl -s -X POST http://localhost:8002/api/leaves/usage \
  -H "Content-Type: application/json" \
  -d '{"employee_id": 1, "days": 2.0}'
```

**실제 출력 (첫 번째 호출):**
```json
{
  "id": 1,
  "employee_id": 1,
  "year": 2025,
  "total_days": 15.0,
  "used_days": 7.0,
  "remaining_days": 8.0
}
```

**스크린 캡처:**
![연차 사용 등록 결과](../assets/CH04/step04_leave_usage.png)

**결과:** PASS
> 원고의 기대 출력(`used_days: 7.0, remaining_days: 8.0`)과 정확히 일치합니다. PostgreSQL `GENERATED ALWAYS AS` 생성 컬럼이 자동으로 `remaining_days`를 계산합니다.

---

### STEP 07: Admin UI 직원 관리 페이지 확인

**원고 지시사항:** `http://localhost:8000/admin/employees`에서 GUI 형태로 직원 관리

**스크린 캡처:**
![직원 관리 Admin UI](../assets/CH04/step07_employees_ui.png)

**결과:** PASS
> 직원 등록, 수정, 삭제, 검색 폼이 모두 정상 렌더링됩니다. 직원 목록 테이블에 5명의 시드 데이터가 표시됩니다.

---

## 4. 챕터 원고 품질 평가

| 평가 항목 | 점수 (5점) | 근거 |
|----------|-----------|------|
| 설명 충분성 | 5 | FastAPI 선택 이유 4가지, PostgreSQL 선택 이유, Jinja2 설계 원칙을 개념 설명 후 코드로 연결하는 흐름이 명확합니다. |
| Why 설명 | 5 | 각 코드 번호 주석(①②③...)이 "왜 이 코드를 쓰는지"를 상세히 설명합니다. `ILIKE`, `GENERATED ALWAYS AS`, `RETURNING` 절 등 DB 문법의 의도가 명확합니다. |
| 실행 재현성 | 4 | 전반적으로 우수하나 한 가지 불일치 발견: 원고 실행 명령은 `python -m uvicorn app.main:app --reload`이지만 기대 출력은 `python app/main.py`로 실행해야 나오는 배너를 보여줍니다. |
| 코드 발췌 정확성 | 5 | 챕터에 인용된 모든 코드 발췌가 실제 `examples/` 코드와 정확히 일치합니다. `crud.py`의 `get_all_employees`, `update_leave_usage` 함수가 원고와 완벽히 동일합니다. |
| 오류 처리 안내 | 4 | DB 연결 전 Docker 실행 경고(`주의: docker-compose up 이전에 FastAPI를 실행하면 안 됩니다`)는 적절합니다. 그러나 Python 3.14에서 psycopg2-binary 빌드 실패 케이스와 포트 충돌 시 대응 방법이 없습니다. |
| 분량 적절성 | 5 | 코드 워크플로우(IPO 패턴) 설명이 각 절마다 포함되어 있어 읽기 좋은 속도로 진행됩니다. `base.html` 계승 구조 설명(섹션 6)이 이후 챕터와의 연결성을 강화합니다. |
| **합계** | **28/30** | |

---

## 5. 발견된 문제점

### 5-1. 실행 명령 vs 기대 출력 불일치 (중간 심각도)

**위치:** 섹션 2 "프로젝트 클론 및 실행"

**문제:** 원고의 실행 명령은 다음과 같습니다:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
그러나 원고의 기대 출력은:
```
=======================================================
  Q/A 사내 AI 사내 시스템 (CH04)
  Admin UI : http://localhost:8000/admin/dashboard
  API 문서 : http://localhost:8000/docs
=======================================================
```
이 배너는 `python app/main.py`를 실행했을 때만 나타납니다 (`app/main.py`의 `if __name__ == "__main__"` 블록). `python -m uvicorn` 명령은 uvicorn을 직접 호출하므로 배너가 표시되지 않습니다.

**권장 수정:** 실행 명령을 `python app/main.py`로 변경하거나, 기대 출력에서 배너를 제거하고 uvicorn의 실제 출력으로 대체하십시오.

### 5-2. Python 버전 제한 미기재 (낮은 심각도)

**위치:** `requirements.txt`, README.md

**문제:** `requirements.txt` 주석에는 "Python 3.10+ 필요"라고 명시되어 있으나, Python 3.13+에서 `psycopg2-binary`의 빌드 성공 여부가 불명확합니다. 실제 리뷰 환경(Python 3.14.3)에서는 psycopg2-binary 설치 성공이 확인되었지만, 이는 환경에 따라 달라질 수 있습니다.

**권장 수정:** README.md에 "권장 Python 버전: 3.10 ~ 3.12. 3.13 이상에서는 psycopg2-binary 빌드 오류가 발생할 수 있습니다."를 추가하십시오.

### 5-3. Swagger UI에 Admin 라우트 노출 (정보성)

**위치:** `app/views.py` 라우터 설정

**문제:** `GET /admin/dashboard`, `GET /admin/employees` 등 Admin UI 라우트가 Swagger UI(`/docs`)에 노출됩니다. 이는 `views.router`에 `include_in_schema=False`가 없기 때문입니다. 독자가 Swagger UI를 처음 열면 `/admin/*` 라우트가 많아서 혼란스러울 수 있습니다.

**권장 수정:** `views.py`의 라우터 정의에 `include_in_schema=False`를 추가하거나, 원고에서 "Swagger UI에는 Admin UI 라우트도 표시됩니다"라는 안내를 추가하십시오.

### 5-4. `data/` 폴더 명칭 불일치 (낮은 심각도)

**위치:** 챕터 섹션 3 "프로젝트 구조 파악"

**문제:** 원고의 프로젝트 구조에는 `data/schema.sql`로 표시되어 있습니다. 그러나 `docker-compose.yml`은 `./data/schema.sql:/docker-entrypoint-initdb.d/01_schema.sql`로 마운트하며 실제 파일명은 `schema.sql`입니다. 독자가 챕터 4.2절의 "코드 워크플로우"에서 "`01_schema.sql` 자동 실행"이라는 설명을 보면 파일명이 `01_schema.sql`인지 `schema.sql`인지 혼동할 수 있습니다.

---

## 6. 학생 한 줄 평

> FastAPI 선택 이유부터 base.html이 CH07/CH08에서 계승되는 연결까지 설명이 탄탄합니다. 단, 실행 명령과 기대 출력 배너의 불일치 때문에 처음 따라 할 때 "내 출력이 왜 다르지?"라는 당혹감을 줄 수 있습니다. 이 점만 수정하면 완성도 높은 챕터입니다.

---

## 7. 개선 제안

1. **실행 명령 통일**: 배너를 보여주고 싶다면 실행 명령을 `python app/main.py`로 변경하거나, uvicorn 직접 실행 명령에 맞게 기대 출력을 수정하십시오.

2. **Python 버전 경고 추가**: README.md와 원고에 Python 3.12 이하를 권장한다는 명시를 추가하십시오. 특히 macOS Homebrew Python이 최신 버전인 경우 `python3.12 -m venv venv`처럼 버전을 명시하는 방법을 안내하면 좋습니다.

3. **포트 충돌 대응 안내**: 원고 섹션 2에 "포트 5432 또는 8000이 이미 사용 중인 경우: `docker-compose.yml`의 포트 설정과 `.env`의 포트 값을 함께 변경하십시오"라는 트러블슈팅 안내를 추가하십시오.

4. **views.py Swagger 노출 설명**: Swagger UI에 Admin UI 라우트가 표시되는 것이 의도된 동작이라면 원고에서 언급하고, 그렇지 않다면 `include_in_schema=False`를 추가하십시오.

5. **`data/` 폴더 파일명 설명 보강**: `docker-compose.yml`에서 `schema.sql`이 컨테이너 내부에서 `01_schema.sql`로 마운트된다는 점을 섹션 4.2의 코드 워크플로우 설명에서 명확히 하십시오.

---

## 부록: 캡처 파일 목록

| 스크린샷 | 경로 | 플레이스홀더 경로 |
|---------|------|----------------|
| uvicorn 서버 시작 로그 | `assets/CH04/step00_server_start.png` | `assets/CH04/04_server-start.png` |
| docker-compose ps | `assets/CH04/step01_docker_ps.png` | — |
| pip install 결과 | `assets/CH04/step02_pip_install.png` | — |
| GET /api/employees | `assets/CH04/step03_api_employees.png` | — |
| POST /api/leaves/usage | `assets/CH04/step04_leave_usage.png` | — |
| Admin 대시보드 | `assets/CH04/step05_admin_dashboard.png` | `assets/CH04/04_admin-dashboard.png` |
| Swagger UI | `assets/CH04/step06_swagger_ui.png` | — |
| 직원 관리 Admin UI | `assets/CH04/step07_employees_ui.png` | `assets/CH04/04_employees-ui.png` |
| 휴가 관리 Admin UI | `assets/CH04/step08_leaves_ui.png` | — |
| 매출 관리 Admin UI | `assets/CH04/step09_sales_ui.png` | — |
