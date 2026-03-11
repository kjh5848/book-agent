"""BM25 + 벡터 하이브리드 검색 모듈.

키워드 매칭에 강한 BM25와 의미적 유사도 검색에 강한 ChromaDB를
결합하여 각각의 약점을 보완합니다. Reciprocal Rank Fusion(RRF)으로
두 검색 결과의 순위 점수를 통합합니다.
"""

import os
from typing import Optional

# rank_bm25 선택적 임포트
try:
    from rank_bm25 import BM25Okapi

    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False

# ChromaDB 선택적 임포트
try:
    import chromadb

    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./outputs/chroma_db")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "connecthr_docs")


class HybridSearch:
    """BM25와 벡터 검색을 결합한 하이브리드 검색 클래스.

    BM25는 키워드 빈도 기반 전통적 검색으로 정확한 용어 매칭에 강하고,
    벡터 검색은 의미적 유사도로 동의어·패러프레이즈를 처리합니다.
    두 결과를 RRF(Reciprocal Rank Fusion)로 결합하여 최종 결과를 반환합니다.

    Attributes:
        collection_name: ChromaDB 컬렉션 이름
        chroma_client: ChromaDB 클라이언트
        collection: ChromaDB 컬렉션
        bm25_corpus: BM25 인덱싱에 사용된 문서 리스트
        bm25_index: BM25Okapi 인덱스
        is_mock_mode: 패키지 미설치 시 Mock 모드 여부
    """

    def __init__(self, collection_name: str = CHROMA_COLLECTION) -> None:
        """HybridSearch를 초기화합니다.

        Args:
            collection_name: 벡터 검색에 사용할 ChromaDB 컬렉션 이름
        """

        # --- Input ---
        self.collection_name = collection_name
        self.chroma_client = None
        self.collection = None
        self.bm25_corpus: list[dict] = []
        self.bm25_index: Optional[object] = None
        self.is_mock_mode = False

        # --- Process ---
        if not BM25_AVAILABLE:
            print("  [경고] rank-bm25 패키지가 설치되지 않았습니다.")
            print("  설치 명령어: pip install rank-bm25")
            self.is_mock_mode = True

        if not CHROMADB_AVAILABLE:
            print("  [경고] chromadb 패키지가 설치되지 않았습니다.")
            self.is_mock_mode = True

        if not self.is_mock_mode:
            try:
                self.chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
                self.collection = self.chroma_client.get_or_create_collection(
                    name=collection_name,
                    metadata={"hnsw:space": "cosine"},
                )
                self._build_bm25_index()
                print(f"  [HybridSearch] 초기화 완료: {collection_name}")
            except Exception as e:
                print(f"  [경고] HybridSearch 초기화 실패: {e}. Mock 모드로 전환합니다.")
                self.is_mock_mode = True

        if self.is_mock_mode:
            print("  [HybridSearch] Mock 모드로 실행합니다.")

        # --- Output ---
        # self.bm25_index 및 self.collection 설정 완료

    def _build_bm25_index(self) -> None:
        """ChromaDB에서 모든 문서를 가져와 BM25 인덱스를 구축합니다.

        Raises:
            RuntimeError: ChromaDB 연결이 없는 경우
        """

        # --- Input ---
        if not self.collection:
            raise RuntimeError("ChromaDB 컬렉션이 초기화되지 않았습니다.")

        # --- Process ---
        doc_count = self.collection.count()
        if doc_count == 0:
            print("  [경고] ChromaDB 컬렉션이 비어있습니다. BM25 인덱스를 생성할 수 없습니다.")
            return

        all_docs = self.collection.get(
            include=["documents", "metadatas"],
            limit=doc_count,
        )

        documents = all_docs.get("documents", [])
        metadatas = all_docs.get("metadatas", [])
        ids = all_docs.get("ids", [])

        self.bm25_corpus = []
        tokenized_corpus: list[list[str]] = []

        for doc_text, meta, doc_id in zip(documents, metadatas, ids):
            self.bm25_corpus.append({
                "id": doc_id,
                "content": doc_text,
                "source": meta.get("source", ""),
                "metadata": meta,
            })
            # 한국어 포함 간단 공백 토크나이징
            tokens = doc_text.lower().split()
            tokenized_corpus.append(tokens)

        self.bm25_index = BM25Okapi(tokenized_corpus)
        print(f"  BM25 인덱스 구축 완료: {len(self.bm25_corpus)}개 문서")

        # --- Output ---
        # self.bm25_index 빌드 완료

    def _bm25_search(self, query: str, top_k: int) -> list[dict]:
        """BM25 알고리즘으로 키워드 검색을 수행합니다.

        Args:
            query: 검색 질문 문자열
            top_k: 반환할 상위 문서 수

        Returns:
            BM25 점수 순으로 정렬된 문서 리스트. 각 항목:
            - content (str): 문서 텍스트
            - source (str): 출처 파일명
            - bm25_score (float): BM25 점수
            - bm25_rank (int): BM25 순위 (1부터 시작)
        """

        # --- Input ---
        if not self.bm25_index or not self.bm25_corpus:
            return []

        # --- Process ---
        query_tokens = query.lower().split()
        scores = self.bm25_index.get_scores(query_tokens)

        # 점수 순 인덱스 정렬
        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        top_indices = ranked_indices[:top_k]

        results: list[dict] = []
        for rank, idx in enumerate(top_indices, start=1):
            if idx < len(self.bm25_corpus):
                doc = self.bm25_corpus[idx].copy()
                doc["bm25_score"] = float(scores[idx])
                doc["bm25_rank"] = rank
                results.append(doc)

        # --- Output ---
        return results

    def _vector_search(self, query: str, top_k: int) -> list[dict]:
        """ChromaDB 벡터 검색을 수행합니다.

        Args:
            query: 검색 질문 문자열
            top_k: 반환할 상위 문서 수

        Returns:
            코사인 유사도 순으로 정렬된 문서 리스트. 각 항목:
            - content (str): 문서 텍스트
            - source (str): 출처 파일명
            - vector_score (float): 코사인 유사도 점수 (높을수록 유사)
            - vector_rank (int): 벡터 검색 순위 (1부터 시작)
        """

        # --- Input ---
        if not self.collection:
            return []

        # --- Process ---
        try:
            doc_count = self.collection.count()
            n_results = min(top_k, max(1, doc_count))
            query_result = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as e:
            print(f"  [경고] 벡터 검색 오류: {e}")
            return []

        documents = query_result.get("documents", [[]])[0]
        metadatas = query_result.get("metadatas", [[]])[0]
        distances = query_result.get("distances", [[]])[0]

        results: list[dict] = []
        for rank, (doc_text, meta, distance) in enumerate(
            zip(documents, metadatas, distances), start=1
        ):
            # 코사인 거리를 유사도 점수로 변환 (1 - distance)
            vector_score = 1.0 - float(distance)
            results.append({
                "content": doc_text,
                "source": os.path.basename(meta.get("source", "")),
                "metadata": meta,
                "vector_score": round(vector_score, 4),
                "vector_rank": rank,
            })

        # --- Output ---
        return results

    def _reciprocal_rank_fusion(
        self,
        bm25_results: list[dict],
        vector_results: list[dict],
        k_constant: int = 60,
    ) -> list[dict]:
        """BM25와 벡터 검색 결과를 RRF 알고리즘으로 통합합니다.

        RRF(Reciprocal Rank Fusion) 공식:
        RRF(d) = sum(1 / (k + rank(d)))
        k_constant=60은 RRF 논문 권장 기본값입니다.

        Args:
            bm25_results: BM25 검색 결과 리스트 (bm25_rank 포함)
            vector_results: 벡터 검색 결과 리스트 (vector_rank 포함)
            k_constant: RRF 상수 (기본값: 60)

        Returns:
            RRF 점수 기준으로 통합 정렬된 문서 리스트. 각 항목에 rrf_score 포함.
        """

        # --- Input ---
        rrf_scores: dict[str, float] = {}
        doc_index: dict[str, dict] = {}

        # --- Process ---
        # BM25 결과로 RRF 점수 계산
        for doc in bm25_results:
            source = doc.get("source", doc.get("id", ""))
            rank = doc.get("bm25_rank", 1)
            rrf_score = 1.0 / (k_constant + rank)
            rrf_scores[source] = rrf_scores.get(source, 0.0) + rrf_score
            if source not in doc_index:
                doc_index[source] = doc.copy()

        # 벡터 검색 결과로 RRF 점수 누적
        for doc in vector_results:
            source = doc.get("source", "")
            rank = doc.get("vector_rank", 1)
            rrf_score = 1.0 / (k_constant + rank)
            rrf_scores[source] = rrf_scores.get(source, 0.0) + rrf_score
            if source not in doc_index:
                doc_index[source] = doc.copy()

        # RRF 점수 순으로 정렬
        sorted_sources = sorted(rrf_scores.keys(), key=lambda s: rrf_scores[s], reverse=True)

        fused_results: list[dict] = []
        for final_rank, source in enumerate(sorted_sources, start=1):
            doc = doc_index[source].copy()
            doc["rrf_score"] = round(rrf_scores[source], 6)
            doc["final_rank"] = final_rank
            fused_results.append(doc)

        # --- Output ---
        return fused_results

    def search(self, query: str, top_k: int = 5, alpha: float = 0.5) -> list[dict]:
        """하이브리드 검색을 수행합니다.

        BM25와 벡터 검색을 각각 실행한 후 RRF로 결합합니다.
        alpha 값은 두 검색의 가중치를 결정하지만, 현재 구현에서는
        RRF 방식으로 통합하므로 alpha는 로깅 목적으로 사용됩니다.

        Args:
            query: 검색 질문 문자열
            top_k: 반환할 최종 상위 문서 수 (기본값: 5)
            alpha: 벡터 검색 가중치 (0.0=BM25 전용, 1.0=벡터 전용, 0.5=균등)
                   현재 RRF 방식에서는 로깅 목적으로만 사용됩니다.

        Returns:
            RRF 점수 기준으로 정렬된 문서 리스트. 각 항목:
            - content (str): 문서 텍스트
            - source (str): 출처 파일명
            - rrf_score (float): RRF 통합 점수
            - final_rank (int): 최종 순위
        """

        # --- Input ---
        if not query or not query.strip():
            return []

        print(f"  [하이브리드 검색] 질문: {query[:50]}... (alpha={alpha})")

        # --- Process ---
        if self.is_mock_mode:
            # Mock 모드: 샘플 결과 반환
            mock_results = []
            mock_docs = [
                {"content": f"연차 신청은 사용 예정일 7일 전에 신청해야 합니다.", "source": "leave_rules.txt"},
                {"content": f"비밀번호는 90일마다 변경해야 합니다.", "source": "it_guide.txt"},
                {"content": f"급여는 매월 25일에 지급됩니다.", "source": "hr_policy.txt"},
            ]
            for i, doc in enumerate(mock_docs[:top_k], start=1):
                doc_copy = doc.copy()
                doc_copy["rrf_score"] = round(1.0 / (60 + i), 6)
                doc_copy["final_rank"] = i
                mock_results.append(doc_copy)
            print(f"  [Mock] {len(mock_results)}개 문서 반환")
            return mock_results

        # BM25 검색
        bm25_results = self._bm25_search(query=query, top_k=top_k * 2)
        print(f"  BM25 결과: {len(bm25_results)}개")

        # 벡터 검색
        vector_results = self._vector_search(query=query, top_k=top_k * 2)
        print(f"  벡터 검색 결과: {len(vector_results)}개")

        # RRF로 결합
        fused_results = self._reciprocal_rank_fusion(
            bm25_results=bm25_results,
            vector_results=vector_results,
        )

        final_results = fused_results[:top_k]
        print(f"  RRF 통합 후 최종: {len(final_results)}개")

        # --- Output ---
        return final_results

    def compare_search_methods(self, query: str, top_k: int = 3) -> dict:
        """BM25, 벡터, 하이브리드 세 가지 검색 방법을 비교합니다.

        Args:
            query: 검색 질문 문자열
            top_k: 각 방법별 반환할 상위 문서 수 (기본값: 3)

        Returns:
            비교 결과 딕셔너리:
            - bm25 (list[dict]): BM25 검색 결과
            - vector (list[dict]): 벡터 검색 결과
            - hybrid (list[dict]): 하이브리드(RRF) 검색 결과
        """

        # --- Input ---
        print(f"\n  [검색 방법 비교] 질문: {query[:50]}...")

        # --- Process ---
        if self.is_mock_mode:
            mock_doc = {"content": "Mock 문서 내용입니다.", "source": "mock.txt"}
            return {
                "bm25": [dict(mock_doc, bm25_rank=i + 1) for i in range(top_k)],
                "vector": [dict(mock_doc, vector_rank=i + 1) for i in range(top_k)],
                "hybrid": [dict(mock_doc, rrf_score=0.016, final_rank=i + 1) for i in range(top_k)],
            }

        bm25_results = self._bm25_search(query=query, top_k=top_k)
        vector_results = self._vector_search(query=query, top_k=top_k)
        hybrid_results = self.search(query=query, top_k=top_k)

        # --- Output ---
        return {
            "bm25": bm25_results,
            "vector": vector_results,
            "hybrid": hybrid_results,
        }
