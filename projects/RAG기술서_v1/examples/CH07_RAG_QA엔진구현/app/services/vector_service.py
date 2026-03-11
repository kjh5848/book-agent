"""
ChromaDB 벡터 검색 서비스.

CH06에서 생성한 ChromaDB(nomic-embed-text 임베딩)에 연결하여
비정형 문서 유사도 검색을 제공합니다.

CH06 → CH07 연결:
    CH06 outputs/chroma_db/ → CH07 data/chroma_db/ 복사 후 사용
    임베딩 모델: nomic-embed-text (Ollama, CH06과 동일 모델 필수)
"""

import os
from typing import Any

from langchain_community.vectorstores import Chroma

VECTOR_DB_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")


class VectorService:
    """ChromaDB 벡터 검색 서비스 — Ollama 임베딩 사용."""

    def __init__(self) -> None:
        """
        OllamaEmbeddings를 초기화하고 ChromaDB에 연결합니다.

        환경 변수:
            OLLAMA_BASE_URL    : Ollama 서버 주소 (기본값: "http://localhost:11434")
            EMBED_MODEL        : 임베딩 모델명 (기본값: "nomic-embed-text")
            CHROMA_PERSIST_DIR : ChromaDB 저장 경로 (기본값: "./data/chroma_db")
            COLLECTION_NAME    : ChromaDB 컬렉션 이름 (기본값: "rag_docs")

        data/chroma_db 디렉토리가 없으면 경고만 출력하고 지연 초기화를 지원합니다.
        ChromaDB가 없는 상태에서도 서버가 정상 기동됩니다.
        """
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        embed_model = os.getenv("EMBED_MODEL", "nomic-embed-text")
        collection_name = os.getenv("COLLECTION_NAME", "rag_docs")

        print(f"[VectorService] 초기화 중 (임베딩 모델: {embed_model}, DB 경로: {VECTOR_DB_DIR})")

        try:
            from langchain_ollama import OllamaEmbeddings
            self.embeddings = OllamaEmbeddings(base_url=ollama_url, model=embed_model)
        except ImportError as exc:
            raise ImportError(
                "langchain-ollama 패키지가 설치되지 않았습니다. "
                "pip install langchain-ollama 를 실행하십시오."
            ) from exc

        self.vector_db: Chroma | None = None
        self.collection_name = collection_name

        if os.path.exists(VECTOR_DB_DIR):
            try:
                self.vector_db = Chroma(
                    persist_directory=VECTOR_DB_DIR,
                    embedding_function=self.embeddings,
                    collection_name=collection_name,
                )
                print("[VectorService] ChromaDB 연결 완료.")
            except Exception as exc:
                print(f"[VectorService] ChromaDB 연결 실패: {exc}")
        else:
            print(
                f"[VectorService] 경고: {VECTOR_DB_DIR} 디렉토리가 없습니다. "
                "CH06 outputs/chroma_db 를 복사하십시오."
            )

    def search_unstructured(self, query: str, k: int = 3) -> list[dict[str, Any]]:
        """
        비정형 문서 유사도 검색을 수행합니다.

        ChromaDB가 초기화되지 않은 경우 지연 초기화를 시도합니다.
        Chroma 유사도 점수는 거리(낮을수록 유사)를 반환하므로
        1 - score 변환으로 0~1 범위의 유사도로 표시합니다.

        Args:
            query: 검색 질문 문자열.
            k    : 반환할 최대 문서 수 (기본값: 3).

        Returns:
            list[dict]: [
                {
                    "content": 문서 본문,
                    "source" : 출처 파일명,
                    "score"  : 유사도 점수 (0~1, 높을수록 유사)
                },
                ...
            ]
        """
        # --- Input ---
        if self.vector_db is None:
            # 지연 초기화 시도
            if os.path.exists(VECTOR_DB_DIR):
                print(f"[VectorService] ChromaDB 지연 초기화 중 (경로: {VECTOR_DB_DIR})")
                try:
                    self.vector_db = Chroma(
                        persist_directory=VECTOR_DB_DIR,
                        embedding_function=self.embeddings,
                        collection_name=self.collection_name,
                    )
                except Exception as exc:
                    print(f"[VectorService] 지연 초기화 실패: {exc}")
                    return []
            else:
                print("[VectorService] 경고: ChromaDB가 없습니다. 빈 결과를 반환합니다.")
                return []

        # --- Process ---
        try:
            raw_results = self.vector_db.similarity_search_with_score(query, k=k)
        except Exception as exc:
            print(f"[VectorService] 유사도 검색 오류: {exc}")
            return []

        # --- Output ---
        formatted: list[dict[str, Any]] = []
        for doc, distance in raw_results:
            # Chroma 거리 → 유사도 변환 (0~1 범위)
            similarity = max(0.0, 1.0 - float(distance))
            formatted.append(
                {
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", "알 수 없음"),
                    "score": round(similarity, 4),
                }
            )
        return formatted


# 싱글톤 인스턴스
vector_service = VectorService()
