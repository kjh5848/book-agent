"""ChromaDB 기반 유사도 검색 모듈.

커넥트HR 사내 문서가 저장된 ChromaDB 컬렉션에서
사용자 질문과 유사한 청크를 검색합니다.
Ollama 임베딩을 1차 시도하고, 연결 불가 시 sentence-transformers로 자동 대체합니다.
"""

import os
from typing import Optional

# 환경 변수에서 설정 로드
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "connecthr_docs")
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "3"))

# sentence-transformers fallback 모델 (한국어 지원)
FALLBACK_EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"


def _get_ollama_embedding(text: str) -> Optional[list[float]]:
    """Ollama API로 단일 텍스트를 임베딩합니다.

    Args:
        text: 임베딩할 텍스트 문자열

    Returns:
        임베딩 벡터. Ollama 연결 실패 시 None을 반환합니다.
    """

    # --- Input ---
    try:
        import requests
    except ImportError:
        return None

    # --- Process ---
    api_url = f"{OLLAMA_BASE_URL}/api/embeddings"
    try:
        resp = requests.post(
            api_url,
            json={"model": OLLAMA_EMBED_MODEL, "prompt": text},
            timeout=30,
        )
        resp.raise_for_status()
        embedding = resp.json().get("embedding")
        if embedding is None:
            return None
        return embedding
    except Exception:
        return None

    # --- Output ---
    # 임베딩 벡터 반환 또는 None


def _get_sentence_transformer_embedding(text: str) -> list[float]:
    """sentence-transformers로 단일 텍스트를 임베딩합니다.

    Ollama를 사용할 수 없을 때 대체 수단으로 사용됩니다.

    Args:
        text: 임베딩할 텍스트 문자열

    Returns:
        임베딩 벡터 (384차원)

    Raises:
        RuntimeError: sentence-transformers 패키지 설치가 되지 않은 경우
    """

    # --- Input ---
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        raise RuntimeError(
            "sentence-transformers가 설치되지 않았습니다.\n"
            "다음 명령어로 설치하십시오: pip install sentence-transformers"
        )

    # --- Process ---
    # 모델을 매번 로드하는 비용을 줄이기 위해 모듈 수준에서 캐싱
    if not hasattr(_get_sentence_transformer_embedding, "_model"):
        print(f"  [Fallback] sentence-transformers 모델 로딩: {FALLBACK_EMBED_MODEL}")
        print("  (최초 실행 시 모델 다운로드로 수 분이 소요될 수 있습니다)")
        _get_sentence_transformer_embedding._model = SentenceTransformer(FALLBACK_EMBED_MODEL)

    model = _get_sentence_transformer_embedding._model
    vector = model.encode(text if text.strip() else " ", convert_to_numpy=True)

    # --- Output ---
    return vector.tolist()


def _embed_query(query: str) -> tuple[list[float], str]:
    """쿼리 텍스트를 임베딩하고 사용된 엔진 이름을 반환합니다.

    Ollama를 1차 시도하고 실패하면 sentence-transformers로 대체합니다.

    Args:
        query: 임베딩할 쿼리 문자열

    Returns:
        (임베딩 벡터, 사용된 엔진 이름) 튜플

    Raises:
        RuntimeError: 모든 임베딩 방법이 실패한 경우
    """

    # --- Input ---
    if not query or not query.strip():
        raise ValueError(
            "검색 쿼리가 비어있습니다. 질문을 입력하십시오."
        )

    # --- Process ---
    # 1차 시도: Ollama
    embedding = _get_ollama_embedding(query)
    if embedding is not None:
        engine = "ollama"
    else:
        # 2차 시도: sentence-transformers
        embedding = _get_sentence_transformer_embedding(query)
        engine = "sentence-transformers"

    # --- Output ---
    return embedding, engine


class ChromaRetriever:
    """ChromaDB 컬렉션에서 유사도 검색을 수행하는 클래스.

    커넥트HR 사내 문서 벡터 DB에서 사용자 질문과 관련된
    청크를 검색하고 결과를 반환합니다.

    Attributes:
        persist_dir: ChromaDB 파일이 저장된 디렉토리 경로
        collection_name: 검색 대상 컬렉션 이름
        default_k: 기본 반환 결과 수
        collection: ChromaDB 컬렉션 인스턴스 (초기화 후 설정)
        embed_engine: 현재 사용 중인 임베딩 엔진 이름
    """

    def __init__(
        self,
        persist_dir: Optional[str] = None,
        collection_name: Optional[str] = None,
        default_k: Optional[int] = None,
    ) -> None:
        """ChromaRetriever를 초기화합니다.

        Args:
            persist_dir: ChromaDB 저장 디렉토리 경로.
                None이면 환경 변수 CHROMA_PERSIST_DIR 값을 사용합니다.
            collection_name: 검색할 컬렉션 이름.
                None이면 환경 변수 CHROMA_COLLECTION 값을 사용합니다.
            default_k: 기본 반환 결과 수.
                None이면 환경 변수 RAG_TOP_K 값을 사용합니다.

        Raises:
            RuntimeError: chromadb 패키지가 설치되지 않은 경우
            RuntimeError: 지정한 컬렉션이 존재하지 않거나 비어있는 경우
        """

        # --- Input ---
        self.persist_dir = persist_dir or CHROMA_PERSIST_DIR
        self.collection_name = collection_name or CHROMA_COLLECTION
        self.default_k = default_k or RAG_TOP_K
        self.embed_engine = "unknown"

        # --- Process ---
        try:
            import chromadb
        except ImportError:
            raise RuntimeError(
                "chromadb가 설치되지 않았습니다.\n"
                "다음 명령어로 설치하십시오: pip install chromadb"
            )

        try:
            client = chromadb.PersistentClient(path=self.persist_dir)
            # get_collection: 없으면 예외 발생 (의도적 — 먼저 DB를 구축해야 함)
            self.collection = client.get_collection(name=self.collection_name)
        except Exception as e:
            raise RuntimeError(
                f"ChromaDB 컬렉션을 로드할 수 없습니다.\n"
                f"컬렉션 이름: '{self.collection_name}'\n"
                f"저장 경로: '{self.persist_dir}'\n"
                f"CH06 벡터 DB 구축 예제를 먼저 실행하십시오.\n"
                f"오류: {e}"
            ) from e

        doc_count = self.collection.count()
        print(f"  ChromaRetriever 초기화 완료: '{self.collection_name}' ({doc_count}개 문서)")

        # --- Output ---
        # self.collection에 컬렉션 인스턴스가 설정됨

    def search(self, query: str, k: Optional[int] = None) -> list[dict]:
        """쿼리와 유사한 상위 k개 문서를 반환합니다.

        Args:
            query: 검색할 질문 또는 키워드 문자열
            k: 반환할 결과 수. None이면 default_k를 사용합니다.

        Returns:
            검색 결과 딕셔너리 리스트. 각 원소는 다음 키를 포함합니다:
            - content (str): 청크 텍스트
            - source (str): 출처 파일명
            - score (float): 유사도 점수 (0.0~1.0, 높을수록 관련성 높음)
            - metadata (dict): 추가 메타데이터

        Raises:
            ValueError: 쿼리가 비어있는 경우
            RuntimeError: 검색 중 오류가 발생한 경우
        """

        # --- Input ---
        top_k = k or self.default_k
        actual_k = min(top_k, self.collection.count())

        if actual_k == 0:
            print("  [경고] 컬렉션에 저장된 문서가 없습니다.")
            return []

        # --- Process ---
        # 쿼리 임베딩 생성
        query_embedding, self.embed_engine = _embed_query(query)

        # ChromaDB 검색 수행
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=actual_k,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as e:
            raise RuntimeError(
                f"ChromaDB 검색 실패\n쿼리: '{query}'\n오류: {e}"
            ) from e

        # 결과 형식 변환
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        formatted: list[dict] = []
        for doc, meta, dist in zip(docs, metas, distances):
            # 코사인 거리(0~2) → 유사도(0~1)로 변환
            similarity_score = max(0.0, 1.0 - dist)
            formatted.append({
                "content": doc,
                "source": meta.get("source", "unknown"),
                "score": round(similarity_score, 4),
                "metadata": meta,
            })

        # --- Output ---
        return formatted

    def search_with_score(self, query: str, k: Optional[int] = None) -> list[dict]:
        """유사도 점수를 포함하여 상위 k개 문서를 반환합니다.

        search()와 동일한 결과를 반환하지만, 점수를 명시적으로 로그에 출력합니다.

        Args:
            query: 검색할 질문 또는 키워드 문자열
            k: 반환할 결과 수. None이면 default_k를 사용합니다.

        Returns:
            search()와 동일한 형식의 검색 결과 리스트.
            각 원소에 score 키가 포함됩니다.
        """

        # --- Input ---
        results = self.search(query=query, k=k)

        # --- Process ---
        print(f"\n  검색 결과 ({len(results)}개) — 쿼리: '{query}'")
        for i, result in enumerate(results, start=1):
            source = result["source"]
            score = result["score"]
            preview = result["content"][:60].replace("\n", " ")
            print(f"  [{i}] 출처: {source} | 유사도: {score:.2%} | 미리보기: {preview}...")

        # --- Output ---
        return results

    def get_collection_info(self) -> dict:
        """컬렉션 기본 정보를 반환합니다.

        Returns:
            컬렉션 정보 딕셔너리:
            - collection_name (str): 컬렉션 이름
            - doc_count (int): 저장된 문서 수
            - persist_dir (str): 저장 경로
            - embed_engine (str): 현재 임베딩 엔진
        """

        # --- Input / Process ---
        doc_count = self.collection.count()

        info = {
            "collection_name": self.collection_name,
            "doc_count": doc_count,
            "persist_dir": self.persist_dir,
            "embed_engine": self.embed_engine,
        }

        # --- Output ---
        return info
