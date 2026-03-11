"""기초 RAG 구현 모듈 — ChromaDB + LLM 파이프라인 (섹션 2.3).

ChromaDB 로컬 컬렉션에 사내 HR 문서 샘플을 저장하고,
사용자 질문에 대해 유사도 검색으로 관련 문서를 찾은 후
LLM에 전달하여 정확한 답변을 생성합니다.
출처 문서 정보를 함께 표시하여 신뢰성을 높입니다.
"""

import os
from typing import Optional

import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# --- 상수 ---
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
COLLECTION_NAME = "hr_documents"
TOP_K = 2  # 검색 시 반환할 관련 문서 수

# 인메모리 샘플 HR 문서 (파일 없이 동작)
SAMPLE_HR_DOCUMENTS: list[dict[str, str]] = [
    {
        "id": "hr-leave-001",
        "content": (
            "커넥트HR 연차유급휴가 규정 (제1조)\n"
            "신입사원(근속 1년 미만)은 입사 후 매월 1일씩 월차를 부여하여 최대 11일 사용 가능합니다. "
            "근속 1년 이상 직원은 연 15일의 연차유급휴가를 부여합니다. "
            "근속 3년 이상부터는 2년마다 1일씩 추가하여 최대 25일까지 부여합니다. "
            "미사용 연차는 연말 정산 시 통상임금으로 지급합니다."
        ),
        "source": "HR-인사규정-2024.pdf",
        "page": "3",
    },
    {
        "id": "hr-vacation-002",
        "content": (
            "커넥트HR 여름 휴가 지원금 규정 (제2조)\n"
            "전 직원에게 여름 휴가 지원금으로 1인당 30만원을 지급합니다. "
            "지급 시기는 매년 6월 마지막 주 급여일입니다. "
            "근속 기간에 관계없이 동일 금액을 지급합니다."
        ),
        "source": "HR-인사규정-2024.pdf",
        "page": "5",
    },
    {
        "id": "hr-remote-003",
        "content": (
            "커넥트HR 재택근무 정책 (제3조)\n"
            "재택근무 신청은 근무일 기준 2일 전까지 팀장에게 서면 승인을 받아야 합니다. "
            "재택근무는 월 최대 6일까지 허용됩니다. "
            "중요 회의 또는 프로젝트 마감일에는 재택근무를 사용할 수 없습니다."
        ),
        "source": "HR-재택근무정책-2024.pdf",
        "page": "1",
    },
]

# 검색 테스트 질문
TEST_QUESTION = "커넥트HR의 연차 규정에서 신입사원 1년차 연차 일수는 몇 일입니까?"

# Mock LLM 응답 — Ollama 미연결 시
MOCK_RAG_RESPONSE = (
    "검색된 커넥트HR 인사 규정(HR-인사규정-2024.pdf, 3페이지)에 따르면, "
    "신입사원(근속 1년 미만)은 입사 후 매월 1일씩 월차를 부여받아 최대 11일을 사용할 수 있습니다. "
    "이는 RAG가 정확한 문서를 검색하여 LLM에 전달했기 때문에 가능한 정확한 답변입니다."
)


def create_chroma_collection() -> chromadb.Collection:
    """ChromaDB 인메모리 컬렉션을 생성하고 샘플 문서를 저장합니다.

    별도 파일 없이 메모리에서 동작하므로 실습 환경을 간소화합니다.

    Returns:
        문서가 저장된 ChromaDB 컬렉션 객체

    Raises:
        RuntimeError: ChromaDB 초기화에 실패한 경우
    """
    # --- Input ---
    try:
        # 인메모리 ChromaDB 클라이언트 생성
        chroma_client = chromadb.Client()

        # 기본 임베딩 함수 사용 (sentence-transformers 없이 동작)
        embedding_fn = embedding_functions.DefaultEmbeddingFunction()

        # 컬렉션 생성
        collection = chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_fn,
        )
    except Exception as e:
        raise RuntimeError(f"ChromaDB 초기화에 실패했습니다: {e}")

    # --- Process ---
    # 샘플 문서를 컬렉션에 저장
    doc_ids = [doc["id"] for doc in SAMPLE_HR_DOCUMENTS]
    doc_contents = [doc["content"] for doc in SAMPLE_HR_DOCUMENTS]
    doc_metadatas = [
        {"source": doc["source"], "page": doc["page"]}
        for doc in SAMPLE_HR_DOCUMENTS
    ]

    collection.add(
        ids=doc_ids,
        documents=doc_contents,
        metadatas=doc_metadatas,
    )

    # --- Output ---
    return collection


def search_similar_documents(
    collection: chromadb.Collection,
    query: str,
    top_k: int = TOP_K,
) -> list[dict[str, str]]:
    """질문과 유사한 문서를 ChromaDB에서 검색합니다.

    벡터 유사도 검색을 통해 질문과 의미적으로 가까운
    문서를 top_k개 반환합니다.

    Args:
        collection: ChromaDB 컬렉션 객체
        query: 검색 질문 문자열
        top_k: 반환할 최대 문서 수 (기본값: 2)

    Returns:
        검색된 문서 딕셔너리 목록. 각 항목에 content, source, page 포함.
    """
    # --- Input ---
    results = collection.query(
        query_texts=[query],
        n_results=min(top_k, collection.count()),
    )

    # --- Process ---
    retrieved_docs: list[dict[str, str]] = []
    if results["documents"] and results["documents"][0]:
        for i, doc_content in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][i] if results["metadatas"] else {}
            retrieved_docs.append(
                {
                    "content": doc_content,
                    "source": metadata.get("source", "알 수 없음"),
                    "page": metadata.get("page", "0"),
                }
            )

    # --- Output ---
    return retrieved_docs


def build_rag_prompt(question: str, retrieved_docs: list[dict[str, str]]) -> str:
    """검색된 문서를 바탕으로 RAG 프롬프트를 구성합니다.

    Args:
        question: 사용자 질문 문자열
        retrieved_docs: 검색된 관련 문서 목록

    Returns:
        LLM에 전달할 완성된 프롬프트 문자열
    """
    # --- Input ---
    context_parts: list[str] = []
    for i, doc in enumerate(retrieved_docs, start=1):
        context_parts.append(
            f"[문서 {i}] 출처: {doc['source']} (페이지 {doc['page']})\n{doc['content']}"
        )
    context = "\n\n".join(context_parts)

    # --- Process ---
    prompt = f"""다음 검색된 사내 문서만을 근거로 질문에 답하십시오.
문서에 없는 내용은 "해당 정보가 문서에 없습니다"라고 답하십시오.

[검색된 문서]
{context}

[질문]
{question}

[답변]"""

    # --- Output ---
    return prompt


def generate_answer(
    prompt: str,
    client: Optional[object],
    retrieved_docs: list[dict[str, str]],
) -> str:
    """LLM으로 최종 답변을 생성합니다.

    Args:
        prompt: RAG 프롬프트 문자열
        client: Ollama 클라이언트 객체. None이면 Mock 응답 반환.
        retrieved_docs: 출처 표시에 사용할 검색 문서 목록

    Returns:
        LLM 또는 Mock 응답 문자열
    """
    # --- Input ---
    if client is None:
        return MOCK_RAG_RESPONSE

    # --- Process ---
    try:
        answer = client.invoke(prompt)
    except Exception as e:
        print(f"LLM 응답 생성 중 오류가 발생했습니다: {e}")
        answer = MOCK_RAG_RESPONSE

    # --- Output ---
    return answer


def create_ollama_client() -> Optional[object]:
    """Ollama 클라이언트를 생성합니다.

    Returns:
        Ollama 클라이언트 객체. 연결 실패 시 None 반환.
    """
    try:
        from langchain_ollama import OllamaLLM

        client = OllamaLLM(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
        client.invoke("안녕")
        return client
    except Exception:
        return None


def run_simple_rag_demo() -> None:
    """기초 RAG 파이프라인 데모를 실행합니다.

    ChromaDB에 문서를 저장하고 유사도 검색 후 LLM 답변을 생성하는
    전체 RAG 파이프라인을 단계별로 보여줍니다.
    """
    print("=" * 60)
    print("Step 3: 기초 RAG — ChromaDB + LLM 파이프라인")
    print("=" * 60)
    print(f"모델: {OLLAMA_MODEL}")
    print()

    # --- Input ---
    # 1단계: ChromaDB 컬렉션 준비
    print("[1단계] ChromaDB 인메모리 컬렉션에 HR 문서 저장 중...")
    try:
        collection = create_chroma_collection()
        print(f"        완료: {collection.count()}개 문서 저장됨")
    except RuntimeError as e:
        print(f"ChromaDB 초기화 실패: {e}")
        print("chromadb 패키지 설치를 확인하십시오: pip install chromadb")
        return
    print()

    # 2단계: 질문 확인
    question = TEST_QUESTION
    print(f"[2단계] 사용자 질문: {question}")
    print()

    # --- Process ---
    # 3단계: 유사도 검색
    print("[3단계] ChromaDB에서 관련 문서 검색 중...")
    retrieved_docs = search_similar_documents(collection, question, top_k=TOP_K)
    print(f"        {len(retrieved_docs)}개 관련 문서 검색 완료")
    print()

    for i, doc in enumerate(retrieved_docs, start=1):
        print(f"  [검색 결과 {i}]")
        print(f"  출처: {doc['source']} (페이지 {doc['page']})")
        print(f"  내용 미리보기: {doc['content'][:80]}...")
        print()

    # 4단계: RAG 프롬프트 구성
    print("[4단계] 검색된 문서로 RAG 프롬프트 구성...")
    rag_prompt = build_rag_prompt(question, retrieved_docs)
    print(f"        프롬프트 길이: {len(rag_prompt)}자 (전체 문서 대비 최소화)")
    print()

    # 5단계: LLM 답변 생성
    print("[5단계] Ollama 서버 연결 시도 중...")
    client = create_ollama_client()
    if client is None:
        print("        [Mock 모드] Ollama 미연결 — Mock 응답 사용")
    else:
        print("        [연결 성공] Ollama 서버 연결됨")
    print()

    print("[6단계] LLM 답변 생성 중...")
    answer = generate_answer(rag_prompt, client, retrieved_docs)

    # --- Output ---
    print()
    print("=" * 60)
    print("[최종 답변]")
    print("=" * 60)
    print(answer)
    print()

    print("[출처 문서]")
    for i, doc in enumerate(retrieved_docs, start=1):
        print(f"  {i}. {doc['source']} — 페이지 {doc['page']}")
    print()

    print("=" * 60)
    print("[결론] RAG 파이프라인이 성공적으로 작동했습니다!")
    print()
    print("RAG의 핵심 장점:")
    print("  1. 관련 문서만 선택 검색 → 토큰 사용량 최소화")
    print("  2. 실제 사내 문서 기반 답변 → 환각 방지")
    print("  3. 출처 표시 → 답변 신뢰성 확보")
    print("  4. 문서가 늘어나도 검색 속도 일정 → 확장성")
    print("=" * 60)
    print()


if __name__ == "__main__":
    run_simple_rag_demo()
