# CH02 예제 코드 명세 — 개발 환경 구축

## 1. 프로젝트 유형
인프라·설명 챕터. 독립 레포 없음. Docker Compose + Python 환경 설정 파일 모음.

## 2. 디렉토리 구조

```
CH02_개발환경구축/
├── README.md
├── docker-compose.yml        ← PostgreSQL 16 + pgAdmin 컨테이너
├── requirements.txt          ← 전체 프로젝트 Python 의존성
├── .env.example              ← 환경 변수 템플릿
├── .gitignore
├── init/
│   └── 01_schema_and_data.sql  ← DB 초기 스키마 + 샘플 데이터
├── src/
│   ├── __init__.py
│   ├── config.py             ← 환경 변수 로딩 + LLM Provider 스위칭
│   └── verify_env.py         ← 개발 환경 전체 동작 확인 스크립트
├── tests/
│   └── test_config.py
└── outputs/
    └── .gitkeep
```

## 3. 파일별 함수 명세

### `docker-compose.yml` 서비스 구성

| 서비스 | 이미지 | 포트 | 역할 |
|--------|--------|------|------|
| postgres | postgres:16-alpine | 5432 | 메인 DB |
| pgadmin | dpage/pgadmin4 | 5050 | DB 관리 UI (선택) |

- `init/01_schema_and_data.sql`은 postgres 컨테이너 최초 실행 시 자동 실행
- 모든 설정값은 `.env` 파일에서 주입

### `init/01_schema_and_data.sql`

```sql
-- 테이블 3개 (CH04~CH09에서 공통 사용)
CREATE TABLE employees (id, name, department, annual_leave_days, used_leave_days)
CREATE TABLE leaves    (id, employee_id, start_date, end_date, reason, status)
CREATE TABLE sales     (id, employee_id, department, amount, sale_date, quarter)

-- 샘플 데이터: 직원 5명, 연차 기록 10건, 매출 기록 20건
```

### `src/config.py`

```python
def _require_env(key: str) -> str:
    """
    필수 환경 변수 로딩. 없으면 ValueError 발생.
    Input : 환경 변수 키
    Output : 값 문자열
    """

def _get_env(key: str, default: str = "") -> str:
    """선택 환경 변수 로딩. 없으면 default 반환."""

def get_postgres_url() -> str:
    """
    PostgreSQL 연결 URL 생성.
    Output : "postgresql://user:password@host:port/dbname"
    """

def get_llm_config() -> dict:
    """
    LLM Provider 설정 반환.
    Input : LLM_PROVIDER 환경 변수 ("ollama" | "openai")
    Output : {
      "provider": str,
      "model": str,
      "base_url": str | None,  # ollama만 해당
      "api_key": str | None    # openai만 해당
    }
    """
```

### `src/verify_env.py`

```python
def check_python_version() -> bool:
    """Python 3.11 이상 확인."""

def check_env_file() -> bool:
    """.env 파일 존재 여부 확인."""

def check_env_vars() -> bool:
    """필수 환경 변수 로딩 가능 여부 확인."""

def check_packages() -> bool:
    """requirements.txt 주요 패키지 import 테스트."""

def check_ollama() -> bool:
    """Ollama 서버 응답 확인 (http://localhost:11434)."""

def check_postgres() -> bool:
    """PostgreSQL 접속 확인 (psycopg2)."""

def main() -> None:
    """
    6단계 환경 점검 순서대로 실행.
    각 단계: ✓ 또는 ✗ + 오류 메시지 출력
    전체 통과 시: "환경 설정 완료! 3장으로 넘어가세요."
    """
```

## 4. 실행 시나리오

```bash
# 1단계: 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 비밀번호 등 수정

# 2단계: Python 가상환경 + 패키지 설치
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3단계: PostgreSQL 구동
docker-compose up -d

# 4단계: 환경 전체 확인
python src/verify_env.py

# 기대 출력:
# ✓ Python 3.11.x
# ✓ .env 파일 존재
# ✓ 환경 변수 로딩
# ✓ 패키지 설치 (langchain, chromadb, ...)
# ✓ Ollama 서버 응답
# ✓ PostgreSQL 접속
# 환경 설정 완료! 3장으로 넘어가세요.
```

## 5. 의존성

```
# requirements.txt 핵심 (버전 고정)
langchain>=0.3.0
langchain-community>=0.3.0
langchain-ollama>=0.2.0
chromadb>=0.5.0
fastapi>=0.111.0
uvicorn[standard]>=0.30.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.9
pymupdf>=1.24.0
pdfplumber>=0.11.0
python-dotenv>=1.0.0
requests>=2.31.0
sentence-transformers>=3.0.0
rank-bm25>=0.2.2
easyocr>=1.7.0
```

## 6. .env.example

```
# LLM Provider 설정 (ollama 또는 openai)
LLM_PROVIDER=ollama

# LLM 모델명 설정
# Ollama 예시: deepseek-r1:1.5b, deepseek-r1:8b, llama3, mistral
# OpenAI 예시: gpt-4o, gpt-4o-mini
LLM_MODEL_NAME=deepseek-r1:1.5b

# Ollama 설정 (PROVIDER가 ollama인 경우 필요)
OLLAMA_BASE_URL=http://localhost:11434

# OpenAI 설정 (PROVIDER가 openai인 경우 필요)
# OPENAI_API_KEY=sk-proj-...

# 임베딩 모델
EMBED_MODEL=nomic-embed-text

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=rag_db
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=rag_password

# pgAdmin (선택)
PGADMIN_EMAIL=admin@example.com
PGADMIN_PASSWORD=admin
```

## 7. 이 챕터 코드의 특징
- CH03~CH10 전체에서 공통으로 사용하는 **베이스 환경**
- `requirements.txt`는 책 전체 의존성을 한 번에 설치하도록 통합 관리
- `src/config.py`의 `get_llm_config()`는 CH03~CH09에서 재사용
