"""
retriever.py — ChromaDB 기반 LangChain Retriever 설정 모듈

ChromaDB에 저장된 문서를 LangChain VectorStoreRetriever로 래핑하여
RAG Chain이 유사도 검색을 수행할 수 있도록 준비합니다.
"""

import os
import chromadb
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.vectorstores import VectorStoreRetriever


def get_chroma_client(persist_dir: str) -> chromadb.ClientAPI:
    """
    ChromaDB 영속 클라이언트를 반환합니다.

    Args:
        persist_dir: ChromaDB 데이터가 저장된 디렉토리 경로.

    Returns:
        PersistentClient 인스턴스.

    Raises:
        FileNotFoundError: 지정한 경로가 존재하지 않을 경우.
    """

    # --- Input ---
    if not os.path.exists(persist_dir):
        raise FileNotFoundError(
            f"ChromaDB 경로를 찾을 수 없습니다: '{persist_dir}'\n"
            "CH06 실습을 먼저 완료하거나 올바른 경로를 .env에 설정하십시오."
        )

    # --- Process ---
    client = chromadb.PersistentClient(path=persist_dir)

    # --- Output ---
    return client


def get_retriever(
    persist_dir: str = "./data/chroma_db",
    collection_name: str = "rag_docs",
    k: int = 3,
    filter_dept: str | None = None,
) -> VectorStoreRetriever:
    """
    LangChain VectorStoreRetriever를 반환합니다.

    ChromaDB에 저장된 문서 컬렉션을 LangChain Chroma 래퍼로 감싼 뒤,
    as_retriever()를 호출하여 RAG Chain과 연동 가능한 Retriever를 생성합니다.
    부서 필터(filter_dept)를 지정하면 해당 부서 문서만 검색합니다.

    Args:
        persist_dir: ChromaDB 영속 데이터 디렉토리 경로.
        collection_name: 검색 대상 컬렉션 이름.
        k: 유사도 검색 시 반환할 문서 수.
        filter_dept: 부서 메타데이터 필터. None이면 전체 검색.

    Returns:
        LangChain VectorStoreRetriever 인스턴스.

    Raises:
        FileNotFoundError: ChromaDB 경로가 존재하지 않을 경우.
        ValueError: 컬렉션에 문서가 없을 경우.
    """

    # --- Input ---
    embed_model = os.getenv("EMBED_MODEL", "nomic-embed-text")
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    embedding_function = OllamaEmbeddings(
        model=embed_model,
        base_url=ollama_base_url,
    )

    # --- Process ---
    # ChromaDB 경로 유효성 확인
    if not os.path.exists(persist_dir):
        raise FileNotFoundError(
            f"ChromaDB 경로를 찾을 수 없습니다: '{persist_dir}'\n"
            "CH06 실습을 먼저 완료한 뒤 아래 명령으로 데이터를 복사하십시오:\n"
            "  cp -r ../CH06_벡터DB구축/outputs/chroma_db ./data/chroma_db"
        )

    # LangChain Chroma 래퍼 생성
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embedding_function,
        persist_directory=persist_dir,
    )

    # 문서 수 확인
    doc_count = vectorstore._collection.count()
    if doc_count == 0:
        raise ValueError(
            f"컬렉션 '{collection_name}'에 문서가 없습니다.\n"
            "CH06 실습을 먼저 완료하여 문서를 ChromaDB에 저장하십시오."
        )

    # 검색 설정 구성 (부서 필터 적용 여부 결정)
    search_kwargs: dict = {"k": k}
    if filter_dept is not None:
        search_kwargs["filter"] = {"department": filter_dept}

    # Retriever 생성
    retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)

    # --- Output ---
    return retriever
