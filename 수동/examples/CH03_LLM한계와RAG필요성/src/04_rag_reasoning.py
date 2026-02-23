"""
[Step 4 — 심화] RAG + DeepSeek R1 추론 능력 확인

이 스크립트는 03_rag_preview.py와 동일한 RAG 구조를 사용하여,
단순한 정보 검색이 아니라 계산·추론이 필요한 질문에 답변합니다.

핵심 질문:
  "입사 6개월차 신입인데 리프레시 데이 2번 썼어. 몇 번 남았는지 규정 기반으로 계산해줘."

처리 흐름:
  1. ChromaDB에서 "신입사원 리프레시 데이" 관련 청크 검색
  2. 검색된 규정(매월 1회 = 6개월 → 총 6번 사용 가능)을 LLM에 전달
  3. DeepSeek R1이 6 - 2 = 4번 남았다고 계산하여 답변

주의:
  - ChromaDB는 인메모리 전용 (영속화 없음)
  - LCEL(|) 연산자 기반 파이프라인 사용 (RetrievalQA 사용 금지)

실행:
  python src/04_rag_reasoning.py
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

# 추론·계산이 필요한 질문 (03번과 다른 점)
REASONING_QUESTION: str = (
    "입사 6개월차 신입인데 리프레시 데이 2번 썼어. "
    "몇 번 남았는지 규정 기반으로 계산해줘."
)

# 검색에 사용할 HR 규정 문서 (03번과 동일 구조, 추론에 필요한 수치 포함)
HR_DOCS: list[Document] = [
    Document(
        page_content=(
            "[인사규정] 신입사원 연차 및 리프레시 데이: "
            "신입사원은 입사 후 3년간 법정 연차가 발생하지 않는다. "
            "대신 매월 1회 유급 리프레시 데이를 사용할 수 있다. "
            "리프레시 데이는 해당 월에 미사용 시 다음 달로 이월되지 않는다. "
            "3일 이상 연속 사용 시 팀장 사전 승인이 필요하다."
        ),
        metadata={"source": "인사규정", "section": "제4조"},
    ),
    Document(
        page_content=(
            "[보안규정] 보안 USB 사용 정책: "
            "모든 임직원은 회사가 지급한 보안 인증 USB만 사용해야 한다. "
            "개인 USB 및 외부 저장매체 사용은 엄격히 금지된다. "
            "위반 시 보안 규정 위반으로 처리된다."
        ),
        metadata={"source": "보안규정", "section": "제7조"},
    ),
    Document(
        page_content=(
            "[복지규정] 식대 지원 정책: "
            "점심 식대는 무제한 법인카드로 지원한다. "
            "저녁 식사는 오후 9시 이후 야근 시에만 사용 가능하다. "
            "주말 및 공휴일 식대는 별도 신청 양식을 사용한다."
        ),
        metadata={"source": "복지규정", "section": "제10조"},
    ),
]


def build_vectorstore(docs: list[Document]) -> Chroma:
    """
    Document 목록을 임베딩하여 인메모리 ChromaDB에 저장합니다.

    각 Document는 이미 적절한 크기로 정의되어 있으므로
    추가적인 청킹 없이 그대로 저장합니다.

    Input  : langchain_core.documents.Document 목록
    Process: OllamaEmbeddings 생성 → Chroma.from_documents() 호출
    Output : 인메모리 Chroma VectorStore 인스턴스

    Args:
        docs: 임베딩할 Document 객체 목록

    Returns:
        인메모리 Chroma VectorStore 인스턴스

    Raises:
        SystemExit: 임베딩 모델 연결 실패 또는 벡터스토어 생성 실패 시
    """

    # --- Input ---
    if not docs:
        raise ValueError("저장할 Document 목록이 비어 있습니다.")

    # --- Process ---
    try:
        embeddings = OllamaEmbeddings(
            model=EMBED_MODEL,
            base_url=OLLAMA_BASE_URL,
        )
        # persist_directory 없음 → 인메모리 전용
        vectorstore = Chroma.from_documents(
            documents=docs,
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
    검색된 Document 목록을 출처 정보와 함께 컨텍스트 문자열로 변환합니다.

    출처 정보(source, section)를 포함하여 LLM이 어떤 규정 조항을
    근거로 답변하는지 명확히 알 수 있도록 합니다.

    Input  : langchain_core.documents.Document 목록
    Process: 각 Document의 metadata와 page_content를 포함한 문자열로 결합
    Output : 출처와 내용이 포함된 컨텍스트 문자열

    Args:
        docs: 검색된 Document 객체 목록

    Returns:
        출처와 내용이 포함된 컨텍스트 문자열
    """

    # --- Input ---
    if not docs:
        return "(검색된 문서 없음)"

    # --- Process ---
    parts: list[str] = []
    for doc in docs:
        source = doc.metadata.get("source", "출처 불명")
        section = doc.metadata.get("section", "")
        header = f"[{source} {section}]" if section else f"[{source}]"
        parts.append(f"{header}\n{doc.page_content}")

    # --- Output ---
    return "\n\n".join(parts)


def build_rag_chain(vectorstore: Chroma, k: int = 2) -> tuple[Any, Any]:
    """
    추론·계산 질문에 특화된 LCEL 기반 RAG 체인을 생성합니다.

    03번 실험과 동일한 LCEL 구조이지만, 프롬프트에 "계산 과정을 포함하여
    답변하라"는 지시를 추가하여 DeepSeek R1의 추론 능력을 활용합니다.

    Input  : Chroma VectorStore 인스턴스, 검색할 문서 수 k
    Process: retriever 생성 → 추론 프롬프트 정의 → LCEL | 체인 구성
    Output : (LCEL Runnable 체인, retriever) 튜플

    Args:
        vectorstore: 검색 대상 ChromaDB VectorStore
        k: 유사도 검색으로 반환할 최대 문서 수 (기본값: 2)

    Returns:
        (rag_chain, retriever) 튜플
    """

    # --- Input ---
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})

    # --- Process ---
    # 추론·계산 질문에 특화된 프롬프트
    # "계산 과정을 단계별로 제시하라"는 지시를 추가하여 DeepSeek R1의 추론 능력 활용
    prompt = ChatPromptTemplate.from_template(
        """당신은 회사 내부 규정을 기반으로 계산과 추론을 수행하는 AI 비서입니다.
아래 [참고 문서]의 규정을 근거로 질문에 답변하십시오.

중요 지침:
  1. 계산이 필요한 경우 반드시 계산 과정을 단계별로 제시하십시오.
  2. 규정의 어느 조항을 근거로 답변하는지 명시하십시오.
  3. 참고 문서에 없는 내용은 "해당 내용이 문서에 없습니다"라고 답변하십시오.
  4. 반드시 한국어로 답변하십시오.

[참고 문서]
{context}

[질문]
{question}

[답변 — 규정 근거와 계산 과정을 포함하여]"""
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


def display_retrieved_docs(docs: list[Document]) -> None:
    """
    검색된 근거 문서를 터미널에 출력합니다.

    RAG가 어떤 문서를 검색하여 LLM에 전달했는지 확인함으로써
    "RAG = 검색 + 생성"임을 명확히 이해할 수 있습니다.

    Input  : 검색된 Document 목록
    Process: 각 Document의 출처와 내용을 포맷하여 출력
    Output : 표준 출력으로 검색 문서 목록 출력

    Args:
        docs: 검색된 Document 객체 목록
    """

    # --- Input ---
    print(f"\n[검색 근거 문서] — {len(docs)}개 청크가 LLM에 전달되었습니다.")
    print("-" * 65)

    # --- Process ---
    for i, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source", "출처 불명")
        section = doc.metadata.get("section", "")
        label = f"{source} {section}" if section else source
        print(f"  [{i}] {label}")
        print(f"      {doc.page_content[:100]}...")

    # --- Output ---
    print("-" * 65)


def main() -> None:
    """
    계산·추론이 필요한 질문으로 RAG + DeepSeek R1 추론 능력을 시연합니다.

    동일한 RAG 구조(03_rag_preview.py)를 사용하되, 질문을
    "리프레시 데이 몇 번 남았어?"와 같이 계산이 필요한 형태로 교체합니다.

    Input  : REASONING_QUESTION 상수, HR_DOCS 상수
    Process:
      1) HR_DOCS를 임베딩하여 인메모리 ChromaDB 생성
      2) LCEL RAG 체인 구성
      3) 질문 실행 → 검색 문서 출력 → LLM 답변 출력
    Output : 검색 근거 문서 + LLM 추론 답변을 표준 출력으로 출력
    """

    # --- Input ---
    print("=" * 65)
    print("CH03 실험 4: RAG + 추론 — DeepSeek R1 계산·추론 능력 확인")
    print("=" * 65)
    print(f"사용 모델    : {OLLAMA_MODEL}")
    print(f"임베딩 모델  : {EMBED_MODEL}")
    print(f"Ollama 서버  : {OLLAMA_BASE_URL}")
    print(f"ChromaDB 모드: 인메모리 전용 (재실행 시 초기화)")
    print()
    print("이 실험은 RAG가 단순한 정보 검색을 넘어 LLM의 추론 능력과")
    print("결합하여 계산 문제도 해결할 수 있음을 보여줍니다.\n")

    # --- Process ---
    # 1단계: 문서 임베딩 및 벡터스토어 생성
    print("[단계 1/3] HR 규정 문서를 임베딩하여 ChromaDB에 저장 중...")
    print(f"           저장할 문서: {len(HR_DOCS)}개 (인사규정, 보안규정, 복지규정)")
    start_embed = time.time()
    vectorstore = build_vectorstore(HR_DOCS)
    elapsed_embed = time.time() - start_embed
    print(f"           임베딩 완료 ({elapsed_embed:.1f}초)")

    # 2단계: LCEL RAG 체인 구성
    print("\n[단계 2/3] LCEL RAG 체인 구성 중...")
    rag_chain, retriever = build_rag_chain(vectorstore, k=2)
    print("           체인 구성 완료: 검색기 → 추론 프롬프트 → LLM → 파서")

    # 3단계: 질문 실행
    print("\n[단계 3/3] 추론 질문 실행 중...")
    print(f"\n{'=' * 65}")
    print("질문:")
    print(f"  {REASONING_QUESTION}")
    print("=" * 65)

    # 검색 근거 문서 확인
    retrieved_docs = retriever.invoke(REASONING_QUESTION)
    display_retrieved_docs(retrieved_docs)

    print("\n[LLM 추론 중...]")
    print("DeepSeek R1이 검색된 규정을 바탕으로 계산합니다...")
    print("  규정: 신입사원은 매월 1회 리프레시 데이를 사용할 수 있다.")
    print("  입사 6개월 → 총 6번 사용 가능")
    print("  이미 2번 사용 → 6 - 2 = 4번 남음\n")

    start_answer = time.time()
    answer = rag_chain.invoke(REASONING_QUESTION)
    elapsed_answer = time.time() - start_answer

    # --- Output ---
    print(f"LLM 추론 답변 ({elapsed_answer:.1f}초):\n")
    print(answer)

    print("\n" + "=" * 65)
    print("실험 4 완료: RAG + 추론")
    print("=" * 65)
    print("\n[핵심 관찰]")
    print("  RAG는 단순히 문서를 검색하여 그대로 반환하는 것이 아닙니다.")
    print("  검색된 규정(매월 1회)을 LLM에 전달하면,")
    print("  LLM이 '6개월 × 1회 - 2회 = 4회'를 직접 계산하여 답변합니다.")
    print("  이것이 RAG + LLM 추론의 조합이 강력한 이유입니다.\n")
    print("[다음 챕터]")
    print("  4장: 사내 시스템(DB + CRUD API)을 확보하고 MCP 개념을 학습합니다.")
    print("  6장: 실제 PDF 문서로 체계적인 RAG 파이프라인을 구현합니다.\n")


if __name__ == "__main__":
    main()
