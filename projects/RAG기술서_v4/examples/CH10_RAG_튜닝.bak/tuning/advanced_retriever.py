"""고급 Retriever 모듈.

ParentDocumentRetriever, SelfQueryRetriever, ContextualCompressionRetriever
세 가지 고급 검색 전략을 구현하고 비교합니다.
ChromaDB 없이 인메모리 샘플로 동작하는 폴백 로직을 포함합니다.
"""

import os
import sys
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()

console = Console()

# --- 상수 정의 ---
BASE_DIR = Path(__file__).resolve().parent.parent
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:8b")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "jhgan/ko-sroberta-multitask")

# 샘플 문서 (부모 문서와 자식 청크 구조 시연용)
PARENT_DOCUMENTS = [
    {
        "id": "parent_001",
        "title": "HR 취업규칙 - 휴가 규정",
        "content": """제15조 (연차유급휴가)
사용자는 1년간 80퍼센트 이상 출근한 근로자에게 15일의 유급휴가를 주어야 한다.
사용자는 3년 이상 계속하여 근로한 근로자에게는 제1항에 따른 휴가에 최초 1년을 초과하는
계속 근로 연수 매 2년에 대하여 1일을 가산한 유급휴가를 주어야 한다.
이 경우 가산휴가를 포함한 총 휴가 일수는 25일을 한도로 한다.

제16조 (연차 신청)
연차유급휴가를 사용하고자 할 때에는 사용 예정일 3일 전까지 인사담당자에게 서면으로
신청하여야 한다. 단, 긴급한 경우에는 구두 신청 후 사후 서면 제출이 가능하다.
팀장은 업무 상황을 고려하여 휴가 시기를 조정할 수 있으나, 근로자의 휴가 사용 권리는
침해하여서는 아니 된다.""",
        "metadata": {"source": "HR_취업규칙_v1.0.pdf", "chapter": "15-16", "topic": "휴가"}
    },
    {
        "id": "parent_002",
        "title": "HR 근무규정 - 재택근무",
        "content": """제4조 (재택근무 신청 자격)
재택근무는 입사 후 6개월이 경과한 정규직 직원에 한하여 신청할 수 있다.
재택근무 신청은 팀장의 사전 승인을 받아야 하며, 최대 주 2회까지 허용된다.

제5조 (재택근무 중 의무사항)
재택근무 중에도 정규 근무시간(09:00~18:00)을 준수하여야 하며,
화상회의 등 팀 협업에 성실히 참여하여야 한다.
재택근무 중 업무 연락에는 1시간 이내에 응답하여야 한다.
프로젝트 마감 기간이나 팀장이 필요하다고 판단하는 경우 재택근무가 제한될 수 있다.""",
        "metadata": {"source": "HR_근무규정_v2.1.pdf", "chapter": "4-5", "topic": "재택근무"}
    }
]

CHILD_CHUNKS = [
    # parent_001의 자식 청크
    {"parent_id": "parent_001", "content": "연차유급휴가는 1년간 80% 이상 출근 시 15일이 부여됩니다.", "metadata": {"source": "HR_취업규칙_v1.0.pdf"}},
    {"parent_id": "parent_001", "content": "3년 이상 근속 시 매 2년마다 1일씩 추가되며 최대 25일입니다.", "metadata": {"source": "HR_취업규칙_v1.0.pdf"}},
    {"parent_id": "parent_001", "content": "연차 신청은 3일 전 서면으로 하며 팀장 승인이 필요합니다.", "metadata": {"source": "HR_취업규칙_v1.0.pdf"}},
    # parent_002의 자식 청크
    {"parent_id": "parent_002", "content": "재택근무는 입사 6개월 이상 정규직에 한해 신청 가능합니다.", "metadata": {"source": "HR_근무규정_v2.1.pdf"}},
    {"parent_id": "parent_002", "content": "재택근무는 팀장 사전 승인 후 주 2회까지 허용됩니다.", "metadata": {"source": "HR_근무규정_v2.1.pdf"}},
    {"parent_id": "parent_002", "content": "재택근무 중에는 정규 근무시간 준수 및 1시간 내 응답 의무가 있습니다.", "metadata": {"source": "HR_근무규정_v2.1.pdf"}},
]


# ============================================================
# INPUT: LLM 및 임베딩 모델 로드
# ============================================================

def load_llm() -> object:
    """설정된 LLM Provider에 따라 LLM을 로드합니다.

    Returns:
        LangChain LLM 인스턴스

    Raises:
        SystemExit: LLM 로드 실패 시
    """
    if LLM_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            console.print(
                "[red]OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.[/red]"
            )
            console.print(".env 파일에 API 키를 입력하십시오.")
            sys.exit(1)
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                api_key=OPENAI_API_KEY,
                model=OPENAI_MODEL,
                temperature=0
            )
        except ImportError:
            console.print("[red]langchain-openai 패키지를 설치하십시오.[/red]")
            sys.exit(1)

    else:  # ollama (기본)
        try:
            from langchain_ollama import ChatOllama
            return ChatOllama(
                base_url=OLLAMA_BASE_URL,
                model=OLLAMA_MODEL,
                temperature=0
            )
        except ImportError:
            console.print("[red]langchain-ollama 패키지를 설치하십시오.[/red]")
            sys.exit(1)


def load_embeddings() -> object:
    """임베딩 모델을 로드합니다.

    Returns:
        LangChain Embeddings 인스턴스
    """
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings

        console.print(f"[dim]임베딩 모델 로드 중: {EMBEDDING_MODEL}[/dim]")
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"}
        )
        console.print("[green]임베딩 모델 로드 완료[/green]")
        return embeddings

    except ImportError:
        console.print("[red]langchain-community 패키지를 설치하십시오.[/red]")
        sys.exit(1)


# ============================================================
# PROCESS: 고급 Retriever 구현
# ============================================================

class ParentDocumentRetrieverDemo:
    """ParentDocumentRetriever 동작 데모.

    작은 자식 청크로 검색하고, 원본 부모 문서 전체를 컨텍스트로 반환합니다.
    LangChain의 ParentDocumentRetriever를 직접 구현하지 않고
    동작 원리를 시연하는 경량 버전입니다.

    Attributes:
        parent_docs: 부모 문서 리스트
        child_chunks: 자식 청크 리스트
    """

    def __init__(
        self,
        parent_docs: list[dict],
        child_chunks: list[dict]
    ):
        """초기화합니다.

        Args:
            parent_docs: 부모 문서 리스트
            child_chunks: 자식 청크 리스트
        """
        self.parent_docs = {doc["id"]: doc for doc in parent_docs}
        self.child_chunks = child_chunks

    def search(self, query: str, top_k: int = 2) -> list[dict]:
        """자식 청크로 검색하고 부모 문서를 반환합니다.

        Args:
            query: 검색 쿼리
            top_k: 반환할 부모 문서 수

        Returns:
            부모 문서 리스트 (관련 자식 청크 정보 포함)
        """
        # 자식 청크에서 쿼리 키워드 매칭
        query_words = set(query.lower().split())
        scored_chunks = []

        for chunk in self.child_chunks:
            chunk_words = set(chunk["content"].lower().split())
            score = len(query_words & chunk_words) / len(query_words) if query_words else 0
            scored_chunks.append((score, chunk))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)

        # 상위 자식 청크에서 부모 문서 ID 추출 (중복 제거)
        seen_parents = set()
        results = []

        for score, chunk in scored_chunks:
            parent_id = chunk["parent_id"]
            if parent_id not in seen_parents and len(results) < top_k:
                seen_parents.add(parent_id)
                parent_doc = self.parent_docs.get(parent_id)
                if parent_doc:
                    results.append({
                        "parent_content": parent_doc["content"],
                        "child_chunk": chunk["content"],
                        "metadata": parent_doc["metadata"],
                        "score": score,
                        "retriever_type": "parent_document"
                    })

        return results


class SelfQueryRetrieverDemo:
    """SelfQueryRetriever 동작 데모.

    LLM이 자연어 질문에서 메타데이터 필터를 자동으로 추출합니다.
    ChromaDB 없이 인메모리 방식으로 동작을 시연합니다.

    Attributes:
        documents: 문서 리스트 (metadata 포함)
        llm: LLM 인스턴스 (필터 추출용)
    """

    def __init__(self, documents: list[dict], llm: Optional[object] = None):
        """초기화합니다.

        Args:
            documents: 문서 리스트
            llm: LLM 인스턴스 (None이면 규칙 기반 추출 사용)
        """
        self.documents = documents
        self.llm = llm

    def extract_filter_from_query(self, query: str) -> dict:
        """쿼리에서 메타데이터 필터를 추출합니다.

        LLM 없이 키워드 규칙으로 필터를 추출합니다.

        Args:
            query: 자연어 쿼리

        Returns:
            추출된 메타데이터 필터 딕셔너리
        """
        filters = {}

        # 토픽 키워드 매핑
        topic_keywords = {
            "휴가": ["연차", "휴가", "유급"],
            "재택근무": ["재택", "원격", "WFH"],
            "출장": ["출장", "여비", "출장비"],
            "평가": ["성과", "평가", "KPI"],
            "복리후생": ["복지", "복리", "자기계발", "건강검진"]
        }

        query_lower = query.lower()
        for topic, keywords in topic_keywords.items():
            if any(kw in query_lower for kw in keywords):
                filters["topic"] = topic
                break

        return filters

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """메타데이터 자동 필터링으로 검색합니다.

        Args:
            query: 자연어 검색 쿼리
            top_k: 반환할 문서 수

        Returns:
            필터링된 검색 결과 리스트
        """
        # 자동 필터 추출
        filters = self.extract_filter_from_query(query)
        console.print(f"  [dim]자동 추출된 필터: {filters}[/dim]")

        # 필터 적용
        filtered_docs = self.documents
        for key, value in filters.items():
            filtered_docs = [
                doc for doc in filtered_docs
                if doc.get("metadata", {}).get(key) == value
            ]

        # 키워드 기반 점수 계산
        query_words = set(query.lower().split())
        scored_docs = []
        for doc in filtered_docs:
            content_words = set(doc["content"].lower().split())
            score = len(query_words & content_words) / len(query_words) if query_words else 0
            scored_docs.append((score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, doc in scored_docs[:top_k]:
            results.append({
                "content": doc["content"],
                "score": score,
                "metadata": doc.get("metadata", {}),
                "applied_filter": filters,
                "retriever_type": "self_query"
            })

        return results


class ContextualCompressionRetrieverDemo:
    """ContextualCompressionRetriever 동작 데모.

    검색된 문서에서 쿼리와 관련된 부분만 추출하여
    컨텍스트 창을 절약하는 방식을 시연합니다.

    Attributes:
        base_documents: 원본 문서 리스트
    """

    def __init__(self, documents: list[dict]):
        """초기화합니다.

        Args:
            documents: 원본 문서 리스트
        """
        self.documents = documents

    def compress_document(self, query: str, document: str) -> str:
        """문서에서 쿼리 관련 문장만 추출합니다.

        LLM 기반 압축 대신 키워드 매칭으로 관련 문장을 추출합니다.

        Args:
            query: 검색 쿼리
            document: 원본 문서 텍스트

        Returns:
            압축된 관련 문장들
        """
        query_words = set(query.lower().split())
        sentences = [s.strip() for s in document.replace("\n", ". ").split(".") if s.strip()]

        relevant_sentences = []
        for sentence in sentences:
            sentence_words = set(sentence.lower().split())
            overlap = len(query_words & sentence_words)
            if overlap >= 1 and len(sentence) > 10:
                relevant_sentences.append(sentence)

        return ". ".join(relevant_sentences[:3]) if relevant_sentences else document[:100]

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """검색 후 관련 내용만 압축하여 반환합니다.

        Args:
            query: 검색 쿼리
            top_k: 반환할 문서 수

        Returns:
            압축된 검색 결과 리스트
        """
        query_words = set(query.lower().split())

        # 초기 검색
        scored_docs = []
        for doc in self.documents:
            content_words = set(doc["content"].lower().split())
            score = len(query_words & content_words) / len(query_words) if query_words else 0
            scored_docs.append((score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, doc in scored_docs[:top_k]:
            original_content = doc["content"]
            compressed_content = self.compress_document(query, original_content)

            results.append({
                "original_content": original_content,
                "compressed_content": compressed_content,
                "compression_ratio": len(compressed_content) / len(original_content),
                "score": score,
                "metadata": doc.get("metadata", {}),
                "retriever_type": "contextual_compression"
            })

        return results


# ============================================================
# OUTPUT: 고급 Retriever 비교 실험
# ============================================================

def run_advanced_retriever_experiment() -> None:
    """고급 Retriever 세 가지를 비교 실험합니다."""
    console.rule("[bold blue]CH10 고급 Retriever 실험[/bold blue]")

    # 테스트용 문서 세트
    test_documents = [
        {"content": chunk["content"], "metadata": {**chunk["metadata"], "parent_id": chunk["parent_id"]}}
        for chunk in CHILD_CHUNKS
    ]

    test_query = "연차 신청 절차와 팀장 승인 방법"
    console.print(f"\n[bold]테스트 쿼리:[/bold] {test_query}")

    # --- PROCESS 1: ParentDocumentRetriever ---
    console.print("\n[bold yellow]1. ParentDocumentRetriever[/bold yellow]")
    console.print(
        "  [dim]원리: 작은 청크로 검색 → 원본 전체 문서 반환 (컨텍스트 풍부)[/dim]"
    )

    parent_retriever = ParentDocumentRetrieverDemo(PARENT_DOCUMENTS, CHILD_CHUNKS)
    parent_results = parent_retriever.search(test_query, top_k=2)

    for i, result in enumerate(parent_results, 1):
        console.print(f"  결과 {i}:")
        console.print(f"    매칭 청크: '{result['child_chunk']}'")
        console.print(f"    부모 문서 길이: {len(result['parent_content'])}자")
        console.print(f"    소스: {result['metadata'].get('source', '')}")

    # --- PROCESS 2: SelfQueryRetriever ---
    console.print("\n[bold yellow]2. SelfQueryRetriever[/bold yellow]")
    console.print(
        "  [dim]원리: LLM이 질문에서 메타데이터 필터 자동 추출 → 정확한 필터링[/dim]"
    )

    self_query_retriever = SelfQueryRetrieverDemo(test_documents)

    sq_queries = [
        "휴가 관련 규정을 알려주십시오",
        "재택근무 신청 방법은 무엇입니까"
    ]

    for q in sq_queries:
        console.print(f"\n  쿼리: '{q}'")
        sq_results = self_query_retriever.search(q, top_k=2)
        for r in sq_results:
            console.print(
                f"    필터: {r['applied_filter']} | "
                f"내용: {r['content'][:50]}..."
            )

    # --- PROCESS 3: ContextualCompression ---
    console.print("\n[bold yellow]3. ContextualCompressionRetriever[/bold yellow]")
    console.print(
        "  [dim]원리: 검색된 문서에서 쿼리 관련 부분만 추출 → LLM 토큰 절약[/dim]"
    )

    cc_retriever = ContextualCompressionRetrieverDemo(test_documents)
    cc_results = cc_retriever.search(test_query, top_k=3)

    table = Table(title="Contextual Compression 결과")
    table.add_column("순위", justify="center")
    table.add_column("원본 길이", style="yellow")
    table.add_column("압축 길이", style="green")
    table.add_column("압축률", style="cyan")
    table.add_column("압축된 내용", style="white")

    for i, result in enumerate(cc_results, 1):
        table.add_row(
            str(i),
            f"{len(result['original_content'])}자",
            f"{len(result['compressed_content'])}자",
            f"{result['compression_ratio']:.0%}",
            result['compressed_content'][:50] + "..."
        )

    console.print(table)

    # --- OUTPUT: 비교 요약 ---
    console.rule("[bold green]실험 완료[/bold green]")

    summary_table = Table(title="고급 Retriever 비교 요약")
    summary_table.add_column("Retriever", style="cyan")
    summary_table.add_column("핵심 원리", style="white")
    summary_table.add_column("장점", style="green")
    summary_table.add_column("단점", style="red")
    summary_table.add_column("추천 상황", style="yellow")

    summary_table.add_row(
        "ParentDocument",
        "소→대 역매핑",
        "풍부한 컨텍스트",
        "토큰 소모 증가",
        "긴 문서, 문맥 중요"
    )
    summary_table.add_row(
        "SelfQuery",
        "LLM 필터 추출",
        "자동 메타 필터링",
        "LLM 추가 호출",
        "구조화된 메타데이터"
    )
    summary_table.add_row(
        "Contextual Compression",
        "관련 문장만 추출",
        "토큰 절약",
        "정보 손실 위험",
        "긴 문서, 토큰 제한"
    )

    console.print(summary_table)


if __name__ == "__main__":
    run_advanced_retriever_experiment()
