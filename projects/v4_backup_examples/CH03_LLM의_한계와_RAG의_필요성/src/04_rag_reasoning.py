"""
04_rag_reasoning.py — RAG + DeepSeek R1 추론 능력 확인

RAG로 검색된 매출 데이터를 컨텍스트로 제공하고,
LLM의 추론(계산, 집계) 능력을 함께 활용하여 복잡한 질문에 답변합니다.

이 실습의 핵심:
    - RAG는 단순 검색+답변을 넘어 '추론'까지 가능합니다
    - DeepSeek R1의 Chain-of-Thought 추론으로 계산 과정을 명시합니다
    - 인메모리 ChromaDB에 매출 데이터를 저장하고 집계 질문에 답변합니다

실행 방법:
    python src/04_rag_reasoning.py

필요 환경:
    - Ollama가 실행 중이어야 합니다 (ollama serve)
    - 최초 실행 시 한국어 임베딩 모델이 자동 다운로드됩니다 (~400MB)
"""

import sys
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# ChromaDB 임포트
try:
    import chromadb
    from chromadb.utils import embedding_functions
except ImportError:
    print("\n[오류] chromadb 패키지가 설치되지 않았습니다.")
    print("  해결 방법: pip install -r requirements.txt")
    sys.exit(1)

# .env 파일 로드
load_dotenv(Path(__file__).parent.parent / ".env")

# --- 설정 상수 ---
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:8b")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

EMBEDDING_MODEL = "jhgan/ko-sroberta-multitask"  # 한국어 임베딩 모델
TOP_K = 5  # 검색 결과 상위 K개 (매출 데이터는 여러 행이 필요)
REQUEST_TIMEOUT = 180  # 초 (추론 질문은 응답이 더 오래 걸릴 수 있음)


# =============================================================================
# === INPUT ===
# =============================================================================

# 매출 데이터 샘플 — 월별/부서별 매출 기록
# 실제 사내 시스템에서는 PostgreSQL에서 가져오지만, 이 실습에서는 텍스트로 표현합니다
SALES_DOCUMENTS = [
    {
        "id": "sales_2025_01_dev",
        "content": (
            "매출 기록 — 2025년 1월 개발팀\n"
            "기간: 2025-01-01 ~ 2025-01-31\n"
            "부서: 개발팀\n"
            "제품: 소프트웨어 라이선스\n"
            "매출액: 45,000,000원\n"
            "계약 건수: 12건\n"
            "주요 고객: A전자, B물류, C유통\n"
        ),
        "metadata": {"year": "2025", "quarter": "Q1", "month": "01", "department": "개발팀"},
    },
    {
        "id": "sales_2025_01_sales",
        "content": (
            "매출 기록 — 2025년 1월 영업팀\n"
            "기간: 2025-01-01 ~ 2025-01-31\n"
            "부서: 영업팀\n"
            "제품: 컨설팅 서비스\n"
            "매출액: 32,000,000원\n"
            "계약 건수: 8건\n"
            "주요 고객: D제조, E건설\n"
        ),
        "metadata": {"year": "2025", "quarter": "Q1", "month": "01", "department": "영업팀"},
    },
    {
        "id": "sales_2025_02_dev",
        "content": (
            "매출 기록 — 2025년 2월 개발팀\n"
            "기간: 2025-02-01 ~ 2025-02-28\n"
            "부서: 개발팀\n"
            "제품: 소프트웨어 라이선스 + 유지보수\n"
            "매출액: 51,000,000원\n"
            "계약 건수: 15건\n"
            "주요 고객: F금융, G보험, H통신\n"
        ),
        "metadata": {"year": "2025", "quarter": "Q1", "month": "02", "department": "개발팀"},
    },
    {
        "id": "sales_2025_02_sales",
        "content": (
            "매출 기록 — 2025년 2월 영업팀\n"
            "기간: 2025-02-01 ~ 2025-02-28\n"
            "부서: 영업팀\n"
            "제품: 컨설팅 서비스 + 교육\n"
            "매출액: 28,500,000원\n"
            "계약 건수: 7건\n"
            "주요 고객: I유통, J물류\n"
        ),
        "metadata": {"year": "2025", "quarter": "Q1", "month": "02", "department": "영업팀"},
    },
    {
        "id": "sales_2025_03_dev",
        "content": (
            "매출 기록 — 2025년 3월 개발팀\n"
            "기간: 2025-03-01 ~ 2025-03-31\n"
            "부서: 개발팀\n"
            "제품: 소프트웨어 라이선스\n"
            "매출액: 63,000,000원\n"
            "계약 건수: 18건\n"
            "주요 고객: K제약, L바이오, M에너지\n"
        ),
        "metadata": {"year": "2025", "quarter": "Q1", "month": "03", "department": "개발팀"},
    },
    {
        "id": "sales_2025_03_sales",
        "content": (
            "매출 기록 — 2025년 3월 영업팀\n"
            "기간: 2025-03-01 ~ 2025-03-31\n"
            "부서: 영업팀\n"
            "제품: 컨설팅 서비스\n"
            "매출액: 41,000,000원\n"
            "계약 건수: 11건\n"
            "주요 고객: N물산, O무역, P반도체\n"
        ),
        "metadata": {"year": "2025", "quarter": "Q1", "month": "03", "department": "영업팀"},
    },
    {
        "id": "sales_2025_q1_summary",
        "content": (
            "2025년 1분기 매출 요약 보고서\n"
            "집계 기간: 2025년 1월 ~ 3월 (Q1)\n"
            "개발팀 1분기 합계: 159,000,000원 (1월 45M + 2월 51M + 3월 63M)\n"
            "영업팀 1분기 합계: 101,500,000원 (1월 32M + 2월 28.5M + 3월 41M)\n"
            "전체 1분기 합계: 260,500,000원\n"
            "전년 동기 대비: +18.3% 성장\n"
            "목표 달성률: 104.2% (목표: 250,000,000원)\n"
        ),
        "metadata": {"year": "2025", "quarter": "Q1", "category": "요약보고서"},
    },
]

# 추론이 필요한 질문 목록
REASONING_QUESTIONS = [
    "2025년 1분기 전체 매출 합계는 얼마인가요? 부서별로도 알려주세요.",
    "1분기 중 개발팀의 월별 매출 증감 추이를 분석해 주세요.",
    "2025년 1분기 목표 달성률이 가장 높은 달은 언제인가요?",
]


# =============================================================================
# === PROCESS ===
# =============================================================================

def build_chroma_collection(
    client: chromadb.Client,
    collection_name: str,
    documents: list[dict],
) -> chromadb.Collection:
    """ChromaDB 인메모리 컬렉션에 매출 데이터 문서를 저장합니다.

    Args:
        client: ChromaDB 클라이언트 인스턴스
        collection_name: 생성할 컬렉션 이름
        documents: 저장할 문서 딕셔너리 리스트

    Returns:
        문서가 저장된 ChromaDB Collection 인스턴스
    """
    print(f"\n  [ChromaDB] 컬렉션 '{collection_name}' 생성 중...")
    print(f"  [임베딩 모델] {EMBEDDING_MODEL}")

    try:
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )  # ①
    except Exception as e:
        print(f"\n[오류] 임베딩 모델 로드에 실패했습니다: {e}")
        print("  인터넷 연결을 확인하십시오.")
        sys.exit(1)

    collection = client.create_collection(
        name=collection_name,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )  # ②

    for doc in documents:
        collection.add(
            documents=[doc["content"]],
            ids=[doc["id"]],
            metadatas=[doc["metadata"]],
        )  # ③

    print(f"  [완료] {len(documents)}개 문서 저장 완료")
    return collection


def search_relevant_documents(
    collection: chromadb.Collection,
    query: str,
    top_k: int = TOP_K,
) -> list[dict]:
    """질문과 가장 관련성 높은 문서를 검색합니다.

    Args:
        collection: 검색할 ChromaDB 컬렉션
        query: 검색 쿼리 문자열
        top_k: 반환할 최대 문서 수 (기본: 5)

    Returns:
        검색된 문서 딕셔너리 리스트
    """
    results = collection.query(
        query_texts=[query],
        n_results=min(top_k, collection.count()),  # ① 저장된 문서 수를 초과하지 않도록
    )

    retrieved = []
    for i, doc_text in enumerate(results["documents"][0]):  # ②
        retrieved.append({
            "content": doc_text,
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i],
        })
    return retrieved  # ③


def build_reasoning_prompt(retrieved_docs: list[dict], question: str) -> str:
    """추론이 필요한 질문을 위한 RAG 프롬프트를 구성합니다.

    단순 검색+답변이 아닌, 계산이나 분석이 필요한 질문을 위해
    Chain-of-Thought 방식으로 단계별 추론을 요청합니다.

    Args:
        retrieved_docs: 검색된 문서 딕셔너리 리스트
        question: 사용자 질문 문자열

    Returns:
        추론 요청이 포함된 완성된 프롬프트 문자열
    """
    context_parts = []
    for i, doc in enumerate(retrieved_docs, start=1):
        dept = doc["metadata"].get("department", "")
        month = doc["metadata"].get("month", "")
        category = doc["metadata"].get("category", "")
        label = f"문서 {i}"
        if dept and month:
            label += f" ({month}월 {dept})"
        elif category:
            label += f" ({category})"
        context_parts.append(f"[{label}]\n{doc['content'].strip()}")

    context = "\n\n".join(context_parts)

    return (
        "당신은 사내 매출 데이터를 분석하는 전문 AI 비서입니다.\n"
        "아래 제공된 사내 매출 문서를 바탕으로 질문에 정확히 답변하십시오.\n"
        "계산이 필요한 경우 단계별로 계산 과정을 명시하십시오.\n"
        "문서에 없는 정보는 추측하지 말고 '문서에서 확인할 수 없습니다.'라고 답변하십시오.\n\n"
        f"[매출 관련 문서 (상위 {len(retrieved_docs)}개)]\n{context}\n\n"
        f"[질문]\n{question}\n\n"
        "[답변 (계산 과정 포함)]"
    )


def call_ollama(prompt: str) -> str:
    """Ollama API에 HTTP 요청을 보내 LLM 응답을 받아옵니다.

    Args:
        prompt: LLM에 전달할 프롬프트 문자열

    Returns:
        LLM이 생성한 응답 문자열

    Raises:
        SystemExit: 연결 실패 또는 응답 오류 시 종료
    """
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}

    try:
        response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)  # ①
        response.raise_for_status()  # ②
    except requests.exceptions.ConnectionError:
        print("\n[오류] Ollama 서버에 연결할 수 없습니다.")
        print("  해결 방법: 터미널에서 'ollama serve' 명령을 먼저 실행하십시오.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print(f"\n[오류] Ollama 응답 시간이 초과되었습니다. (제한: {REQUEST_TIMEOUT}초)")
        print("  추론 질문은 일반 질문보다 응답 시간이 더 오래 걸릴 수 있습니다.")
        print("  더 작은 모델을 사용하거나 REQUEST_TIMEOUT을 늘리십시오.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"\n[오류] Ollama API 응답 오류: {e}")
        sys.exit(1)

    return response.json().get("response", "")  # ③


def call_openai(prompt: str) -> str:
    """OpenAI API를 호출하여 LLM 응답을 받아옵니다.

    Args:
        prompt: LLM에 전달할 프롬프트 문자열

    Returns:
        LLM이 생성한 응답 문자열

    Raises:
        SystemExit: API 키 미설정 또는 연결 오류 시 종료
    """
    if not OPENAI_API_KEY:
        print("\n[오류] OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        sys.exit(1)

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": OPENAI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,  # 계산 질문은 낮은 온도로 정확성 향상
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        print("\n[오류] OpenAI API 서버에 연결할 수 없습니다.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"\n[오류] OpenAI API 응답 오류: {e}")
        sys.exit(1)

    return response.json()["choices"][0]["message"]["content"]


def ask_llm_with_reasoning(retrieved_docs: list[dict], question: str) -> str:
    """검색된 문서를 기반으로 LLM에 추론을 포함한 답변을 요청합니다.

    Args:
        retrieved_docs: ChromaDB에서 검색된 문서 리스트
        question: 사용자 질문 문자열

    Returns:
        LLM이 생성한 추론 포함 답변 문자열
    """
    prompt = build_reasoning_prompt(retrieved_docs, question)  # ①

    if LLM_PROVIDER == "ollama":
        return call_ollama(prompt)  # ②
    elif LLM_PROVIDER == "openai":
        return call_openai(prompt)
    else:
        print(f"\n[오류] 지원하지 않는 LLM 제공자입니다: '{LLM_PROVIDER}'")
        sys.exit(1)


# =============================================================================
# === OUTPUT ===
# =============================================================================

def display_reasoning_result(
    question_num: int,
    question: str,
    retrieved_docs: list[dict],
    answer: str,
) -> None:
    """추론 질문의 RAG 결과를 포맷에 맞게 출력합니다.

    Args:
        question_num: 질문 번호
        question: 사용자 질문 문자열
        retrieved_docs: 검색된 문서 딕셔너리 리스트
        answer: LLM이 생성한 추론 포함 답변 문자열
    """
    print(f"\n{'=' * 60}")
    print(f"[추론 질문 {question_num}]")
    print(f"  {question}")
    print(f"\n[검색된 관련 문서 — 상위 {len(retrieved_docs)}개]")
    for i, doc in enumerate(retrieved_docs, start=1):
        dept = doc["metadata"].get("department", "")
        month = doc["metadata"].get("month", "")
        category = doc["metadata"].get("category", "")
        label = f"{month}월 {dept}" if dept and month else category or "문서"
        similarity = 1 - doc["distance"]
        print(f"  [{i}] {label} | 유사도: {similarity:.3f}")
    print(f"\n[LLM 추론 답변]")
    print("-" * 40)
    print(answer)
    print("-" * 40)


def main() -> None:
    """메인 실행 함수 — RAG + 추론 능력 확인 실습을 실행합니다.

    매출 데이터를 ChromaDB에 저장하고, 계산/분석이 필요한 질문을 통해
    RAG + LLM 추론 능력의 시너지를 체험합니다.
    """
    print("\n" + "=" * 60)
    print("[실습 4] RAG + 추론 능력 확인 — 매출 데이터 분석")
    print("=" * 60)
    print(f"\n[사용 모델] {LLM_PROVIDER.upper()} / {OLLAMA_MODEL if LLM_PROVIDER == 'ollama' else OPENAI_MODEL}")
    print(f"[임베딩 모델] {EMBEDDING_MODEL}")
    print(f"[데이터] 2025년 1분기 부서별 월별 매출 기록 {len(SALES_DOCUMENTS)}건")

    # 인메모리 ChromaDB 생성 및 매출 데이터 저장
    client = chromadb.Client()  # ①
    collection = build_chroma_collection(
        client, "ch03_sales_reasoning", SALES_DOCUMENTS
    )  # ②

    # 추론 질문별 RAG 실행
    for i, question in enumerate(REASONING_QUESTIONS, start=1):
        print(f"\n\n--- [추론 질문 {i}/{len(REASONING_QUESTIONS)}] LLM 답변 생성 중... ---")

        retrieved_docs = search_relevant_documents(collection, question)  # ③
        answer = ask_llm_with_reasoning(retrieved_docs, question)  # ④
        display_reasoning_result(i, question, retrieved_docs, answer)

    # 최종 정리
    print("\n" + "=" * 60)
    print("[4단계 실습 완료 — 비교 요약]")
    print()
    print("  단계 1 (LLM 단독):         사내 정보 없음 → 환각 발생")
    print("  단계 2 (Context Injection): 문서 삽입 가능, 토큰 한계 존재")
    print("  단계 3 (RAG 미리보기):      관련 문서 검색 → 정확한 답변")
    print("  단계 4 (RAG + 추론):        데이터 검색 + 계산/분석 → 심화 답변")
    print()
    print("  [다음 챕터 예고]")
    print("  CH04: FastAPI로 실제 사내 시스템(직원/휴가/매출 CRUD)을 구축합니다.")
    print("  CH06: ChromaDB를 영속화하고 PDF/DOCX 문서를 자동으로 인덱싱합니다.")


if __name__ == "__main__":
    main()
