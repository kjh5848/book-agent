"""답변 근거 시스템 모듈.

RAG 검색 결과에 원본 문서 캡처 이미지와 DB 데이터를
근거(evidence)로 첨부하여 신뢰도 높은 답변을 제공한다.

IPO 패턴:
  Input  - 사용자 질문
  Process - 벡터검색(비정형) 또는 DB조회(정형) + 근거 수집
  Output - {answer, evidence: [{text, image_path, source}]}

실행 방법:
    python tuning/evidence_pipeline.py
"""

import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

load_dotenv()

console = Console()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CAPTURED_DIR = DATA_DIR / "captured"


# ============================================================
# 1. 근거 포함 검색
# ============================================================

def retrieve_with_evidence(
    query: str,
    query_type: str = "unstructured",
    top_k: int = 3,
) -> dict[str, Any]:
    """질문에 대해 답변 근거를 포함한 검색 결과를 반환한다.

    Args:
        query: 사용자 질문.
        query_type: 질문 유형 (structured/unstructured).
        top_k: 검색할 상위 결과 수.

    Returns:
        근거 포함 응답 딕셔너리.
    """
    if query_type == "structured":
        return _retrieve_structured_evidence(query)
    else:
        return _retrieve_unstructured_evidence(query, top_k)


def _retrieve_unstructured_evidence(
    query: str,
    top_k: int = 3,
) -> dict[str, Any]:
    """비정형 질문에 대해 벡터검색 + 캡처 이미지 근거를 반환한다."""
    try:
        import chromadb
        from chromadb.config import Settings

        client = chromadb.Client(Settings(anonymized_telemetry=False))

        try:
            collection = client.get_collection("document_captures")
        except Exception:
            # 컬렉션이 없으면 샘플 데이터로 대체
            return _get_sample_unstructured_evidence(query)

        results = collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        evidence = []
        for i in range(len(results["ids"][0])):
            doc_text = results["documents"][0][i]
            meta = results["metadatas"][0][i]
            distance = results["distances"][0][i]

            evidence.append({
                "text": doc_text[:300],
                "image_path": meta.get("image_path", ""),
                "source": meta.get("source", "unknown"),
                "page": meta.get("page", ""),
                "relevance": round(1 - distance, 3),
            })

        # 답변 생성 (간단 컨텍스트 조합)
        context = "\n".join(e["text"][:200] for e in evidence)
        answer = f"관련 문서에서 찾은 내용:\n\n{context}" if evidence else "관련 문서를 찾지 못했습니다."

        return {
            "answer": answer,
            "query_type": "unstructured",
            "evidence": evidence,
        }

    except (ImportError, Exception):
        return _get_sample_unstructured_evidence(query)


def _retrieve_structured_evidence(query: str) -> dict[str, Any]:
    """정형 질문에 대해 DB 조회 결과를 근거로 반환한다."""
    # 샘플 데이터 기반 모의 조회
    sample_db_results = {
        "연차": {
            "answer": "김민준의 연차 잔여일수는 12일입니다.",
            "evidence": [{
                "table_data": {
                    "employee": "김민준",
                    "total_days": 15,
                    "used_days": 3,
                    "remaining_days": 12,
                },
                "query": "SELECT remaining_days FROM leaves WHERE employee_name = '김민준'",
                "source": "DB: leaves",
            }],
        },
        "매출": {
            "answer": "영업부 11월 매출 합계는 52,000,000원입니다.",
            "evidence": [{
                "table_data": {
                    "department": "영업부",
                    "month": "2024-11",
                    "total_sales": 52000000,
                },
                "query": "SELECT SUM(amount) FROM sales WHERE dept = '영업부' AND month = '2024-11'",
                "source": "DB: sales",
            }],
        },
    }

    for keyword, result in sample_db_results.items():
        if keyword in query:
            return {
                "answer": result["answer"],
                "query_type": "structured",
                "evidence": result["evidence"],
            }

    return {
        "answer": "해당 데이터를 찾을 수 없습니다.",
        "query_type": "structured",
        "evidence": [],
    }


def _get_sample_unstructured_evidence(query: str) -> dict[str, Any]:
    """ChromaDB가 없을 때 샘플 근거 데이터를 반환한다."""
    # 캡처 이미지 탐색
    captured_images = list(CAPTURED_DIR.rglob("*.png"))

    evidence = []
    sample_docs = [
        {
            "text": "Article 12 (Annual Leave): Employees with 1 year of service receive 15 days of annual leave. Unused leave may be carried over to the next year up to 5 days.",
            "source": "HR_취업규칙_v1.0.pdf",
            "page": "3",
        },
        {
            "text": "Article 13 (Sick Leave): Employees may use up to 30 days of paid sick leave per year. A doctor's certificate is required for sick leave exceeding 3 consecutive days.",
            "source": "HR_취업규칙_v1.0.pdf",
            "page": "3",
        },
        {
            "text": "Total revenue for H1 2025 reached KRW 12.5 billion, representing a 15% increase compared to H1 2024.",
            "source": "sample_sales_report.docx",
            "page": "1",
        },
    ]

    for i, doc in enumerate(sample_docs[:3]):
        img_path = ""
        if i < len(captured_images):
            img_path = str(captured_images[i])

        evidence.append({
            "text": doc["text"],
            "image_path": img_path,
            "source": doc["source"],
            "page": doc["page"],
            "relevance": round(0.95 - i * 0.1, 3),
        })

    context = "\n".join(e["text"][:200] for e in evidence)
    answer = f"관련 문서에서 찾은 내용:\n\n{context}"

    return {
        "answer": answer,
        "query_type": "unstructured",
        "evidence": evidence,
    }


# ============================================================
# 2. 근거 포맷 변환
# ============================================================

def format_evidence_response(result: dict[str, Any]) -> dict[str, Any]:
    """근거 응답을 API 반환 형식으로 변환한다.

    Args:
        result: retrieve_with_evidence 반환값.

    Returns:
        API 응답 형식 딕셔너리.
    """
    formatted_evidence = []

    for ev in result.get("evidence", []):
        if result["query_type"] == "unstructured":
            image_path = ev.get("image_path", "")
            image_url = ""
            if image_path:
                # 상대 경로로 변환 (웹 서빙용)
                try:
                    rel_path = Path(image_path).relative_to(BASE_DIR)
                    image_url = f"/static/{rel_path}"
                except ValueError:
                    image_url = image_path

            formatted_evidence.append({
                "text": ev.get("text", ""),
                "image_url": image_url,
                "source": ev.get("source", ""),
                "page": ev.get("page", ""),
                "relevance": ev.get("relevance", 0),
            })
        else:
            formatted_evidence.append({
                "table_data": ev.get("table_data", {}),
                "query": ev.get("query", ""),
                "source": ev.get("source", ""),
            })

    return {
        "answer": result["answer"],
        "query_type": result["query_type"],
        "evidence": formatted_evidence,
    }


# ============================================================
# 3. 데모 실행
# ============================================================

def run_evidence_demo() -> None:
    """답변 근거 시스템 데모를 실행한다."""
    console.rule("[bold blue]CH10 답변 근거 시스템 데모[/bold blue]")

    # --- 비정형 질문 데모 ---
    console.print("\n[bold cyan]1. 비정형 질문 (문서 검색 + 캡처 이미지)[/bold cyan]")

    unstructured_queries = [
        "연차 사용 규정이 어떻게 되나요?",
        "보안 정책에 대해 설명해줘",
    ]

    for query in unstructured_queries:
        console.print(f"\n  [bold]Q: {query}[/bold]")
        result = retrieve_with_evidence(query, query_type="unstructured")
        formatted = format_evidence_response(result)

        console.print(f"  A: {formatted['answer'][:150]}...")

        if formatted["evidence"]:
            ev_table = Table(title="답변 근거", show_lines=True)
            ev_table.add_column("출처", style="cyan", width=25)
            ev_table.add_column("페이지", style="yellow", width=6)
            ev_table.add_column("텍스트 미리보기", style="white", width=40)
            ev_table.add_column("이미지", style="green", width=20)

            for ev in formatted["evidence"]:
                img_display = Path(ev["image_url"]).name if ev.get("image_url") else "(없음)"
                ev_table.add_row(
                    ev.get("source", ""),
                    str(ev.get("page", "")),
                    ev.get("text", "")[:80] + "...",
                    img_display,
                )
            console.print(ev_table)

    # --- 정형 질문 데모 ---
    console.print("\n[bold cyan]2. 정형 질문 (DB 조회)[/bold cyan]")

    structured_queries = [
        "김민준 연차 잔여일수 알려줘",
        "영업부 11월 매출 합계가 얼마야?",
    ]

    for query in structured_queries:
        console.print(f"\n  [bold]Q: {query}[/bold]")
        result = retrieve_with_evidence(query, query_type="structured")
        formatted = format_evidence_response(result)

        console.print(f"  A: {formatted['answer']}")

        if formatted["evidence"]:
            for ev in formatted["evidence"]:
                console.print(Panel(
                    f"SQL: {ev.get('query', 'N/A')}\n"
                    f"Source: {ev.get('source', 'N/A')}\n"
                    f"Data: {ev.get('table_data', {})}",
                    title="DB 근거",
                    border_style="blue",
                ))

    # --- API 응답 형식 예시 ---
    console.print("\n[bold cyan]3. API 응답 형식 예시[/bold cyan]")

    sample_result = retrieve_with_evidence(
        "연차 규정 알려줘", query_type="unstructured"
    )
    api_response = format_evidence_response(sample_result)

    import json
    console.print(Panel(
        json.dumps(api_response, ensure_ascii=False, indent=2)[:500],
        title="POST /api/chat 응답 예시",
        border_style="green",
    ))

    # --- 요약 ---
    console.rule("[bold green]데모 완료[/bold green]")
    console.print(
        "\n[bold]답변 근거 시스템 흐름:[/bold]\n"
        "  비정형 질문 → 벡터검색 → 관련 텍스트 + 원본 캡처 이미지\n"
        "  정형 질문   → DB 조회  → 구조화 데이터 + SQL 쿼리\n"
        "  웹 UI       → evidence 섹션에 근거 표시\n"
    )


if __name__ == "__main__":
    _PROJECT_ROOT = str(BASE_DIR)
    if _PROJECT_ROOT not in sys.path:
        sys.path.insert(0, _PROJECT_ROOT)

    run_evidence_demo()
