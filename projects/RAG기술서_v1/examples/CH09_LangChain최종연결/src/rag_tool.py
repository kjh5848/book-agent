"""
CH09 LangChain 최종 연결 — RAG 도구 모듈.

ChromaDB + Ollama 임베딩 기반 사내 문서 검색 도구를 LangChain Tool로 제공합니다.
CH07에서 구축한 벡터 DB를 조회하여 관련 문서 내용을 반환합니다.

전제 조건:
    - CH07 RAG QA 엔진에서 ChromaDB가 이미 구축되어 있어야 합니다.
    - .env의 CHROMA_PERSIST_DIR에 ChromaDB 경로를 설정하십시오.
    - Ollama 서버가 실행 중이어야 하며 임베딩 모델이 설치되어 있어야 합니다.

환경 변수:
    CHROMA_PERSIST_DIR : ChromaDB 영속 디렉토리 경로
    COLLECTION_NAME    : ChromaDB 컬렉션 이름 (기본값: rag_docs)
    EMBED_MODEL        : 임베딩 모델명 (기본값: nomic-embed-text)
    OLLAMA_BASE_URL    : Ollama 서버 URL (기본값: http://localhost:11434)
"""

import os

from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()


def _build_retriever(k: int = 3):
    """환경 변수 설정을 기반으로 ChromaDB 검색기를 초기화합니다.

    langchain_chroma 및 chromadb를 지연 임포트하여 모듈 로딩 시
    chromadb 초기화 오류가 전파되지 않도록 합니다.

    Args:
        k: 반환할 유사 문서 최대 개수.

    Returns:
        Chroma: 검색 준비된 ChromaDB 인스턴스.

    Raises:
        RuntimeError: ChromaDB 연결에 실패하는 경우.
    """
    # --- Input ---
    chroma_dir = os.getenv("CHROMA_PERSIST_DIR", "../CH07_RAG_QA엔진구현/data/chroma_db")
    collection_name = os.getenv("COLLECTION_NAME", "rag_docs")
    embed_model = os.getenv("EMBED_MODEL", "nomic-embed-text")
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # --- Process ---
    # 지연 임포트: chromadb는 Python 3.13+ 환경에서 pydantic v1 호환성 이슈가 있으므로
    # 실제 도구 호출 시점에 임포트하여 모듈 로딩 오류를 방지합니다.
    try:
        from langchain_chroma import Chroma
        from langchain_ollama import OllamaEmbeddings

        embeddings = OllamaEmbeddings(
            model=embed_model,
            base_url=ollama_base_url,
        )
        vectorstore = Chroma(
            collection_name=collection_name,
            persist_directory=chroma_dir,
            embedding_function=embeddings,
        )
    except Exception as exc:
        raise RuntimeError(
            f"ChromaDB 연결에 실패했습니다: {exc}\n"
            f"경로({chroma_dir})와 Ollama 서버({ollama_base_url}) 상태를 확인하십시오.\n"
            "Python 3.13 이상 환경에서는 chromadb와 pydantic v1 호환성 문제가 발생할 수 있습니다. "
            "Python 3.9~3.12 환경에서 실행하십시오."
        ) from exc

    # --- Output ---
    return vectorstore


@tool
def search_company_documents(query: str) -> str:
    """사내 문서(규정, 가이드, 정책)를 검색하여 관련 내용을 반환합니다.

    CH07 ChromaDB에 저장된 사내 문서를 Ollama 임베딩 기반 유사도 검색으로 조회합니다.
    상위 3개 결과를 출처와 함께 반환합니다.

    Args:
        query: 검색할 내용 (예: "연차 신청 기한", "재택근무 정책").

    Returns:
        str: 관련 문서 내용과 출처 정보.
             예: "출처: HR_취업규칙.pdf\n내용: 연차는 발생일로부터 1년 내 사용해야 합니다."
             결과가 없으면 "관련 문서를 찾지 못했습니다." 를 반환합니다.
             ChromaDB 연결 실패 시 오류 안내 메시지를 반환합니다.
    """
    # --- Input ---
    k = 3

    # --- Process ---
    try:
        vectorstore = _build_retriever(k=k)
        docs = vectorstore.similarity_search(query, k=k)
    except RuntimeError as exc:
        return (
            f"문서 검색 중 오류가 발생했습니다: {exc}\n"
            "CH07 ChromaDB가 올바르게 구축되어 있는지 확인하십시오."
        )
    except Exception as exc:
        return f"예상치 못한 오류가 발생했습니다: {exc}"

    if not docs:
        return "관련 문서를 찾지 못했습니다."

    # 검색 결과를 출처와 함께 포맷팅
    result_parts: list[str] = []
    for i, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source", doc.metadata.get("file_name", "출처 미상"))
        content = doc.page_content.strip()
        result_parts.append(f"[{i}] 출처: {source}\n내용: {content}")

    # --- Output ---
    return "\n\n".join(result_parts)


# LangChain Tool 인스턴스 (agent.py에서 사용)
RAG_TOOL = search_company_documents
