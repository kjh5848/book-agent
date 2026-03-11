"""하이브리드 검색 모듈.

BM25(키워드 검색)와 Vector Search(의미 검색)를 결합하는
EnsembleRetriever를 구현합니다.
alpha 파라미터로 두 검색 방식의 가중치를 조정합니다.
ChromaDB 없이 인메모리 샘플 데이터로 실행 가능합니다.
"""

import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()

console = Console()

# --- 상수 정의 ---
BASE_DIR = Path(__file__).resolve().parent.parent
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "jhgan/ko-sroberta-multitask")
USE_SAMPLE_DATA = os.getenv("USE_SAMPLE_DATA", "true").lower() == "true"

# 인메모리 샘플 문서
SAMPLE_DOCUMENTS = [
    "연차유급휴가는 1년 이상 근속한 직원에게 15일이 부여됩니다. 3년 이상 근속 시 매 2년마다 1일씩 추가됩니다.",
    "연차 신청은 사용 예정일 3일 전까지 인사담당자에게 서면으로 제출하고 팀장 승인을 받아야 합니다.",
    "재택근무는 입사 6개월 이상 정규직 직원에 한해 주 2회까지 신청 가능합니다. 팀장 사전 승인이 필요합니다.",
    "출장비는 출장 완료 후 5영업일 이내에 영수증과 함께 경비 정산 시스템에 제출해야 합니다.",
    "성과 평가는 상반기와 하반기에 각 1회 실시하며, 목표달성도 60%, 역량평가 30%, 동료평가 10%입니다.",
    "자기계발비는 연간 50만원 한도로 직무 관련 도서, 온라인 강의, 자격증 취득 비용을 지원합니다.",
    "개인 USB 사용은 원칙적으로 금지되며, IT보안팀 승인 장치만 사용 가능합니다.",
    "신입사원 온보딩은 1주차 오리엔테이션, 2-4주차 부서 적응, 2-3개월차 업무 통합 3단계로 진행됩니다.",
    "퇴직금은 근속 1년 이상 시 계속근로기간 1년에 대해 30일분 평균임금으로 산정하여 지급합니다.",
    "육아휴직은 만 8세 이하 자녀를 둔 직원이 신청할 수 있으며 최대 1년 사용이 가능합니다.",
    "고충처리는 1차 팀장 처리 후 미해결 시 인사팀 고충처리위원회에 서면 신청하며 15일 내 결과를 통보받습니다.",
    "건강검진은 연 1회 전액 회사 부담으로 실시하며, 검진 당일은 유급 처리됩니다.",
]

SAMPLE_METADATAS = [
    {"source": "HR_취업규칙_v1.0.pdf", "section": "3.1"},
    {"source": "HR_취업규칙_v1.0.pdf", "section": "3.2"},
    {"source": "HR_근무규정_v2.1.pdf", "section": "4.1"},
    {"source": "재무_출장규정_v2.0.pdf", "section": "3"},
    {"source": "HR_성과평가지침_v2.0.pdf", "section": "2.1"},
    {"source": "HR_복리후생규정_v3.0.pdf", "section": "6.2"},
    {"source": "IT_보안정책_v3.0.pdf", "section": "5.3"},
    {"source": "HR_온보딩가이드_v1.5.pdf", "section": "2"},
    {"source": "HR_취업규칙_v1.0.pdf", "section": "12"},
    {"source": "HR_복리후생규정_v3.0.pdf", "section": "7"},
    {"source": "HR_취업규칙_v1.0.pdf", "section": "9"},
    {"source": "HR_복리후생규정_v3.0.pdf", "section": "8"},
]


# ============================================================
# INPUT: 검색기 생성
# ============================================================

class BM25Retriever:
    """BM25 키워드 기반 검색기.

    rank-bm25 라이브러리를 사용하여 키워드 기반 검색을 수행합니다.

    Attributes:
        documents: 원본 문서 리스트
        metadatas: 문서 메타데이터 리스트
        bm25: BM25 인덱스
    """

    def __init__(
        self,
        documents: list[str],
        metadatas: list[dict] = None
    ):
        """BM25 인덱스를 생성합니다.

        Args:
            documents: 문서 텍스트 리스트
            metadatas: 문서 메타데이터 리스트
        """
        self.documents = documents
        self.metadatas = metadatas or [{} for _ in documents]
        self.bm25 = self._build_index(documents)

    def _build_index(self, documents: list[str]) -> object:
        """BM25 인덱스를 빌드합니다.

        Args:
            documents: 문서 리스트

        Returns:
            BM25Okapi 인스턴스
        """
        try:
            from rank_bm25 import BM25Okapi

            # 한국어 공백 기반 토크나이징
            tokenized_docs = [doc.lower().split() for doc in documents]
            return BM25Okapi(tokenized_docs)

        except ImportError:
            console.print(
                "[red]rank-bm25 패키지가 설치되지 않았습니다.[/red]"
            )
            console.print("pip install rank-bm25 를 실행하십시오.")
            sys.exit(1)

    def search(
        self,
        query: str,
        top_k: int = 5
    ) -> list[dict]:
        """BM25로 문서를 검색합니다.

        Args:
            query: 검색 쿼리
            top_k: 반환할 상위 문서 수

        Returns:
            검색 결과 리스트 (content, score, metadata 포함)
        """
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)

        # 점수와 인덱스를 함께 정렬
        scored_indices = sorted(
            enumerate(scores),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]

        results = []
        for idx, score in scored_indices:
            results.append({
                "content": self.documents[idx],
                "score": float(score),
                "metadata": self.metadatas[idx],
                "retriever_type": "bm25"
            })

        return results


class VectorRetriever:
    """벡터 기반 시맨틱 검색기.

    sentence-transformers를 사용하여 의미 기반 검색을 수행합니다.
    ChromaDB 없이 numpy 기반 인메모리 검색을 지원합니다.

    Attributes:
        documents: 원본 문서 리스트
        metadatas: 문서 메타데이터 리스트
        embeddings: 사전 계산된 문서 임베딩
        model: 임베딩 모델
    """

    def __init__(
        self,
        documents: list[str],
        metadatas: list[dict] = None,
        model_name: str = EMBEDDING_MODEL
    ):
        """임베딩 모델과 문서 인덱스를 초기화합니다.

        Args:
            documents: 문서 텍스트 리스트
            metadatas: 문서 메타데이터 리스트
            model_name: 임베딩 모델 이름
        """
        self.documents = documents
        self.metadatas = metadatas or [{} for _ in documents]
        self.model = self._load_model(model_name)
        self.embeddings = self._embed_documents(documents)

    def _load_model(self, model_name: str) -> object:
        """임베딩 모델을 로드합니다.

        Args:
            model_name: 모델 이름

        Returns:
            SentenceTransformer 인스턴스
        """
        try:
            from sentence_transformers import SentenceTransformer

            console.print(f"[dim]임베딩 모델 로드 중: {model_name}[/dim]")
            model = SentenceTransformer(model_name)
            console.print("[green]임베딩 모델 로드 완료[/green]")
            return model

        except ImportError:
            console.print(
                "[red]sentence-transformers 패키지가 설치되지 않았습니다.[/red]"
            )
            console.print("pip install sentence-transformers 를 실행하십시오.")
            sys.exit(1)

    def _embed_documents(self, documents: list[str]) -> "numpy.ndarray":
        """문서 임베딩을 사전 계산합니다.

        Args:
            documents: 문서 리스트

        Returns:
            문서 임베딩 배열
        """
        import numpy as np

        console.print("[dim]문서 임베딩 생성 중...[/dim]")
        embeddings = self.model.encode(documents, convert_to_numpy=True)
        console.print(f"[green]임베딩 생성 완료:[/green] {len(documents)}개 문서")
        return embeddings

    def search(
        self,
        query: str,
        top_k: int = 5
    ) -> list[dict]:
        """코사인 유사도 기반 검색을 수행합니다.

        Args:
            query: 검색 쿼리
            top_k: 반환할 상위 문서 수

        Returns:
            검색 결과 리스트 (content, score, metadata 포함)
        """
        import numpy as np

        query_embedding = self.model.encode([query], convert_to_numpy=True)[0]

        # 코사인 유사도 계산
        norms = np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        norms = np.where(norms == 0, 1e-9, norms)
        similarities = np.dot(self.embeddings, query_embedding) / norms

        # 상위 k개 추출
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            results.append({
                "content": self.documents[idx],
                "score": float(similarities[idx]),
                "metadata": self.metadatas[idx],
                "retriever_type": "vector"
            })

        return results


# ============================================================
# PROCESS: EnsembleRetriever (하이브리드 검색)
# ============================================================

class EnsembleRetriever:
    """BM25 + Vector 검색 결합 앙상블 검색기.

    두 검색 방식의 점수를 정규화한 후 alpha 가중치로 결합합니다.
    alpha=1.0이면 Vector만, alpha=0.0이면 BM25만 사용합니다.

    Attributes:
        bm25_retriever: BM25 검색기
        vector_retriever: Vector 검색기
        alpha: BM25 가중치 (0.0 ~ 1.0)
    """

    def __init__(
        self,
        bm25_retriever: BM25Retriever,
        vector_retriever: VectorRetriever,
        alpha: float = 0.5
    ):
        """앙상블 검색기를 초기화합니다.

        Args:
            bm25_retriever: BM25 검색기 인스턴스
            vector_retriever: Vector 검색기 인스턴스
            alpha: Vector 검색 가중치 (0.0=BM25만, 1.0=Vector만, 0.5=균등)
        """
        self.bm25_retriever = bm25_retriever
        self.vector_retriever = vector_retriever
        self.alpha = alpha

    def _normalize_scores(self, results: list[dict]) -> list[dict]:
        """검색 점수를 0~1 범위로 정규화합니다.

        Args:
            results: 검색 결과 리스트 (score 포함)

        Returns:
            정규화된 결과 리스트
        """
        if not results:
            return results

        scores = [r["score"] for r in results]
        min_score = min(scores)
        max_score = max(scores)
        score_range = max_score - min_score

        for r in results:
            if score_range > 0:
                r["normalized_score"] = (r["score"] - min_score) / score_range
            else:
                r["normalized_score"] = 1.0

        return results

    def search(
        self,
        query: str,
        top_k: int = 5,
        fetch_k: int = 10
    ) -> list[dict]:
        """하이브리드 검색을 수행합니다.

        BM25와 Vector 검색 결과를 결합하여 최종 순위를 계산합니다.

        Args:
            query: 검색 쿼리
            top_k: 최종 반환할 문서 수
            fetch_k: 각 검색기에서 가져올 후보 문서 수

        Returns:
            결합된 검색 결과 리스트 (hybrid_score 포함)
        """
        # 각 검색기에서 결과 가져오기
        bm25_results = self.bm25_retriever.search(query, top_k=fetch_k)
        vector_results = self.vector_retriever.search(query, top_k=fetch_k)

        # 점수 정규화
        bm25_results = self._normalize_scores(bm25_results)
        vector_results = self._normalize_scores(vector_results)

        # 문서별 점수 통합
        doc_scores: dict[str, dict] = {}

        for result in bm25_results:
            key = result["content"]
            doc_scores[key] = {
                "content": result["content"],
                "metadata": result["metadata"],
                "bm25_score": result["normalized_score"],
                "vector_score": 0.0
            }

        for result in vector_results:
            key = result["content"]
            if key in doc_scores:
                doc_scores[key]["vector_score"] = result["normalized_score"]
            else:
                doc_scores[key] = {
                    "content": result["content"],
                    "metadata": result["metadata"],
                    "bm25_score": 0.0,
                    "vector_score": result["normalized_score"]
                }

        # 하이브리드 점수 계산 (alpha: vector 가중치)
        final_results = []
        for doc_data in doc_scores.values():
            hybrid_score = (
                self.alpha * doc_data["vector_score"]
                + (1 - self.alpha) * doc_data["bm25_score"]
            )
            doc_data["hybrid_score"] = hybrid_score
            doc_data["retriever_type"] = "hybrid"
            final_results.append(doc_data)

        # 최종 정렬 및 반환
        final_results.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return final_results[:top_k]


# ============================================================
# OUTPUT: alpha 실험 결과 출력
# ============================================================

def run_alpha_experiment(
    bm25: BM25Retriever,
    vector: VectorRetriever,
    test_queries: list[str]
) -> list[dict]:
    """alpha 파라미터 실험 (0.0 ~ 1.0)을 실행합니다.

    Args:
        bm25: BM25 검색기
        vector: Vector 검색기
        test_queries: 테스트 쿼리 리스트

    Returns:
        alpha별 실험 결과 리스트
    """
    results = []
    alphas = [0.0, 0.3, 0.5, 0.7, 1.0]

    for alpha in alphas:
        ensemble = EnsembleRetriever(bm25, vector, alpha=alpha)

        total_results = 0
        for query in test_queries:
            docs = ensemble.search(query, top_k=5)
            total_results += len(docs)

        avg_results = total_results / len(test_queries)

        label = "BM25만" if alpha == 0.0 else ("Vector만" if alpha == 1.0 else "혼합")
        results.append({
            "alpha": f"{alpha:.1f}",
            "구성": label,
            "BM25 가중치": f"{(1-alpha)*100:.0f}%",
            "Vector 가중치": f"{alpha*100:.0f}%",
            "평균 반환 수": f"{avg_results:.1f}",
            "추천": "단어 정확히 일치" if alpha == 0.0 else ("의미 유사도" if alpha == 1.0 else "균형 검색")
        })

    return results


def print_hybrid_demo(
    ensemble: EnsembleRetriever,
    query: str
) -> None:
    """하이브리드 검색 데모 결과를 출력합니다.

    Args:
        ensemble: 앙상블 검색기
        query: 데모 쿼리
    """
    results = ensemble.search(query, top_k=5)

    table = Table(title=f"하이브리드 검색 결과 (alpha={ensemble.alpha})")
    table.add_column("순위", style="cyan", justify="center")
    table.add_column("BM25 점수", style="yellow")
    table.add_column("Vector 점수", style="blue")
    table.add_column("Hybrid 점수", style="green")
    table.add_column("내용 미리보기", style="white")

    for rank, doc in enumerate(results, 1):
        table.add_row(
            str(rank),
            f"{doc.get('bm25_score', 0):.3f}",
            f"{doc.get('vector_score', 0):.3f}",
            f"{doc.get('hybrid_score', 0):.3f}",
            doc["content"][:50] + "..."
        )

    console.print(table)


def run_hybrid_search_experiment() -> None:
    """하이브리드 검색 전체 실험을 실행합니다."""
    console.rule("[bold blue]CH10 하이브리드 검색 실험[/bold blue]")

    # --- INPUT: 검색기 생성 ---
    console.print("[cyan]BM25 검색기 초기화 중...[/cyan]")
    bm25_retriever = BM25Retriever(SAMPLE_DOCUMENTS, SAMPLE_METADATAS)
    console.print("[green]BM25 검색기 준비 완료[/green]")

    console.print("[cyan]Vector 검색기 초기화 중...[/cyan]")
    vector_retriever = VectorRetriever(SAMPLE_DOCUMENTS, SAMPLE_METADATAS)

    # --- PROCESS: alpha 실험 ---
    console.print("\n[bold yellow]1. alpha 파라미터 실험 (BM25:Vector 가중치 비율)[/bold yellow]")
    test_queries = [
        "연차 신청 절차",
        "재택근무 조건",
        "출장비 정산 방법"
    ]

    alpha_results = run_alpha_experiment(bm25_retriever, vector_retriever, test_queries)

    table = Table(title="alpha 파라미터별 비교")
    for col in alpha_results[0].keys():
        table.add_column(col, style="cyan")
    for row in alpha_results:
        table.add_row(*[str(v) for v in row.values()])
    console.print(table)

    # --- PROCESS: 데모 실험 (alpha=0.5) ---
    console.print("\n[bold yellow]2. 하이브리드 검색 데모 (alpha=0.5)[/bold yellow]")
    demo_query = "연차 신청 절차와 승인 방법"
    console.print(f"  쿼리: '{demo_query}'")

    ensemble = EnsembleRetriever(bm25_retriever, vector_retriever, alpha=0.5)
    print_hybrid_demo(ensemble, demo_query)

    # --- OUTPUT: 권장 설정 ---
    console.rule("[bold green]실험 완료[/bold green]")
    console.print(
        "\n[bold]하이브리드 검색 권장 설정:[/bold]\n"
        "  - 일반 질문 (의미 검색 중심): alpha=0.7\n"
        "  - 정확한 키워드 검색: alpha=0.3\n"
        "  - 균형 잡힌 기본값: alpha=0.5\n"
        "  - 한국어 특수용어/약어: alpha=0.3 (BM25 비중 높임)"
    )


if __name__ == "__main__":
    run_hybrid_search_experiment()
