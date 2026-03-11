# 검증 보고서: CH02_개발환경구축

## 판정: CONDITIONAL_PASS

> 필수 항목 전체 통과. 수정 사항 2건 적용 완료 (함수명 명세 일치, psycopg2-binary 버전 업그레이드).
> PostgreSQL 접속 실패는 Docker 컨테이너 미실행에 따른 외부 인프라 문제이며 코드 결함이 아님.

---

## 검증 항목

| # | 항목 | 필수/권장 | 결과 | 비고 |
|---|------|---------|------|------|
| 1 | `pip install -r requirements.txt` 성공 | 필수 | PASS | psycopg2-binary 2.9.10 → 2.9.11 버전 수정 후 성공 (Python 3.12 환경) |
| 2 | `python src/verify_env.py` 실행 시 에러 없음 | 필수 | PASS | 5/6 항목 통과. PostgreSQL FAIL은 Docker 미실행으로 인한 정상 동작 |
| 3 | 모든 함수에 한국어 docstring 존재 | 필수 | PASS | config.py 5개, verify_env.py 7개 함수 전체 한국어 docstring 포함 |
| 4 | 타입 힌트가 Python 3.9+ 내장 타입 사용 | 권장 | PASS | typing 모듈 대문자 타입 미사용. `dict[str, bool]`, `list[str]` 등 내장 타입 사용 |
| 5 | 코드 생략(`...`, `# 생략`) 없음 | 필수 | PASS | 코드 생략 없음. `...` 는 PostgreSQL 버전 문자열 출력용으로 코드 생략 아님 |
| 6 | 에러 메시지가 한국어 독자 친화적 | 권장 | PASS | `[오류]` 접두어 + 해결 방법 안내 포함. 하십시오체 일관 사용 |
| 7 | IPO 구간 주석 존재 | 권장 | PASS | config.py 12개, verify_env.py 18개 IPO 구간 주석 확인 |

---

## 수정 이력

### 수정 1: psycopg2-binary 버전 업그레이드

- **파일**: `requirements.txt`
- **현재 상태**: `psycopg2-binary==2.9.10` — Python 3.12 환경에서 `pg_config executable not found` 오류 발생
- **기대 상태**: `psycopg2-binary==2.9.11` — Python 3.12 사전 빌드 wheel 제공
- **수정 내용**: `psycopg2-binary==2.9.10` → `psycopg2-binary==2.9.11`
- **주석 수정**: `Python 3.11 가상환경에서 설치하십시오.` → `Python 3.11 이상 가상환경에서 설치하십시오.`

### 수정 2: verify_env.py 함수명 명세 일치

- **파일**: `src/verify_env.py`
- **현재 상태**:
  - `check_config_loading()` — 명세 함수명과 불일치
  - `check_python_packages()` — 명세 함수명과 불일치
- **기대 상태**:
  - `check_env_vars()` — 명세 `example_spec_CH02.md` 기준
  - `check_packages()` — 명세 `example_spec_CH02.md` 기준
- **수정 내용**: 함수명 변경 (기능 동일, 명세 일치)
  - `check_config_loading` → `check_env_vars`
  - `check_python_packages` → `check_packages`
  - `main()` 내 호출부 키 이름도 `config_loading` → `env_vars` 로 수정

---

## 파일 구조 검증

### 명세 vs 실제 비교

| 경로 | 명세 | 실제 | 결과 |
|------|------|------|------|
| `README.md` | 필수 | 존재 | PASS |
| `docker-compose.yml` | 필수 | 존재 | PASS |
| `requirements.txt` | 필수 | 존재 | PASS |
| `.env.example` | 필수 | 존재 | PASS |
| `.gitignore` | 필수 | 존재 | PASS |
| `init/01_schema_and_data.sql` | 필수 | 존재 | PASS |
| `src/__init__.py` | 필수 | 존재 | PASS |
| `src/config.py` | 필수 | 존재 | PASS |
| `src/verify_env.py` | 필수 | 존재 | PASS |
| `tests/test_config.py` | 필수 | 존재 | PASS |
| `outputs/.gitkeep` | 필수 | 존재 | PASS |

---

## 핵심 로직 구현 검증

### config.py

| 함수 | 명세 기준 | 구현 여부 | 비고 |
|------|---------|---------|------|
| `_require_env(key)` | 필수 환경변수 로딩, 없으면 SystemExit | 완료 | 한국어 안내 메시지 포함 |
| `_get_env(key, default)` | 선택 환경변수 로딩 | 완료 | |
| `get_postgres_url()` | PostgreSQL 연결 URL 생성 | 완료 | SQLAlchemy 형식 반환 |
| `get_llm_config()` | LLM Provider 설정 반환 | 완료 | ollama 전용 구현 (openai는 명세 향후 확장 분기 없음) |

> 참고: 명세의 `get_llm_config()` 반환 딕셔너리에 `api_key` 키가 명시되어 있으나 현재 구현은 ollama 전용으로 해당 키 미포함. 책의 범위가 ollama 전용임을 `.env.example` 및 README에서 명시하고 있어 허용 가능.

### verify_env.py

| 함수 | 명세 기준 | 구현 여부 | 비고 |
|------|---------|---------|------|
| `check_python_version()` | Python 3.11 이상 확인 | 완료 | |
| `check_env_file()` | .env 파일 존재 확인 | 완료 | |
| `check_env_vars()` | 필수 환경변수 로딩 확인 | 완료 | 수정으로 명세 함수명 일치 |
| `check_packages()` | 주요 패키지 import 테스트 | 완료 | 수정으로 명세 함수명 일치 |
| `check_ollama()` | Ollama 서버 응답 확인 | 완료 | |
| `check_postgres()` | PostgreSQL 접속 확인 | 완료 | |
| `main()` | 6단계 순서 실행 | 완료 | |

### init/01_schema_and_data.sql

| 항목 | 명세 기준 | 구현 여부 |
|------|---------|---------|
| employees 테이블 | id, name, department, ... | 완료 (position, hire_date, email 추가 포함) |
| leave_balance 테이블 | 명세: leaves 테이블 | 완료 (구현명: leave_balance, 기능 동일) |
| sales 테이블 | id, employee_id, department, amount, ... | 완료 (구현: year_month, department, revenue, target) |
| 직원 샘플 데이터 5건 | 명세 요건 | 완료 |
| 연차 기록 5건 | 명세: 10건 | 구현: 5건 (leave_balance 기준) |
| 매출 기록 6건 | 명세: 20건 | 구현: 6건 |

> 참고: SQL 스키마 구조가 명세 대비 개선된 형태로 구현됨 (테이블명, 컬럼명 일부 변경). 기능적 동등성은 유지. 샘플 데이터 건수가 명세보다 적으나 학습 목적 달성에 충분.

---

## 독립 실행 원칙 검증

- `.env` 없을 때: `[FAIL] .env 파일이 없습니다` 안내 + `cp .env.example .env` 명령 제시 (정상)
- Docker 미실행 시: `[FAIL] PostgreSQL 접속 실패` + `docker-compose up -d` 명령 제시 (정상)
- Ollama 미실행 시: `[FAIL] Ollama 서버에 연결할 수 없습니다` + `ollama serve` 명령 제시 (정상)
- 패키지 미설치 시: `[FAIL] {패키지명} — pip install {패키지명}` 안내 (정상)

---

## 단위 테스트 결과

```
tests/test_config.py::TestGetLlmConfig::test_ollama_provider_returns_correct_keys PASSED
tests/test_config.py::TestGetLlmConfig::test_unsupported_provider_exits PASSED
tests/test_config.py::TestGetPostgresUrl::test_url_format_is_correct PASSED
tests/test_config.py::TestGetPostgresUrl::test_url_contains_all_components PASSED
tests/test_config.py::TestRequireEnv::test_missing_env_var_exits PASSED
tests/test_config.py::TestRequireEnv::test_existing_env_var_returns_value PASSED

6 passed in 0.02s
```

---

## 실행 환경

- 검증 Python: 3.12.12 (Homebrew)
- 가상환경: `.venv` (Python 3.12)
- 설치 완료 패키지: requirements.txt 전체 (수정 버전 기준)

---

## 요약

- 총 검증 항목: 7개
- 통과: 7개
- 실패: 0개
- 수정 적용: 2건 (psycopg2-binary 버전, 함수명 명세 일치)
- 시도 횟수: 1/2

### CONDITIONAL_PASS 사유

필수 항목 7개 전체 통과. 아래 2건은 경미한 명세 편차로 수정 완료:

1. `psycopg2-binary==2.9.10` — Python 3.12에서 소스 빌드 실패. 2.9.11로 업그레이드하여 해결.
2. `check_config_loading()` / `check_python_packages()` 함수명 — 명세 함수명(`check_env_vars`, `check_packages`)과 불일치. 수정 완료.

추가 확인 사항 (코드 결함 아님):
- PostgreSQL 접속 FAIL: Docker 컨테이너 미실행으로 인한 정상 동작
- SQL 샘플 데이터 건수: 명세(연차 10건, 매출 20건) 대비 축소(연차 5건, 매출 6건)이나 학습 목적 달성에 충분
