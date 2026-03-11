"""
RAG 응답 파서 모듈.

LLM 원문 응답에서 답변(answer)과 출처 목록(sources)을 분리하여
JSON 형식의 구조화된 응답으로 변환한다.
"""

import re
from typing import Any

from langchain.schema import Document


def parse_sources_from_docs(docs: list[Document]) -> list[dict[str, Any]]:
    """
    검색된 Document 목록에서 출처 정보를 추출하여 반환한다.

    Args:
        docs: LangChain Document 객체 목록

    Returns:
        출처 정보 딕셔너리 목록.
        각 항목: {"doc": 문서명, "page": 페이지, "snippet": 내용 앞 100자}

    Examples:
        >>> docs = [Document(page_content="내용", metadata={"source": "HR", "page": 3})]
        >>> parse_sources_from_docs(docs)
        [{"doc": "HR", "page": 3, "snippet": "내용"}]
    """
    # === INPUT ===
    sources = []

    # === PROCESS ===
    seen_sources: set[str] = set()
    for doc in docs:
        source = doc.metadata.get("source", "알 수 없는 문서")
        page = doc.metadata.get("page", 0)
        # 동일 출처 중복 제거
        source_key = f"{source}::{page}"
        if source_key in seen_sources:
            continue
        seen_sources.add(source_key)

        snippet = doc.page_content[:120].strip()
        if len(doc.page_content) > 120:
            snippet += "..."

        sources.append(
            {
                "doc": source,
                "page": int(page) if page else 0,
                "snippet": snippet,
            }
        )

    # === OUTPUT ===
    return sources


def parse_answer_text(raw_answer: str) -> str:
    """
    LLM 원문 응답에서 <think>...</think> 태그(DeepSeek R1 추론 토큰)를
    제거하고 실제 답변 텍스트만 반환한다.

    Args:
        raw_answer: LLM에서 받은 원문 응답 문자열

    Returns:
        정제된 답변 문자열 (앞뒤 공백 제거)
    """
    # === INPUT ===
    text = raw_answer

    # === PROCESS ===
    # DeepSeek R1의 <think> 추론 토큰 제거
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = text.strip()

    # 빈 문자열이면 기본 메시지 반환
    if not text:
        text = "답변을 생성하지 못했습니다. 다시 시도해 주세요."

    # === OUTPUT ===
    return text


def build_response(
    raw_answer: str,
    docs: list[Document],
) -> dict[str, Any]:
    """
    LLM 원문 응답과 검색 문서로부터 최종 API 응답 딕셔너리를 구성한다.

    Args:
        raw_answer: LLM이 생성한 원문 답변 문자열
        docs: 검색된 LangChain Document 목록

    Returns:
        JSON 직렬화 가능한 응답 딕셔너리.
        구조: {"answer": str, "sources": list[dict]}

    Examples:
        >>> response = build_response("3일 미만 병가는 증빙 불필요...", docs)
        >>> response["answer"]
        "3일 미만 병가는 증빙 불필요..."
        >>> response["sources"][0]["doc"]
        "HR_취업규칙_v1.0"
    """
    # === INPUT ===
    answer = parse_answer_text(raw_answer)
    sources = parse_sources_from_docs(docs)

    # === PROCESS & OUTPUT ===
    return {
        "answer": answer,
        "sources": sources,
    }
