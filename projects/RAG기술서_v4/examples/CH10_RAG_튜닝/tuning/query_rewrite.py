"""Query Rewrite 모듈.

HyDE(Hypothetical Document Embeddings), Multi-Query 생성,
약어/동의어 처리를 통해 질문의 의도를 더 잘 반영하는 검색을 구현합니다.
LLM 없이도 기본 기능을 테스트할 수 있는 폴백 로직을 포함합니다.
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
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:8b")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# 사내 약어/동의어 사전
ABBREVIATION_MAP: dict[str, str] = {
    "연차": "연차유급휴가",
    "WFH": "재택근무",
    "WFH 정책": "재택근무 규정",
    "OT": "초과근무 (잔업)",
    "HR": "인사부서",
    "PIP": "성과개선계획",
    "연봉 협상": "임금 조정 절차",
    "퇴직금": "퇴직급여",
    "4대보험": "국민연금, 건강보험, 고용보험, 산재보험",
    "경조사": "경조금 지원 규정",
    "반차": "반일 연차",
    "반반차": "2시간 단위 연차",
}

SYNONYM_MAP: dict[str, list[str]] = {
    "연차": ["유급휴가", "휴가", "연차유급휴가"],
    "재택근무": ["원격근무", "WFH", "홈오피스"],
    "성과평가": ["인사고과", "평가", "KPI 달성"],
    "출장": ["외근", "출장업무", "여비"],
    "복리후생": ["복지", "혜택", "베네핏"],
    "온보딩": ["신입교육", "입사교육", "오리엔테이션"],
}


# ============================================================
# INPUT: LLM 로드
# ============================================================

def load_llm() -> Optional[object]:
    """설정된 LLM을 로드합니다. 실패 시 None을 반환합니다.

    Returns:
        LLM 인스턴스 또는 None
    """
    try:
        if LLM_PROVIDER == "openai" and OPENAI_API_KEY:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                api_key=OPENAI_API_KEY,
                model=OPENAI_MODEL,
                temperature=0.3
            )

        else:
            from langchain_ollama import ChatOllama
            return ChatOllama(
                base_url=OLLAMA_BASE_URL,
                model=OLLAMA_MODEL,
                temperature=0.3
            )

    except Exception as e:
        console.print(f"[yellow]LLM 로드 실패: {e}[/yellow]")
        console.print("[yellow]LLM 없이 규칙 기반 모드로 실행합니다.[/yellow]")
        return None


# ============================================================
# PROCESS: 약어/동의어 처리
# ============================================================

def expand_abbreviations(query: str) -> str:
    """쿼리의 약어를 풀어서 표현합니다.

    ABBREVIATION_MAP에 등록된 약어를 전체 용어로 대체합니다.

    Args:
        query: 원본 쿼리

    Returns:
        약어가 확장된 쿼리
    """
    expanded = query
    for abbrev, full_form in ABBREVIATION_MAP.items():
        if abbrev in expanded:
            expanded = expanded.replace(abbrev, full_form)
            console.print(f"  [dim]약어 확장: '{abbrev}' → '{full_form}'[/dim]")

    return expanded


def add_synonyms(query: str) -> list[str]:
    """쿼리에 동의어를 추가한 확장 쿼리 목록을 생성합니다.

    Args:
        query: 원본 쿼리

    Returns:
        동의어가 포함된 확장 쿼리 리스트
    """
    queries = [query]

    for term, synonyms in SYNONYM_MAP.items():
        if term in query:
            for synonym in synonyms:
                new_query = query.replace(term, synonym)
                if new_query != query:
                    queries.append(new_query)

    return list(set(queries))


# ============================================================
# PROCESS: HyDE (Hypothetical Document Embeddings)
# ============================================================

def generate_hypothetical_document_llm(
    query: str,
    llm: object
) -> str:
    """LLM으로 가상 답변 문서를 생성합니다.

    HyDE 기법: 실제 문서 대신 가상 문서를 생성하여 검색에 활용합니다.
    실제 답변이 없어도 더 나은 검색 결과를 얻을 수 있습니다.

    Args:
        query: 검색 쿼리
        llm: LLM 인스턴스

    Returns:
        생성된 가상 답변 문서
    """
    try:
        from langchain_core.messages import HumanMessage

        hyde_prompt = f"""다음 질문에 대한 가상의 사내 규정 문서 발췌문을 생성하십시오.
실제 존재하는 문서처럼 구체적인 내용으로 작성하십시오.

질문: {query}

사내 규정 발췌문 (3-5문장):"""

        response = llm.invoke([HumanMessage(content=hyde_prompt)])
        return response.content.strip()

    except Exception as e:
        console.print(f"[yellow]LLM 생성 실패: {e}[/yellow]")
        return generate_hypothetical_document_rule_based(query)


def generate_hypothetical_document_rule_based(query: str) -> str:
    """규칙 기반으로 가상 답변 문서를 생성합니다.

    LLM 없이 키워드 기반으로 간단한 가상 문서를 생성합니다.

    Args:
        query: 검색 쿼리

    Returns:
        규칙 기반 가상 답변 문서
    """
    templates = {
        "연차": "연차유급휴가 규정에 따르면, 직원은 1년 이상 근속 시 15일의 유급휴가를 받습니다. 신청은 3일 전까지 서면으로 하며 팀장 승인이 필요합니다.",
        "재택": "재택근무 정책에 의거하여, 입사 6개월 이상 정규직 직원은 주 2회까지 재택근무를 신청할 수 있습니다. 팀장 사전 승인이 필요하며 정규 근무시간을 준수해야 합니다.",
        "출장": "출장 규정에 따라, 출장비는 완료 후 5영업일 이내에 영수증과 함께 정산 신청해야 합니다. 숙박비 15만원, 식비 5만원이 한도입니다.",
        "평가": "성과 평가 지침에 따르면, 평가는 상하반기 각 1회 실시하며 목표달성도 60%, 역량평가 30%, 동료평가 10%로 구성됩니다.",
    }

    query_lower = query.lower()
    for keyword, template in templates.items():
        if keyword in query_lower:
            return template

    return f"{query}에 관한 사내 규정은 인사팀 담당자에게 문의하거나 사내 규정집을 참조하십시오."


def generate_hypothetical_document(
    query: str,
    llm: Optional[object] = None
) -> str:
    """HyDE 가상 문서를 생성합니다.

    LLM이 있으면 LLM으로, 없으면 규칙 기반으로 생성합니다.

    Args:
        query: 검색 쿼리
        llm: LLM 인스턴스 (None이면 규칙 기반 사용)

    Returns:
        생성된 가상 답변 문서
    """
    if llm is not None:
        return generate_hypothetical_document_llm(query, llm)
    return generate_hypothetical_document_rule_based(query)


# ============================================================
# PROCESS: Multi-Query 생성
# ============================================================

def generate_multi_queries_llm(
    query: str,
    llm: object,
    num_queries: int = 3
) -> list[str]:
    """LLM으로 다양한 관점의 쿼리를 생성합니다.

    하나의 질문을 여러 관점에서 재표현하여 검색 범위를 넓힙니다.

    Args:
        query: 원본 쿼리
        llm: LLM 인스턴스
        num_queries: 생성할 쿼리 수

    Returns:
        생성된 다중 쿼리 리스트
    """
    try:
        from langchain_core.messages import HumanMessage

        prompt = f"""다음 질문을 {num_queries}가지 다른 방식으로 재표현하십시오.
각 질문은 같은 정보를 구하지만 다른 표현 방식을 사용해야 합니다.
번호 없이 각 질문을 한 줄씩 출력하십시오.

원본 질문: {query}

재표현된 질문들:"""

        response = llm.invoke([HumanMessage(content=prompt)])
        lines = [
            line.strip()
            for line in response.content.strip().split("\n")
            if line.strip() and not line.strip().startswith("#")
        ]

        return [query] + lines[:num_queries]

    except Exception as e:
        console.print(f"[yellow]Multi-Query LLM 생성 실패: {e}[/yellow]")
        return generate_multi_queries_rule_based(query)


def generate_multi_queries_rule_based(query: str) -> list[str]:
    """규칙 기반으로 다중 쿼리를 생성합니다.

    LLM 없이 템플릿 방식으로 다양한 표현을 생성합니다.

    Args:
        query: 원본 쿼리

    Returns:
        다중 쿼리 리스트
    """
    templates = [
        query,
        f"{query}에 대한 규정이 있습니까?",
        f"{query} 관련 정책 안내",
        f"{query} 절차 및 방법",
    ]
    return templates[:4]


def generate_multi_queries(
    query: str,
    llm: Optional[object] = None,
    num_queries: int = 3
) -> list[str]:
    """다중 쿼리를 생성합니다.

    LLM이 있으면 LLM으로, 없으면 규칙 기반으로 생성합니다.

    Args:
        query: 원본 쿼리
        llm: LLM 인스턴스 (None이면 규칙 기반 사용)
        num_queries: 생성할 추가 쿼리 수

    Returns:
        다중 쿼리 리스트 (원본 포함)
    """
    if llm is not None:
        return generate_multi_queries_llm(query, llm, num_queries)
    return generate_multi_queries_rule_based(query)


def merge_multi_query_results(
    all_results: list[list[dict]],
    top_k: int = 5
) -> list[dict]:
    """다중 쿼리 결과를 병합하고 중복을 제거합니다.

    Args:
        all_results: 각 쿼리별 검색 결과 리스트
        top_k: 최종 반환할 문서 수

    Returns:
        병합된 검색 결과 리스트
    """
    seen_contents = set()
    merged = []

    for results in all_results:
        for result in results:
            content_key = result.get("content", "")[:50]
            if content_key not in seen_contents:
                seen_contents.add(content_key)
                merged.append(result)

    # 점수 기준 정렬
    merged.sort(key=lambda x: x.get("score", 0), reverse=True)
    return merged[:top_k]


# ============================================================
# OUTPUT: 실험 결과 출력
# ============================================================

def run_query_rewrite_experiment() -> None:
    """Query Rewrite 전체 실험을 실행합니다."""
    console.rule("[bold blue]CH10 Query Rewrite 실험[/bold blue]")

    # LLM 로드 시도
    llm = load_llm()
    if llm is None:
        console.print("[cyan]LLM 없이 규칙 기반 모드로 실행합니다.[/cyan]")
    else:
        console.print("[green]LLM 로드 성공[/green]")

    # 테스트 쿼리
    test_queries = [
        "연차 신청 절차는 어떻게 됩니까?",
        "WFH 정책이 어떻게 됩니까?",
        "4대보험 가입은 언제 됩니까?"
    ]

    # --- PROCESS 1: 약어 확장 ---
    console.print("\n[bold yellow]1. 약어/동의어 확장[/bold yellow]")

    abbrev_table = Table(title="약어 확장 결과")
    abbrev_table.add_column("원본 쿼리", style="yellow")
    abbrev_table.add_column("확장된 쿼리", style="green")
    abbrev_table.add_column("변경 여부", style="cyan")

    for query in test_queries:
        expanded = expand_abbreviations(query)
        changed = "변경됨" if expanded != query else "동일"
        abbrev_table.add_row(query, expanded, changed)

    console.print(abbrev_table)

    # 동의어 확장
    console.print("\n[bold cyan]동의어 확장 예시:[/bold cyan]")
    synonym_query = "연차 사용 규정을 알려주십시오"
    synonym_queries = add_synonyms(synonym_query)
    console.print(f"  원본: '{synonym_query}'")
    for i, q in enumerate(synonym_queries, 1):
        console.print(f"  확장 {i}: '{q}'")

    # --- PROCESS 2: HyDE 가상 문서 생성 ---
    console.print("\n[bold yellow]2. HyDE (Hypothetical Document Embeddings)[/bold yellow]")
    console.print("  [dim]원리: 가상 답변 문서 생성 → 그 문서와 유사한 실제 문서 검색[/dim]")

    hyde_table = Table(title="HyDE 가상 문서 생성")
    hyde_table.add_column("원본 쿼리", style="yellow")
    hyde_table.add_column("생성된 가상 문서", style="green")

    for query in test_queries[:2]:
        console.print(f"\n  쿼리: '{query}'")
        hypothetical_doc = generate_hypothetical_document(query, llm)
        console.print(f"  가상 문서: {hypothetical_doc[:100]}...")
        hyde_table.add_row(query, hypothetical_doc[:80] + "...")

    console.print(hyde_table)

    # --- PROCESS 3: Multi-Query ---
    console.print("\n[bold yellow]3. Multi-Query 생성[/bold yellow]")
    console.print("  [dim]원리: 1개 질문 → N개 다양한 표현으로 검색 결과 다양화[/dim]")

    for query in test_queries[:2]:
        console.print(f"\n  원본 쿼리: '{query}'")
        multi_queries = generate_multi_queries(query, llm, num_queries=3)

        multi_table = Table(title="Multi-Query 결과")
        multi_table.add_column("번호", justify="center", style="cyan")
        multi_table.add_column("생성된 쿼리", style="white")

        for i, mq in enumerate(multi_queries, 1):
            label = "(원본)" if i == 1 else f"(변형 {i-1})"
            multi_table.add_row(str(i), f"{mq} {label}")

        console.print(multi_table)

    # --- OUTPUT: 권장 사항 ---
    console.rule("[bold green]실험 완료[/bold green]")

    rec_table = Table(title="Query Rewrite 기법 비교")
    rec_table.add_column("기법", style="cyan")
    rec_table.add_column("핵심 원리", style="white")
    rec_table.add_column("적용 상황", style="yellow")
    rec_table.add_column("LLM 필요", style="magenta")

    rec_table.add_row(
        "약어/동의어 확장",
        "사전 기반 매핑",
        "전문 용어, 약어 많은 도메인",
        "불필요"
    )
    rec_table.add_row(
        "HyDE",
        "가상 문서 임베딩",
        "답변이 구체적인 사실 문서 검색",
        "필요"
    )
    rec_table.add_row(
        "Multi-Query",
        "다각도 질문 변환",
        "포괄적 정보 수집 필요",
        "필요 (선택)"
    )

    console.print(rec_table)


if __name__ == "__main__":
    run_query_rewrite_experiment()
