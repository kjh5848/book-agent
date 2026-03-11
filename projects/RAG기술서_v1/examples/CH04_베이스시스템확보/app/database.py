"""
database.py
===========
SQLAlchemy 엔진 및 세션 팩토리를 구성합니다.
FastAPI의 Depends(get_db) 패턴에서 사용하는 세션 생성기를 제공합니다.
"""

import os
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# --- Input ---
# 환경 변수에서 PostgreSQL 연결 정보를 읽습니다.
load_dotenv()

POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB: str = os.getenv("POSTGRES_DB", "rag_db")
POSTGRES_USER: str = os.getenv("POSTGRES_USER", "rag_user")
POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "rag_password")

# --- Process ---
# PostgreSQL 접속 URL 구성 및 엔진 생성
DATABASE_URL: str = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # 연결 유효성 사전 확인 (네트워크 단절 대응)
    echo=False,           # SQL 쿼리 로깅 비활성화 (디버깅 시 True로 변경)
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """모든 ORM 모델의 기반 클래스입니다."""
    pass


# --- Output ---
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI 의존성 주입용 DB 세션 생성기입니다.

    각 요청마다 새 세션을 생성하고, 요청 완료 후 반드시 세션을 닫습니다.

    Yields:
        Session: SQLAlchemy 데이터베이스 세션 객체

    Examples:
        @app.get("/example")
        def example_endpoint(db: Session = Depends(get_db)):
            ...
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
