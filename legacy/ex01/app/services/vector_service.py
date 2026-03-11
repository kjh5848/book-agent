import os
from typing import List, Dict, Any
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

VECTOR_DB_DIR = "data/embedding_db"

class VectorService:
    def __init__(self):
        print(f"[VectorService] 초기화 중 (디렉토리: {VECTOR_DB_DIR})")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="jhgan/ko-sroberta-multitask",
            model_kwargs={'device': 'cpu'}
        )
        self.vector_db = None
        if os.path.exists(VECTOR_DB_DIR):
            self.vector_db = Chroma(
                persist_directory=VECTOR_DB_DIR,
                embedding_function=self.embeddings
            )

    def search_unstructured(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """비정형 데이터(문서) 검색 (동적 초기화 지원)"""
        if not self.vector_db:
            if os.path.exists(VECTOR_DB_DIR):
                print(f"[VectorService] 벡터 DB 지연 초기화 중 (경로: {VECTOR_DB_DIR})")
                self.vector_db = Chroma(
                    persist_directory=VECTOR_DB_DIR,
                    embedding_function=self.embeddings
                )
            else:
                print("[VectorService] 경고: 벡터 DB가 초기화되지 않았으며 디렉토리를 찾을 수 없습니다.")
                return []
        
        results = self.vector_db.similarity_search_with_score(query, k=k)
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "source": doc.metadata.get("source", "Unknown"),
                "score": float(score)
            })
        return formatted_results

# 싱글톤 인스턴스
vector_service = VectorService()
