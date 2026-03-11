"""Retriever 튜닝 실험 모듈.

k값(3/5/10), similarity threshold, metadata filtering 조건에 따른
검색 성능 차이를 실험하고 최적 설정을 찾습니다.
ChromaDB 없이 인메모리 샘플 데이터로 실행 가능합니다.
"""

import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()

console = Console()

# --- 상수 정의 ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "jhgan/ko-sroberta-multitask")
USE_SAMPLE_DATA = os.getenv("USE_SAMPLE_DATA", "true").lower() == "true"
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(BASE_DIR / "data" / "chroma_db"))

# 인메모리 샘플 문서 (ChromaDB 없이 실험용)
SAMPLE_DOCUMENTS = [
    {
        "id": "doc_001",
        "content": "연차유급휴가는 1년 이상 근속한 직원에게 15일이 부여됩니다. 3년 이상 근속 시 2년마다 1일씩 추가됩니다.",
        "metadata": {
            "department": "HR",
            "version": "v1.0",
            "doc_type": "policy",
            "source": "HR_취업규칙_v1.0.pdf"
        }
    },
    {
        "id": "doc_002",
        "content": "연차 신청은 사용 예정일 3일 전까지 인사담당자에게 서면으로 신청해야 합니다. 팀장 승인이 필요합니다.",
        "metadata": {
            "department": "HR",
            "version": "v1.0",
            "doc_type": "procedure",
            "source": "HR_취업규칙_v1.0.pdf"
        }
    },
    {
        "id": "doc_003",
        "content": "재택근무는 입사 6개월 이상 정규직 직원에 한해 신청 가능합니다. 주 2회까지 허용됩니다.",
        "metadata": {
            "department": "HR",
            "version": "v2.1",
            "doc_type": "policy",
            "source": "HR_근무규정_v2.1.pdf"
        }
    },
    {
        "id": "doc_004",
        "content": "출장비는 출장 완료 후 5영업일 이내에 영수증과 함께 정산 신청해야 합니다. 숙박비 15만원, 식비 5만원 한도.",
        "metadata": {
            "department": "FINANCE",
            "version": "v2.0",
            "doc_type": "regulation",
            "source": "재무_출장규정_v2.0.pdf"
        }
    },
    {
        "id": "doc_005",
        "content": "성과 평가는 상반기(7월)와 하반기(1월)에 연 2회 실시합니다. 목표달성도 60%, 역량평가 30%, 동료평가 10%.",
        "metadata": {
            "department": "HR",
            "version": "v2.0",
            "doc_type": "policy",
            "source": "HR_성과평가지침_v2.0.pdf"
        }
    },
    {
        "id": "doc_006",
        "content": "자기계발비는 연간 50만원 한도로 지원됩니다. 직무 관련 도서, 온라인 강의, 자격증 취득 비용이 포함됩니다.",
        "metadata": {
            "department": "HR",
            "version": "v3.0",
            "doc_type": "benefit",
            "source": "HR_복리후생규정_v3.0.pdf"
        }
    },
    {
        "id": "doc_007",
        "content": "개인 USB 사용은 원칙적으로 금지됩니다. IT보안팀에서 승인한 암호화 USB만 사용 가능합니다.",
        "metadata": {
            "department": "IT",
            "version": "v3.0",
            "doc_type": "security",
            "source": "IT_보안정책_v3.0.pdf"
        }
    },
    {
        "id": "doc_008",
        "content": "신입사원 온보딩은 1주차 오리엔테이션, 2-4주차 부서 적응, 2-3개월차 업무 통합의 3단계로 진행됩니다.",
        "metadata": {
            "department": "HR",
            "version": "v1.5",
            "doc_type": "guide",
            "source": "HR_온보딩가이드_v1.5.pdf"
        }
    },
    {
        "id": "doc_009",
        "content": "퇴직금은 근속 1년 이상 시 지급되며, 계속근로기간 1년에 대해 30일분 평균임금으로 산정합니다.",
        "metadata": {
            "department": "HR",
            "version": "v1.0",
            "doc_type": "policy",
            "source": "HR_취업규칙_v1.0.pdf"
        }
    },
    {
        "id": "doc_010",
        "content": "육아휴직은 만 8세 이하 자녀를 둔 직원이 신청 가능하며, 최대 1년 사용 가능합니다.",
        "metadata": {
            "department": "HR",
            "version": "v3.0",
            "doc_type": "benefit",
            "source": "HR_복리후생규정_v3.0.pdf"
        }
    }
]


# ============================================================
# INPUT: ChromaDB 또는 인메모리 샘플 준비
# ============================================================

class InMemoryRetriever:
    """인메모리 샘플 데이터를 사용하는 검색기.

    ChromaDB 없이도 실험 가능한 경량 검색기입니다.
    단순 키워드 매칭 방식으로 유사도를 계산합니다.

    Attributes:
        documents: 샘플 문서 리스트
    """

    def __init__(self, documents: list[dict]):
        """초기화합니다.

        Args:
            documents: 문서 딕셔너리 리스트 (content, metadata 포함)
        """
        self.documents = documents

    def similarity_score(self, query: str, doc_content: str) -> float:
        """쿼리와 문서 간 단순 키워드 유사도를 계산합니다.

        Args:
            query: 검색 쿼리
            doc_content: 문서 내용

        Returns:
            유사도 점수 (0.0 ~ 1.0)
        """
        query_words = set(query.lower().split())
        doc_words = set(doc_content.lower().split())

        if not query_words:
            return 0.0

        intersection = query_words & doc_words
        return len(intersection) / len(query_words)

    def search(
        self,
        query: str,
        k: int = 5,
        threshold: float = 0.0,
        metadata_filter: Optional[dict] = None
    ) -> list[dict]:
        """문서를 검색합니다.

        Args:
            query: 검색 쿼리
            k: 반환할 최대 문서 수
            threshold: 최소 유사도 임계값
            metadata_filter: 메타데이터 필터 (예: {"department": "HR"})

        Returns:
            검색 결과 리스트 (score, content, metadata 포함)
        """
        # 메타데이터 필터링
        candidates = self.documents
        if metadata_filter:
            candidates = [
                doc for doc in candidates
                if all(
                    doc["metadata"].get(k) == v
                    for k, v in metadata_filter.items()
                )
            ]

        # 유사도 계산
        scored_docs = []
        for doc in candidates:
            score = self.similarity_score(query, doc["content"])
            if score >= threshold:
                scored_docs.append({
                    "score": score,
                    "content": doc["content"],
                    "metadata": doc["metadata"],
                    "id": doc["id"]
                })

        # 점수 내림차순 정렬 후 top-k 반환
        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        return scored_docs[:k]


def create_chroma_retriever(k: int = 5) -> Optional[object]:
    """ChromaDB 기반 검색기를 생성합니다.

    CHROMA_PERSIST_DIR에 ChromaDB가 존재하는 경우에만 사용합니다.

    Args:
        k: 반환할 최대 문서 수

    Returns:
        LangChain VectorStoreRetriever 또는 None
    """
    chroma_path = Path(CHROMA_PERSIST_DIR)
    if not chroma_path.exists():
        console.print(
            "[yellow]ChromaDB 경로가 없습니다. 인메모리 샘플 모드를 사용합니다.[/yellow]"
        )
        return None

    try:
        import chromadb
        from langchain_chroma import Chroma
        from langchain_community.embeddings import HuggingFaceEmbeddings

        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"}
        )

        vectorstore = Chroma(
            persist_directory=str(chroma_path),
            embedding_function=embeddings
        )

        return vectorstore.as_retriever(search_kwargs={"k": k})

    except Exception as e:
        console.print(f"[red]ChromaDB 로드 실패: {e}[/red]")
        console.print("[yellow]인메모리 샘플 모드로 전환합니다.[/yellow]")
        return None


# ============================================================
# PROCESS: k값 / threshold / metadata 실험
# ============================================================

def run_k_value_experiment(
    retriever: InMemoryRetriever,
    test_queries: list[str]
) -> list[dict]:
    """k값(3, 5, 10) 실험을 실행합니다.

    Args:
        retriever: 검색기 인스턴스
        test_queries: 테스트 쿼리 리스트

    Returns:
        k값별 실험 결과 리스트
    """
    results = []
    k_values = [3, 5, 10]

    for k in k_values:
        avg_results_count = 0
        avg_top_score = 0.0

        for query in test_queries:
            docs = retriever.search(query, k=k)
            avg_results_count += len(docs)
            if docs:
                avg_top_score += docs[0]["score"]

        avg_results_count /= len(test_queries)
        avg_top_score /= len(test_queries)

        results.append({
            "k값": k,
            "평균 반환 문서 수": f"{avg_results_count:.1f}",
            "평균 최고 점수": f"{avg_top_score:.3f}",
            "추천 상황": _get_k_recommendation(k)
        })

    return results


def _get_k_recommendation(k: int) -> str:
    """k값에 따른 추천 상황을 반환합니다.

    Args:
        k: k값

    Returns:
        추천 상황 설명
    """
    recommendations = {
        3: "정확도 중시, 컨텍스트 창 절약",
        5: "일반적인 RAG 최적값 (권장)",
        10: "높은 재현율 필요, ReRanker와 함께 사용"
    }
    return recommendations.get(k, "")


def run_threshold_experiment(
    retriever: InMemoryRetriever,
    test_queries: list[str]
) -> list[dict]:
    """similarity threshold 실험을 실행합니다.

    Args:
        retriever: 검색기 인스턴스
        test_queries: 테스트 쿼리 리스트

    Returns:
        threshold별 실험 결과 리스트
    """
    results = []
    thresholds = [0.0, 0.1, 0.2, 0.3, 0.5]

    for threshold in thresholds:
        total_returned = 0
        total_filtered = 0

        for query in test_queries:
            docs_no_threshold = retriever.search(query, k=10, threshold=0.0)
            docs_with_threshold = retriever.search(query, k=10, threshold=threshold)
            total_returned += len(docs_with_threshold)
            total_filtered += len(docs_no_threshold) - len(docs_with_threshold)

        avg_returned = total_returned / len(test_queries)
        avg_filtered = total_filtered / len(test_queries)

        results.append({
            "임계값": threshold,
            "평균 반환 수": f"{avg_returned:.1f}",
            "평균 필터링 수": f"{avg_filtered:.1f}",
            "효과": "높을수록 저품질 문서 제거"
        })

    return results


def run_metadata_filter_experiment(
    retriever: InMemoryRetriever,
    query: str
) -> list[dict]:
    """메타데이터 필터링 실험을 실행합니다.

    Args:
        retriever: 검색기 인스턴스
        query: 테스트 쿼리

    Returns:
        필터 조건별 실험 결과 리스트
    """
    results = []

    # 필터 조건 목록
    filter_configs = [
        (None, "필터 없음 (전체)"),
        ({"department": "HR"}, "부서: HR"),
        ({"department": "FINANCE"}, "부서: FINANCE"),
        ({"department": "IT"}, "부서: IT"),
        ({"version": "v1.0"}, "버전: v1.0"),
        ({"doc_type": "policy"}, "문서 유형: 정책"),
        ({"doc_type": "benefit"}, "문서 유형: 복리후생")
    ]

    for metadata_filter, description in filter_configs:
        docs = retriever.search(query, k=5, metadata_filter=metadata_filter)
        sources = [doc["metadata"].get("source", "알 수 없음") for doc in docs]

        results.append({
            "필터 조건": description,
            "반환 문서 수": len(docs),
            "검색된 소스": ", ".join(sources) if sources else "없음"
        })

    return results


# ============================================================
# OUTPUT: 실험 결과 출력
# ============================================================

def print_experiment_table(title: str, results: list[dict]) -> None:
    """실험 결과를 테이블로 출력합니다.

    Args:
        title: 테이블 제목
        results: 결과 딕셔너리 리스트
    """
    if not results:
        return

    table = Table(title=title)
    for col in results[0].keys():
        table.add_column(str(col), style="cyan")

    for row in results:
        table.add_row(*[str(v) for v in row.values()])

    console.print(table)


def run_all_retriever_experiments() -> None:
    """모든 Retriever 튜닝 실험을 실행합니다."""
    console.rule("[bold blue]CH10 Retriever 튜닝 실험[/bold blue]")

    # --- INPUT: 검색기 생성 ---
    if USE_SAMPLE_DATA:
        console.print("[cyan]인메모리 샘플 데이터 모드로 실행합니다.[/cyan]")
        retriever = InMemoryRetriever(SAMPLE_DOCUMENTS)
    else:
        chroma_retriever = create_chroma_retriever()
        if chroma_retriever is None:
            console.print("[yellow]ChromaDB 없이 인메모리 샘플 모드로 전환합니다.[/yellow]")
            retriever = InMemoryRetriever(SAMPLE_DOCUMENTS)
        else:
            retriever = chroma_retriever

    # 테스트 쿼리 정의
    test_queries = [
        "연차 신청 절차",
        "재택근무 조건",
        "출장비 정산",
        "성과 평가 기준",
        "자기계발비 지원"
    ]

    # --- PROCESS: k값 실험 ---
    console.print("\n[bold yellow]1. k값 실험 (k=3, 5, 10)[/bold yellow]")
    k_results = run_k_value_experiment(retriever, test_queries)
    print_experiment_table("k값별 검색 결과 비교", k_results)

    # --- PROCESS: threshold 실험 ---
    console.print("\n[bold yellow]2. Similarity Threshold 실험[/bold yellow]")
    threshold_results = run_threshold_experiment(retriever, test_queries)
    print_experiment_table("Threshold별 검색 결과 비교", threshold_results)

    # --- PROCESS: metadata 필터링 실험 ---
    console.print("\n[bold yellow]3. Metadata Filtering 실험[/bold yellow]")
    filter_query = "복리후생 규정 안내"
    console.print(f"  테스트 쿼리: '{filter_query}'")
    filter_results = run_metadata_filter_experiment(retriever, filter_query)
    print_experiment_table("메타데이터 필터별 검색 결과", filter_results)

    # --- OUTPUT: 권장 설정 ---
    console.rule("[bold green]실험 완료[/bold green]")
    console.print(
        "\n[bold]권장 Retriever 설정:[/bold]\n"
        "  - k=5 (일반적인 RAG 최적값)\n"
        "  - threshold=0.2 (저품질 문서 필터링)\n"
        "  - metadata filtering: 부서별/문서 유형별 필터 적용 권장"
    )


if __name__ == "__main__":
    run_all_retriever_experiments()
