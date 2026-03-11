"""
환경 변수 로딩 및 설정 검증 모듈.

.env 파일을 읽어 필수 환경 변수를 검증하고,
기본값이 적용된 설정 객체를 반환합니다.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


# --- 상수 정의 ---
REQUIRED_VARS: list[str] = [
    "OLLAMA_BASE_URL",
    "OLLAMA_MODEL",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
]

DEFAULT_VALUES: dict[str, str] = {
    "OLLAMA_BASE_URL": "http://localhost:11434",
    "OLLAMA_MODEL": "deepseek-r1",
    "OLLAMA_VISION_MODEL": "llava",
    "POSTGRES_HOST": "localhost",
    "POSTGRES_PORT": "5432",
    "POSTGRES_DB": "connecthr",
    "POSTGRES_USER": "admin",
    "POSTGRES_PASSWORD": "password",
    "CHROMA_PERSIST_DIR": "./outputs/chroma_db",
    "FASTAPI_BASE_URL": "http://localhost:8000",
}


@dataclass
class AppConfig:
    """애플리케이션 전체 설정을 담는 데이터 클래스입니다.

    Attributes:
        ollama_base_url: Ollama 서버 주소
        ollama_model: 기본 LLM 모델명
        ollama_vision_model: Vision 모델명
        postgres_host: PostgreSQL 호스트
        postgres_port: PostgreSQL 포트 번호
        postgres_db: 데이터베이스명
        postgres_user: DB 사용자
        postgres_password: DB 비밀번호
        chroma_persist_dir: ChromaDB 저장 경로
        fastapi_base_url: FastAPI 서버 주소
    """

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "deepseek-r1"
    ollama_vision_model: str = "llava"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "connecthr"
    postgres_user: str = "admin"
    postgres_password: str = "password"
    chroma_persist_dir: str = "./outputs/chroma_db"
    fastapi_base_url: str = "http://localhost:8000"

    def get_postgres_dsn(self) -> str:
        """PostgreSQL DSN 연결 문자열을 반환합니다.

        Returns:
            psycopg2 호환 DSN 문자열
        """
        return (
            f"host={self.postgres_host} "
            f"port={self.postgres_port} "
            f"dbname={self.postgres_db} "
            f"user={self.postgres_user} "
            f"password={self.postgres_password}"
        )


def load_env(env_file: str = ".env") -> None:
    """지정된 경로의 .env 파일을 로딩합니다.

    현재 작업 디렉토리 기준으로 .env 파일을 찾습니다.
    파일이 없으면 시스템 환경 변수만 사용합니다.

    Args:
        env_file: .env 파일 경로 (기본값: ".env")
    """
    # --- Input ---
    env_path = Path(env_file)

    # --- Process ---
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=False)
        print(f"  .env 파일 로딩 완료: {env_path.resolve()}")
    else:
        # 상위 디렉토리에서도 탐색
        parent_env = Path("..") / env_file
        if parent_env.exists():
            load_dotenv(dotenv_path=parent_env, override=False)
            print(f"  .env 파일 로딩 완료 (상위 디렉토리): {parent_env.resolve()}")
        else:
            print(f"  경고: .env 파일을 찾을 수 없습니다. 시스템 환경 변수를 사용합니다.")

    # 기본값 적용 (환경 변수가 없는 경우에만)
    for key, default in DEFAULT_VALUES.items():
        if not os.environ.get(key):
            os.environ[key] = default

    # --- Output ---
    # 환경 변수가 os.environ에 반영된 상태


def validate_required_vars() -> list[str]:
    """필수 환경 변수의 존재 여부를 검증합니다.

    REQUIRED_VARS 목록에 정의된 변수 중 값이 비어 있는 항목을 반환합니다.

    Returns:
        누락된 환경 변수 이름 목록. 모두 존재하면 빈 리스트 반환.
    """
    # --- Input ---
    missing: list[str] = []

    # --- Process ---
    for var_name in REQUIRED_VARS:
        value = os.environ.get(var_name, "").strip()
        if not value:
            missing.append(var_name)

    # --- Output ---
    return missing


def build_config() -> AppConfig:
    """환경 변수를 읽어 AppConfig 객체를 생성하여 반환합니다.

    os.environ에서 값을 읽어 AppConfig 인스턴스를 구성합니다.
    타입 변환(포트 번호 정수화 등)도 이 함수에서 처리합니다.

    Returns:
        설정값이 채워진 AppConfig 인스턴스

    Raises:
        ValueError: POSTGRES_PORT가 정수로 변환되지 않을 경우
    """
    # --- Input ---
    raw_port = os.environ.get("POSTGRES_PORT", "5432")

    # --- Process ---
    try:
        postgres_port = int(raw_port)
    except ValueError:
        raise ValueError(
            f"POSTGRES_PORT 값이 올바르지 않습니다: '{raw_port}'. "
            "정수를 입력하십시오. 예: 5432"
        )

    config = AppConfig(
        ollama_base_url=os.environ.get("OLLAMA_BASE_URL", DEFAULT_VALUES["OLLAMA_BASE_URL"]),
        ollama_model=os.environ.get("OLLAMA_MODEL", DEFAULT_VALUES["OLLAMA_MODEL"]),
        ollama_vision_model=os.environ.get("OLLAMA_VISION_MODEL", DEFAULT_VALUES["OLLAMA_VISION_MODEL"]),
        postgres_host=os.environ.get("POSTGRES_HOST", DEFAULT_VALUES["POSTGRES_HOST"]),
        postgres_port=postgres_port,
        postgres_db=os.environ.get("POSTGRES_DB", DEFAULT_VALUES["POSTGRES_DB"]),
        postgres_user=os.environ.get("POSTGRES_USER", DEFAULT_VALUES["POSTGRES_USER"]),
        postgres_password=os.environ.get("POSTGRES_PASSWORD", DEFAULT_VALUES["POSTGRES_PASSWORD"]),
        chroma_persist_dir=os.environ.get("CHROMA_PERSIST_DIR", DEFAULT_VALUES["CHROMA_PERSIST_DIR"]),
        fastapi_base_url=os.environ.get("FASTAPI_BASE_URL", DEFAULT_VALUES["FASTAPI_BASE_URL"]),
    )

    # --- Output ---
    return config


def get_config(env_file: str = ".env") -> AppConfig:
    """환경 변수를 로딩하고 검증한 뒤 설정 객체를 반환하는 통합 진입 함수입니다.

    load_env → validate_required_vars → build_config 순서로 실행합니다.

    Args:
        env_file: .env 파일 경로 (기본값: ".env")

    Returns:
        검증이 완료된 AppConfig 인스턴스

    Raises:
        EnvironmentError: 필수 환경 변수가 누락된 경우
        ValueError: 환경 변수 타입 변환에 실패한 경우
    """
    # --- Input ---
    load_env(env_file)

    # --- Process ---
    missing_vars = validate_required_vars()
    if missing_vars:
        raise EnvironmentError(
            f"다음 필수 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}\n"
            ".env.example 파일을 참고하여 .env 파일을 작성하십시오."
        )

    config = build_config()

    # --- Output ---
    return config


if __name__ == "__main__":
    # 직접 실행 시 설정 정보를 출력합니다.
    try:
        cfg = get_config()
        print("=== 현재 설정값 ===")
        print(f"  Ollama URL  : {cfg.ollama_base_url}")
        print(f"  LLM 모델    : {cfg.ollama_model}")
        print(f"  Vision 모델 : {cfg.ollama_vision_model}")
        print(f"  PostgreSQL  : {cfg.postgres_host}:{cfg.postgres_port}/{cfg.postgres_db}")
        print(f"  ChromaDB    : {cfg.chroma_persist_dir}")
        print(f"  FastAPI     : {cfg.fastapi_base_url}")
    except (EnvironmentError, ValueError) as e:
        print(f"설정 오류: {e}")
