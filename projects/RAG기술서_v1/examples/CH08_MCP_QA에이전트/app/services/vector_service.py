"""
ChromaDB 벡터 검색 서비스.

OllamaEmbeddings(nomic-embed-text)를 사용하여 문서를 임베딩하고,
ChromaDB에서 유사도 기반 검색을 수행합니다.

환경 변수:
    OLLAMA_BASE_URL: Ollama 서버 URL (기본값: http://localhost:11434)
    EMBED_MODEL: 임베딩 모델명 (기본값: nomic-embed-text)
    CHROMA_PERSIST_DIR: ChromaDB 저장 경로 (기본값: ./data/chroma_db)
    COLLECTION_NAME: ChromaDB 컬렉션명 (기본값: rag_docs)
"""

import os

from dotenv import load_dotenv

load_dotenv()


class VectorService:
    """ChromaDB 벡터 검색 서비스.

    OllamaEmbeddings와 Chroma 클라이언트를 초기화하여
    문서 유사도 검색과 문서 수 조회를 제공합니다.

    Attributes:
        collection_name: ChromaDB 컬렉션명.
        vectorstore: LangChain Chroma 벡터 스토어 (초기화 실패 시 None).
    """

    def __init__(self) -> None:
        """
        OllamaEmbeddings와 Chroma 벡터 스토어를 초기화합니다.

        CHROMA_PERSIST_DIR 경로에 DB가 없으면 경고 메시지만 출력하고
        vectorstore를 None으로 설정합니다.
        """
        # --- Input ---
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        embed_model = os.getenv("EMBED_MODEL", "nomic-embed-text")
        chroma_persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
        self.collection_name = os.getenv("COLLECTION_NAME", "rag_docs")

        # --- Process ---
        self.vectorstore = None

        try:
            from langchain_chroma import Chroma
            from langchain_ollama import OllamaEmbeddings

            embeddings = OllamaEmbeddings(
                model=embed_model,
                base_url=ollama_base_url,
            )

            self.vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=embeddings,
                persist_directory=chroma_persist_dir,
            )

            # --- Output ---
            print(f"[VectorService] 초기화 완료 — collection={self.collection_name}")

        except Exception as exc:
            print(
                f"[VectorService] 경고: ChromaDB 초기화에 실패했습니다. "
                f"scripts/ingest.py를 먼저 실행하십시오. 오류: {exc}"
            )

    def search_unstructured(self, query: str, k: int = 3) -> list[dict]:
        """
        비정형 문서에서 유사도 검색을 수행합니다.

        Args:
            query: 검색할 질의 문자열.
            k: 반환할 최대 문서 수 (기본값: 3).

        Returns:
            list[dict]: [{"content": 문서 내용, "source": 출처, "score": 유사도 점수}]
                        벡터 스토어가 없으면 빈 리스트 반환.
        """
        # --- Input ---
        if self.vectorstore is None:
            return []

        # --- Process ---
        try:
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            output = []
            for doc, score in results:
                output.append(
                    {
                        "content": doc.page_content,
                        "source": doc.metadata.get("source", "알 수 없음"),
                        "score": round(float(score), 4),
                    }
                )
            # --- Output ---
            return output

        except Exception as exc:
            print(f"[VectorService] 검색 오류: {exc}")
            return []

    def get_doc_count(self) -> int:
        """
        ChromaDB에 저장된 총 문서 수를 반환합니다.

        Returns:
            int: 총 문서 수. 조회 실패 시 0 반환.
        """
        # --- Input ---
        if self.vectorstore is None:
            return 0

        # --- Process ---
        try:
            collection = self.vectorstore._collection
            count = collection.count()
            # --- Output ---
            return count
        except Exception:
            return 0


# 싱글톤 인스턴스
vector_service = VectorService()
