"""
[Step 3 — 성공] RAG 미리보기 + 청킹 비교

이 스크립트는 인메모리 ChromaDB를 사용하여 RAG 동작을 체험합니다.

Part A: 청킹 없음
  - HR 규정 문서 전체를 단일 Document로 저장
  - 질문과 관련 없는 내용까지 함께 검색됨 → 낮은 정밀도

Part B: 청킹 있음
  - 동일 문서를 ~200자 청크로 분리하여 저장
  - 질문에 정확히 관련된 청크만 반환 → 높은 정밀도

두 결과를 나란히 출력하여 청킹의 필요성을 직접 비교합니다.

주의:
  - ChromaDB는 인메모리 전용(persist_directory 없음)
  - 스크립트 종료 후 데이터는 소멸됨 (개념 체험 목적)
  - LCEL(|) 연산자 기반 파이프라인 사용 (RetrievalQA 사용 금지)
  - 임베딩 모델 필요: ollama pull nomic-embed-text

실행:
  python src/03_rag_preview.py
"""

import os
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import ChatOllama, OllamaEmbeddings

# --- 환경 변수 로드 ---
_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)

# --- 상수 정의 ---
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "deepseek-r1:1.5b")
EMBED_MODEL: str = os.getenv("EMBED_MODEL", "nomic-embed-text")

# 비교 실험에 사용할 HR 규정 문서 (3개 섹션, 명확한 주제 분리)
LONG_DOC: str = """[테크컴퍼니 취업규칙 요약]

제1조 (신입사원 연차 및 리프레시 데이 규정)
신입사원은 입사 후 3년간 법정 연차가 발생하지 않는다.
대신 매월 1회 유급 리프레시 데이를 사용할 수 있다.
리프레시 데이는 해당 월에 미사용 시 다음 달로 이월되지 않는다.
3일 이상 연속 사용 시 팀장 사전 승인이 필요하다.

제2조 (보안 USB 정책)
모든 임직원은 회사가 지급한 보안 인증 USB만 사용해야 한다.
개인 USB 및 외부 저장매체 사용은 엄격히 금지된다.
위반 시 보안 규정 위반으로 처리되며, 3회 누적 시 징계위원회에 회부된다.
보안 USB 분실 시 즉시 IT팀(내선 1004)에 신고해야 한다.

제3조 (식대 지원)
점심 식대는 무제한 법인카드로 지원한다.
저녁 식사는 오후 9시 이후 야근 시에만 사용 가능하다.
주말 및 공휴일 식대는 별도 신청 양식을 사용한다.
1인당 1식 기준 3만 원 이내의 합리적인 금액으로 사용해야 한다.
"""

# 비교 실험에 사용할 질문
QUERY: str = "신입사원 리프레시 데이 규정 알려줘."


def chunk_text(text: str, chunk_size: int = 200, overlap: int = 20) -> list[str]:
    """
    텍스트를 chunk_size 단위로 분할합니다.

    overlap만큼 이전 청크와 내용이 겹치도록 분할하여
    청크 경계에서 문맥이 끊기는 것을 방지합니다.

    Input  : 분할할 텍스트 문자열, 청크 크기(자), 오버랩(자)
    Process: chunk_size 간격으로 시작점을 이동하며 슬라이싱
    Output : 청크 문자열 목록

    Args:
        text: 분할할 텍스트 문자열
        chunk_size: 각 청크의 최대 문자 수 (기본값: 200)
        overlap: 이전 청크와 겹치는 문자 수 (기본값: 20)

    Returns:
        청크 문자열 목록 (빈 청크 제외)
    """

    # --- Input ---
    if not text.strip():
        return []
    if chunk_size <= 0:
        raise ValueError("chunk_size는 양의 정수여야 합니다.")
    if overlap < 0:
        raise ValueError("overlap은 0 이상이어야 합니다.")
    if overlap >= chunk_size:
        raise ValueError("overlap은 chunk_size보다 작아야 합니다.")

    # --- Process ---
    chunks: list[str] = []
    step = chunk_size - overlap
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += step

    # --- Output ---
    return chunks


def build_vectorstore_no_chunk(doc: str) -> Chroma:
    """
    문서 전체를 단일 Document로 인메모리 ChromaDB에 저장합니다.

    청킹 없이 저장하면 검색 시 문서 전체가 하나의 단위로 처리됩니다.
    질문과 관련 없는 내용도 함께 반환되어 정밀도가 낮습니다.

    Input  : 저장할 텍스트 문서 문자열
    Process: 단일 Document 생성 → OllamaEmbeddings → 인메모리 Chroma 생성
    Output : 인메모리 ChromaDB VectorStore 인스턴스

    Args:
        doc: 저장할 텍스트 문서 전체 문자열

    Returns:
        인메모리 Chroma VectorStore 인스턴스

    Raises:
        SystemExit: 임베딩 모델 로드 실패 시
    """

    # --- Input ---
    documents = [
        Document(
            page_content=doc,
            metadata={"source": "hr_policy", "chunk_id": 0, "method": "no_chunk"},
        )
    ]

    # --- Process ---
    try:
        embeddings = OllamaEmbeddings(
            model=EMBED_MODEL,
            base_url=OLLAMA_BASE_URL,
        )
        # persist_directory 없음 → 인메모리 전용
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
        )
    except Exception as e:
        print(f"\n[오류] 벡터스토어 생성 실패: {e}")
        print(f"      임베딩 모델이 다운로드되어 있는지 확인하십시오: ollama pull {EMBED_MODEL}")
        sys.exit(1)

    # --- Output ---
    return vectorstore


def build_vectorstore_with_chunk(doc: str) -> Chroma:
    """
    문서를 chunk_text()로 분할한 후 각 청크를 별도 Document로 저장합니다.

    청킹 후 저장하면 검색 시 질문과 관련된 청크만 반환되어
    정밀도가 높아집니다.

    Input  : 저장할 텍스트 문서 문자열
    Process: chunk_text()로 분할 → 각 청크를 Document로 변환 → 인메모리 Chroma 생성
    Output : 인메모리 ChromaDB VectorStore 인스턴스

    Args:
        doc: 저장할 텍스트 문서 전체 문자열

    Returns:
        인메모리 Chroma VectorStore 인스턴스

    Raises:
        SystemExit: 임베딩 모델 로드 실패 시
    """

    # --- Input ---
    chunks = chunk_text(doc, chunk_size=200, overlap=20)
    documents = [
        Document(
            page_content=chunk,
            metadata={"source": "hr_policy", "chunk_id": i, "method": "with_chunk"},
        )
        for i, chunk in enumerate(chunks)
    ]

    # --- Process ---
    try:
        embeddings = OllamaEmbeddings(
            model=EMBED_MODEL,
            base_url=OLLAMA_BASE_URL,
        )
        # persist_directory 없음 → 인메모리 전용
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
        )
    except Exception as e:
        print(f"\n[오류] 벡터스토어 생성 실패: {e}")
        print(f"      임베딩 모델이 다운로드되어 있는지 확인하십시오: ollama pull {EMBED_MODEL}")
        sys.exit(1)

    # --- Output ---
    return vectorstore


def format_docs(docs: list[Document]) -> str:
    """
    검색된 Document 목록을 컨텍스트 문자열로 변환합니다.

    각 Document에 청크 번호를 붙여 LLM이 어느 청크에서 답변을 찾았는지
    파악할 수 있도록 합니다.

    Input  : langchain_core.documents.Document 목록
    Process: 각 Document의 page_content에 청크 번호를 붙여 문자열로 결합
    Output : LLM에 전달할 컨텍스트 문자열

    Args:
        docs: 검색된 Document 객체 목록

    Returns:
        청크 번호와 내용을 포함한 컨텍스트 문자열
    """

    # --- Input ---
    if not docs:
        return "(검색된 문서 없음)"

    # --- Process ---
    formatted_parts: list[str] = []
    for i, doc in enumerate(docs, start=1):
        chunk_id = doc.metadata.get("chunk_id", i - 1)
        part = f"[청크 {chunk_id}]\n{doc.page_content}"
        formatted_parts.append(part)

    # --- Output ---
    return "\n\n".join(formatted_parts)


def build_rag_chain(vectorstore: Chroma, k: int = 2) -> Any:
    """
    LCEL 기반 RAG 체인을 생성합니다.

    LCEL(LangChain Expression Language)의 | 연산자를 사용하여
    검색기 → 프롬프트 → LLM → 파서 파이프라인을 구성합니다.
    RetrievalQA 또는 langchain_classic은 사용하지 않습니다.

    Input  : Chroma VectorStore 인스턴스, 검색할 문서 수 k
    Process: retriever 생성 → 프롬프트 정의 → LCEL | 체인 구성
    Output : 실행 가능한 LCEL Runnable 체인

    Args:
        vectorstore: 검색 대상 ChromaDB VectorStore
        k: 유사도 검색으로 반환할 최대 문서(청크) 수 (기본값: 2)

    Returns:
        LCEL Runnable 체인 (invoke(query) 호출 가능)
    """

    # --- Input ---
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})

    # --- Process ---
    prompt = ChatPromptTemplate.from_template(
        """당신은 회사 내부 규정에 대해 답변하는 AI 비서입니다.
아래 [참고 문서]를 바탕으로 질문에 답변하십시오.
참고 문서에 없는 내용은 "해당 내용이 문서에 없습니다"라고 답변하십시오.
반드시 한국어로 답변하십시오.

[참고 문서]
{context}

[질문]
{question}

[답변]"""
    )

    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0,
    )

    # LCEL 파이프라인: 검색기 + 프롬프트 + LLM + 파서
    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    # --- Output ---
    return rag_chain, retriever


def run_comparison(query: str) -> None:
    """
    Part A(청킹 없음)와 Part B(청킹 있음)를 순서대로 실행하고
    결과를 나란히 비교 출력합니다.

    두 실험에 동일한 문서(LONG_DOC)와 동일한 질문(query)을 사용하여
    청킹의 유무만이 검색 정밀도에 미치는 영향을 명확히 보여줍니다.

    Input  : 비교 실험에 사용할 질문 문자열
    Process:
      1) build_vectorstore_no_chunk() → build_rag_chain() → invoke()
      2) build_vectorstore_with_chunk() → build_rag_chain() → invoke()
    Output : 두 파트의 검색 결과 및 LLM 답변을 표준 출력으로 비교 출력

    Args:
        query: 비교 실험에 사용할 질문 문자열
    """

    # --- Input ---
    print(f"비교 질문: {query}\n")

    # ────────────────────────────────────────────────────────────
    # Part A: 청킹 없이
    # ────────────────────────────────────────────────────────────
    print("══ Part A: 청킹 없이 ══════════════════════════════════════")
    print("   문서 전체를 단일 Document로 저장합니다.")
    print("   문서를 청킹하지 않으면 질문과 무관한 내용까지 검색됩니다.\n")

    print("   [임베딩 중...] 문서 1개를 임베딩합니다.")
    start_a = time.time()
    vectorstore_a = build_vectorstore_no_chunk(LONG_DOC)
    rag_chain_a, retriever_a = build_rag_chain(vectorstore_a, k=1)

    # 검색된 문서 확인
    retrieved_docs_a = retriever_a.invoke(query)
    print(f"   검색된 문서 수: {len(retrieved_docs_a)}개  (문서 전체 1개)")
    print(f"   검색 내용 미리보기: {retrieved_docs_a[0].page_content[:80]}...")

    print("\n   [LLM 응답 중...]")
    answer_a = rag_chain_a.invoke(query)
    elapsed_a = time.time() - start_a

    print(f"\n   답변 ({elapsed_a:.1f}초):\n   {answer_a.replace(chr(10), chr(10) + '   ')}")

    # ────────────────────────────────────────────────────────────
    # Part B: 청킹 있을 때
    # ────────────────────────────────────────────────────────────
    print("\n══ Part B: 청킹 있을 때 ═══════════════════════════════════")
    print("   문서를 200자 단위 청크로 분리하여 저장합니다.")
    print("   청킹 후에는 질문과 관련된 청크만 정밀하게 반환됩니다.\n")

    chunks = chunk_text(LONG_DOC, chunk_size=200, overlap=20)
    print(f"   [임베딩 중...] {len(chunks)}개 청크를 임베딩합니다.")
    start_b = time.time()
    vectorstore_b = build_vectorstore_with_chunk(LONG_DOC)
    rag_chain_b, retriever_b = build_rag_chain(vectorstore_b, k=2)

    # 검색된 문서 확인
    retrieved_docs_b = retriever_b.invoke(query)
    print(f"   검색된 문서 수: {len(retrieved_docs_b)}개  (관련 청크만 선택됨)")
    for i, doc in enumerate(retrieved_docs_b, start=1):
        print(f"   [청크 {doc.metadata.get('chunk_id', i)}] {doc.page_content[:80]}...")

    print("\n   [LLM 응답 중...]")
    answer_b = rag_chain_b.invoke(query)
    elapsed_b = time.time() - start_b

    print(f"\n   답변 ({elapsed_b:.1f}초):\n   {answer_b.replace(chr(10), chr(10) + '   ')}")

    # ────────────────────────────────────────────────────────────
    # 비교 결과
    # ────────────────────────────────────────────────────────────
    print("\n── 비교 결과 ──────────────────────────────────────────────")
    print(f"  청킹 없음 (Part A): 검색 문서 {len(retrieved_docs_a)}개, 문서 전체 내용 포함")
    print(f"                     → 질문과 무관한 내용(보안 정책, 식대 등)도 컨텍스트에 포함")
    print(f"  청킹 있음 (Part B): 검색 문서 {len(retrieved_docs_b)}개, 관련 청크만 선택")
    print(f"                     → 제1조(연차·리프레시 데이) 관련 내용만 컨텍스트에 포함")
    print()
    print("  [결론] 청킹은 검색 정밀도를 높여 LLM이 더 정확한 컨텍스트를 받도록 합니다.")
    print("         6장(벡터 DB 구축)에서 실제 PDF 문서로 체계적인 청킹을 구현합니다.")

    # --- Output ---
    # (모든 출력은 위의 print() 호출에서 완료됨)


def main() -> None:
    """
    RAG 미리보기 비교 실험의 메인 진입점.

    run_comparison()을 호출하여 QUERY에 대해
    Part A(청킹 없음)와 Part B(청킹 있음)를 비교합니다.

    Input  : QUERY 상수, LONG_DOC 상수
    Process: run_comparison(QUERY) 호출
    Output : 비교 결과 표준 출력
    """

    # --- Input ---
    print("=" * 65)
    print("CH03 실험 3: RAG 미리보기 — 청킹 없음 vs 청킹 있음 비교")
    print("=" * 65)
    print(f"사용 모델    : {OLLAMA_MODEL}")
    print(f"임베딩 모델  : {EMBED_MODEL}")
    print(f"Ollama 서버  : {OLLAMA_BASE_URL}")
    print(f"ChromaDB 모드: 인메모리 전용 (재실행 시 초기화)")
    print()
    print("동일한 문서와 동일한 질문으로 청킹의 유무가")
    print("검색 정밀도에 미치는 영향을 비교합니다.\n")

    # --- Process ---
    run_comparison(QUERY)

    # --- Output ---
    print("\n" + "=" * 65)
    print("실험 3 완료: RAG 미리보기")
    print("=" * 65)
    print("\n[다음 단계]")
    print("  python src/04_rag_reasoning.py")
    print("  → 동일한 RAG 구조로 계산·추론이 필요한 질문에 답변합니다.\n")


if __name__ == "__main__":
    main()
