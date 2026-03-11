"""
CH09 LangChain 최종 연결 — 설정 모듈.

LLM, 애플리케이션 전반의 설정값을 dataclass로 관리합니다.
.env 파일에서 값을 읽어 AppConfig 객체로 반환하며,
로깅 핸들러와 LangChain SQLite 캐시를 초기화합니다.

환경 변수:
    LLM_PROVIDER      : LLM 공급자 (ollama | openai, 기본값: ollama)
    LLM_MODEL_NAME    : 모델명 (기본값: deepseek-r1:1.5b)
    OLLAMA_BASE_URL   : Ollama 서버 URL (기본값: http://localhost:11434)
    OPENAI_API_KEY    : OpenAI API 키 (PROVIDER=openai 시 필요)
    LLM_TIMEOUT       : 요청 타임아웃 초 (기본값: 60)
    MAX_RETRIES       : 최대 재시도 횟수 (기본값: 2)
    ENABLE_CACHE      : LangChain 캐시 활성화 여부 (기본값: true)
    LOG_LEVEL         : 로그 레벨 (기본값: INFO)
"""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass
class LLMConfig:
    """LLM 연결 및 동작 설정을 담는 데이터 클래스입니다.

    Attributes:
        model: 사용할 LLM 모델명.
        provider: LLM 공급자 (ollama | openai).
        base_url: Ollama 서버 URL (provider=ollama 시 사용).
        temperature: 생성 다양성 (0.0~1.0, 낮을수록 결정적).
        timeout: LLM 응답 대기 타임아웃 (초).
        max_retries: 타임아웃 또는 오류 발생 시 최대 재시도 횟수.
    """

    model: str
    provider: str
    base_url: str
    temperature: float = 0.1
    timeout: int = 60
    max_retries: int = 2


@dataclass
class AppConfig:
    """애플리케이션 전체 설정을 담는 데이터 클래스입니다.

    Attributes:
        llm: LLM 연결 설정.
        log_level: 로깅 레벨 문자열 (DEBUG | INFO | WARNING | ERROR).
        log_file: 로그 파일 경로.
        enable_cache: LangChain SQLite 캐시 활성화 여부.
        cache_dir: 캐시 파일 저장 디렉토리.
        fastapi_base_url: CH04 FastAPI 서버 베이스 URL.
        chroma_persist_dir: ChromaDB 영속 디렉토리 경로.
        collection_name: ChromaDB 컬렉션 이름.
        embed_model: 임베딩 모델명.
    """

    llm: LLMConfig
    log_level: str = "INFO"
    log_file: str = "./outputs/logs/app.log"
    enable_cache: bool = True
    cache_dir: str = "./outputs/cache"
    fastapi_base_url: str = "http://localhost:8000"
    chroma_persist_dir: str = "../CH07_RAG_QA엔진구현/data/chroma_db"
    collection_name: str = "rag_docs"
    embed_model: str = "nomic-embed-text"


def load_config() -> AppConfig:
    """환경 변수(.env)에서 설정을 읽어 AppConfig 객체를 반환합니다.

    필요한 디렉토리(캐시, 로그)가 없으면 자동으로 생성합니다.

    Returns:
        AppConfig: 전체 애플리케이션 설정 객체.

    Raises:
        SystemExit: PROVIDER=openai 시 OPENAI_API_KEY가 없는 경우.
    """
    # --- Input ---
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    model = os.getenv("LLM_MODEL_NAME", "deepseek-r1:1.5b")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    timeout = int(os.getenv("LLM_TIMEOUT", "60"))
    max_retries = int(os.getenv("MAX_RETRIES", "2"))
    enable_cache_str = os.getenv("ENABLE_CACHE", "true").lower()
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # --- Process ---
    # OpenAI 공급자 선택 시 API 키 검증
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
            print(".env 파일에 API 키를 입력하십시오. (.env.example 참조)")
            import sys
            sys.exit(1)

    llm_config = LLMConfig(
        model=model,
        provider=provider,
        base_url=base_url,
        timeout=timeout,
        max_retries=max_retries,
    )

    enable_cache = enable_cache_str in ("true", "1", "yes")

    app_config = AppConfig(
        llm=llm_config,
        log_level=log_level,
        log_file="./outputs/logs/app.log",
        enable_cache=enable_cache,
        cache_dir="./outputs/cache",
        fastapi_base_url=os.getenv("FASTAPI_BASE_URL", "http://localhost:8000"),
        chroma_persist_dir=os.getenv(
            "CHROMA_PERSIST_DIR", "../CH07_RAG_QA엔진구현/data/chroma_db"
        ),
        collection_name=os.getenv("COLLECTION_NAME", "rag_docs"),
        embed_model=os.getenv("EMBED_MODEL", "nomic-embed-text"),
    )

    # 캐시 디렉토리 생성
    Path(app_config.cache_dir).mkdir(parents=True, exist_ok=True)

    # 로그 디렉토리 생성
    Path(app_config.log_file).parent.mkdir(parents=True, exist_ok=True)

    # --- Output ---
    return app_config


def setup_logging(config: AppConfig) -> logging.Logger:
    """파일과 콘솔에 동시 출력하는 듀얼 핸들러 로거를 설정합니다.

    로그 포맷: "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
    로그 파일 경로는 AppConfig.log_file 에서 읽습니다.

    Args:
        config: 애플리케이션 설정 객체.

    Returns:
        logging.Logger: 설정 완료된 루트 로거.
    """
    # --- Input ---
    log_format = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    level = getattr(logging, config.log_level, logging.INFO)

    # --- Process ---
    # 루트 로거 설정
    logger = logging.getLogger("ch09")
    logger.setLevel(level)

    # 이미 핸들러가 등록된 경우 중복 추가 방지
    if logger.handlers:
        logger.handlers.clear()

    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 파일 핸들러
    try:
        file_handler = logging.FileHandler(config.log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except OSError as exc:
        logger.warning("로그 파일 핸들러 생성 실패: %s — 콘솔 출력만 사용합니다.", exc)

    # --- Output ---
    return logger


def setup_cache(config: AppConfig) -> None:
    """LangChain SQLiteCache를 설정하고 전역 LLM 캐시로 등록합니다.

    캐시가 활성화된 경우(config.enable_cache=True) 동일한 프롬프트를
    재질의할 때 캐시에서 즉시 응답을 반환합니다.

    Args:
        config: 애플리케이션 설정 객체.

    Returns:
        None
    """
    # --- Input ---
    if not config.enable_cache:
        return

    # --- Process ---
    try:
        from langchain_community.cache import SQLiteCache
        import langchain

        cache_path = os.path.join(config.cache_dir, "langchain_cache.db")
        cache = SQLiteCache(database_path=cache_path)
        langchain.llm_cache = cache
        print(f"[Config] LangChain SQLiteCache 활성화 — {cache_path}")
    except ImportError:
        print(
            "[Config] langchain-community 패키지가 없어 캐시를 비활성화합니다. "
            "pip install langchain-community 명령으로 설치하십시오."
        )

    # --- Output ---
