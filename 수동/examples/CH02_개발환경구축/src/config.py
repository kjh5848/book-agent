"""config.py — 환경 변수 로딩 및 LLM Provider 스위칭 설계

이 모듈은 .env 파일에서 환경 변수를 읽어와 설정 객체로 제공합니다.
LLM_PROVIDER 값에 따라 다른 LLM 백엔드로 투명하게 전환할 수 있습니다.

2장 섹션 4: 환경 변수(.env) 구성 및 LLM Provider 스위칭 설계

설계 원칙:
    - 설정을 코드에 하드코딩하지 않습니다. 모든 설정은 .env에서 읽습니다.
    - LLM_PROVIDER 환경 변수 하나만 바꾸면 LLM 백엔드를 전환할 수 있습니다.
    - 필수 환경 변수가 누락된 경우 즉시 오류 메시지를 출력하고 종료합니다.
"""

import sys
from pathlib import Path

from dotenv import load_dotenv
import os


# --- .env 파일 자동 로딩 ---
# 프로젝트 루트의 .env 파일을 찾아 환경 변수로 적재합니다.
# .env 파일이 없으면 시스템 환경 변수를 사용합니다.
_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=_env_path, override=False)


def _require_env(key: str) -> str:
    """필수 환경 변수를 읽어 반환합니다. 없으면 안내 메시지와 함께 종료합니다.

    Args:
        key: 환경 변수 이름

    Returns:
        환경 변수 값 문자열

    Raises:
        SystemExit: 환경 변수가 설정되어 있지 않을 경우
    """

    # --- Input ---
    value = os.getenv(key)

    # --- Process ---
    if not value:
        print(f"[오류] 필수 환경 변수 '{key}'가 설정되지 않았습니다.")
        print("       프로젝트 루트의 .env.example 파일을 복사하여 .env를 만들고,")
        print("       필요한 값을 입력한 뒤 다시 실행하십시오.")
        print("       cp .env.example .env")
        sys.exit(1)

    # --- Output ---
    return value


def _get_env(key: str, default: str = "") -> str:
    """환경 변수를 읽어 반환합니다. 없으면 기본값을 반환합니다.

    Args:
        key: 환경 변수 이름
        default: 환경 변수가 없을 때 사용할 기본값

    Returns:
        환경 변수 값 또는 기본값
    """

    # --- Input / Process / Output ---
    return os.getenv(key, default)


# =============================================================================
# LLM Provider 설정
# =============================================================================

#: 사용할 LLM 제공자 (현재 지원: ollama)
LLM_PROVIDER: str = _get_env("LLM_PROVIDER", "ollama")

#: Ollama 서버 기본 URL
OLLAMA_BASE_URL: str = _get_env("OLLAMA_BASE_URL", "http://localhost:11434")

#: 사용할 언어 모델 이름
OLLAMA_MODEL: str = _get_env("OLLAMA_MODEL", "deepseek-r1")

#: 이미지 분석용 Vision 모델 이름 (10장)
OLLAMA_VISION_MODEL: str = _get_env("OLLAMA_VISION_MODEL", "llava")


# =============================================================================
# PostgreSQL 설정
# =============================================================================

#: PostgreSQL 호스트 주소
POSTGRES_HOST: str = _get_env("POSTGRES_HOST", "localhost")

#: PostgreSQL 포트 번호
POSTGRES_PORT: int = int(_get_env("POSTGRES_PORT", "5432"))

#: PostgreSQL 데이터베이스 이름
POSTGRES_DB: str = _get_env("POSTGRES_DB", "company_db")

#: PostgreSQL 사용자명
POSTGRES_USER: str = _get_env("POSTGRES_USER", "admin")

#: PostgreSQL 비밀번호
POSTGRES_PASSWORD: str = _get_env("POSTGRES_PASSWORD", "changeme")


def get_postgres_url() -> str:
    """PostgreSQL 접속 URL을 생성하여 반환합니다.

    Returns:
        SQLAlchemy 형식의 PostgreSQL 연결 문자열
        예: postgresql://admin:changeme@localhost:5432/company_db
    """

    # --- Input ---
    # 모듈 상수에서 각 접속 정보를 읽어옵니다.

    # --- Process ---
    url = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )

    # --- Output ---
    return url


# =============================================================================
# ChromaDB 설정
# =============================================================================

#: 벡터 데이터 영속 저장 경로
CHROMA_PERSIST_DIR: str = _get_env("CHROMA_PERSIST_DIR", "./chroma_data")

#: ChromaDB 컬렉션 이름
CHROMA_COLLECTION: str = _get_env("CHROMA_COLLECTION", "company_docs")


# =============================================================================
# FastAPI CRUD 서버 설정
# =============================================================================

#: CRUD API 서버 기본 URL
CRUD_API_BASE_URL: str = _get_env("CRUD_API_BASE_URL", "http://localhost:8000")


# =============================================================================
# LLM Provider 스위칭 로직
# =============================================================================

def get_llm_config() -> dict:
    """현재 LLM_PROVIDER 값에 따른 LLM 설정 딕셔너리를 반환합니다.

    LLM_PROVIDER 환경 변수를 바꾸면 이 함수가 적절한 설정을 자동으로 반환합니다.
    향후 openai, anthropic 등 다른 제공자를 추가할 때도 이 함수만 수정하면 됩니다.

    Returns:
        LLM 설정 딕셔너리. 키: provider, model, base_url (해당하는 경우)

    Raises:
        SystemExit: 지원하지 않는 LLM_PROVIDER 값인 경우
    """

    # --- Input ---
    provider = LLM_PROVIDER.lower()

    # --- Process ---
    if provider == "ollama":
        config = {
            "provider": "ollama",
            "model": OLLAMA_MODEL,
            "base_url": OLLAMA_BASE_URL,
        }
    else:
        print(f"[오류] 지원하지 않는 LLM_PROVIDER 값입니다: '{LLM_PROVIDER}'")
        print("       현재 지원하는 값: ollama")
        print("       .env 파일의 LLM_PROVIDER를 확인하십시오.")
        sys.exit(1)

    # --- Output ---
    return config


def print_config_summary() -> None:
    """현재 로딩된 설정값을 요약하여 출력합니다.

    민감한 정보(비밀번호)는 마스킹하여 출력합니다.
    환경 구축 후 설정이 올바른지 빠르게 확인할 때 사용합니다.
    """

    # --- Input ---
    # 모듈 레벨 상수들을 읽어옵니다.

    # --- Process ---
    password_masked = "*" * len(POSTGRES_PASSWORD) if POSTGRES_PASSWORD else "(미설정)"
    llm_config = get_llm_config()

    # --- Output ---
    print("=" * 50)
    print("현재 환경 설정 요약")
    print("=" * 50)
    print(f"[LLM]")
    print(f"  Provider : {llm_config['provider']}")
    print(f"  Model    : {llm_config['model']}")
    print(f"  Base URL : {llm_config['base_url']}")
    print()
    print(f"[PostgreSQL]")
    print(f"  Host     : {POSTGRES_HOST}:{POSTGRES_PORT}")
    print(f"  Database : {POSTGRES_DB}")
    print(f"  User     : {POSTGRES_USER}")
    print(f"  Password : {password_masked}")
    print()
    print(f"[ChromaDB]")
    print(f"  Persist  : {CHROMA_PERSIST_DIR}")
    print(f"  Collection: {CHROMA_COLLECTION}")
    print()
    print(f"[CRUD API]")
    print(f"  Base URL : {CRUD_API_BASE_URL}")
    print("=" * 50)
