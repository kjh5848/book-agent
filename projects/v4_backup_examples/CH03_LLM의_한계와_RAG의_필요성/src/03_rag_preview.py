"""
03_rag_preview.py — RAG 미리보기 (인메모리 ChromaDB + 한국어 임베딩)

인메모리 ChromaDB에 샘플 문서를 저장하고, 질문과 관련된 문서만 검색하여
LLM에 전달함으로써 RAG(Retrieval-Augmented Generation)의 효과를 체험합니다.

이 실습의 핵심:
    - 전체 문서를 프롬프트에 넣지 않고, 관련 문서만 검색하여 삽입
    - 청킹(Chunking) 유무에 따른 검색 품질 차이 비교
    - 인메모리 DB 사용 → 실행 종료 시 데이터 사라짐 (6장에서 영속화)

실행 방법:
    python src/03_rag_preview.py

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
CHUNK_SIZE = 300  # 청킹 크기 (글자 수)
CHUNK_OVERLAP = 50  # 청크 간 중첩 글자 수
TOP_K = 3  # 검색 결과 상위 K개
REQUEST_TIMEOUT = 120  # 초


# =============================================================================
# === INPUT ===
# =============================================================================

# 샘플 사내 문서 — 여러 종류의 정보가 혼재된 긴 문서
SAMPLE_DOCUMENTS = [
    {
        "id": "doc_leave_001",
        "content": (
            "인사팀 직원 연차 현황 (2025년 기준)\n"
            "김철수 사원: 부서=개발팀, 입사일=2021-03-15, 연차총일수=15일, 사용연차=9일, 남은연차=6일\n"
            "이영희 대리: 부서=마케팅팀, 입사일=2019-07-01, 연차총일수=15일, 사용연차=12일, 남은연차=3일\n"
            "박민수 사원: 부서=영업팀, 입사일=2023-01-10, 연차총일수=11일, 사용연차=5일, 남은연차=6일\n"
            "최지영 과장: 부서=기획팀, 입사일=2017-05-20, 연차총일수=15일, 사용연차=7일, 남은연차=8일\n"
        ),
        "metadata": {"source": "인사팀", "category": "연차현황", "year": "2025"},
    },
    {
        "id": "doc_policy_001",
        "content": (
            "취업규칙 제15조 — 연차 유급휴가 규정\n"
            "1. 1년 이상 근속 직원에게는 15일의 연차 유급휴가를 부여한다.\n"
            "2. 1년 미만 근속 직원에게는 매월 개근 시 1일의 월차를 부여한다.\n"
            "3. 연차는 당해 연도 12월 31일까지 사용하여야 하며, 미사용 연차는 수당으로 지급한다.\n"
            "4. 연차 신청은 사용 예정일 3일 전 팀장 승인이 필요하다.\n"
        ),
        "metadata": {"source": "취업규칙", "category": "휴가정책", "year": "2024"},
    },
    {
        "id": "doc_it_001",
        "content": (
            "IT팀 사내 시스템 사용 가이드 (v2.3)\n"
            "사내 포털 접속: https://hr.company.internal (VPN 필수)\n"
            "연차 신청: 포털 → 근태관리 → 연차신청 → 날짜 선택 → 팀장 결재\n"
            "급여명세서 조회: 포털 → 급여관리 → 명세서조회 (매월 25일 업데이트)\n"
            "비밀번호 분실 시: IT 헬프데스크 내선 1234 또는 it-help@company.com\n"
            "보안 정책: 외부 USB 사용 금지, 개인 이메일 업무 활용 금지, 화면보호기 5분 설정 필수\n"
        ),
        "metadata": {"source": "IT팀", "category": "시스템가이드", "version": "2.3"},
    },
    {
        "id": "doc_onboard_001",
        "content": (
            "신입사원 온보딩 가이드\n"
            "첫날 준비물: 신분증, 통장사본, 주민등록등본\n"
            "노트북 수령: 입사 첫날 IT팀 방문 (3층 IT실)\n"
            "사내 교육: 입사 후 1주일간 필수 온보딩 교육 이수\n"
            "멘토 배정: 팀장이 멘토를 지정하며 3개월간 업무 지원\n"
            "시용기간: 입사 후 3개월 (취업규칙 제3조)\n"
        ),
        "metadata": {"source": "인사팀", "category": "온보딩", "year": "2025"},
    },
]

QUESTION = "김철수 사원의 남은 연차는 며칠인가요?"


# =============================================================================
# === PROCESS ===
# =============================================================================

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """긴 텍스트를 지정된 크기의 청크로 분할합니다.

    슬라이딩 윈도우 방식으로 청크 간 중첩(overlap)을 두어
    문장이 청크 경계에서 잘리는 문제를 완화합니다.

    Args:
        text: 분할할 원본 텍스트 문자열
        chunk_size: 각 청크의 최대 글자 수 (기본: 300)
        overlap: 인접 청크 간 중첩 글자 수 (기본: 50)

    Returns:
        분할된 청크 문자열의 리스트
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size  # ①
        chunk = text[start:end]  # ②
        chunks.append(chunk)
        start += chunk_size - overlap  # ③ 중첩 적용
    return chunks


def build_chroma_collection(
    client: chromadb.Client,
    collection_name: str,
    documents: list[dict],
    use_chunking: bool = True,
) -> chromadb.Collection:
    """ChromaDB 인메모리 컬렉션에 샘플 문서를 저장합니다.

    한국어 임베딩 모델(ko-sroberta-multitask)을 사용하여 문서를 벡터로 변환하고
    ChromaDB에 저장합니다.

    Args:
        client: ChromaDB 클라이언트 인스턴스
        collection_name: 생성할 컬렉션 이름
        documents: 저장할 문서 딕셔너리 리스트 (id, content, metadata 키 포함)
        use_chunking: True이면 청킹 적용, False이면 전체 문서를 하나의 단위로 저장

    Returns:
        문서가 저장된 ChromaDB Collection 인스턴스
    """
    print(f"\n  [ChromaDB] 컬렉션 '{collection_name}' 생성 중...")
    print(f"  [임베딩 모델] {EMBEDDING_MODEL} (최초 실행 시 다운로드 ~400MB)")

    # 한국어 임베딩 함수 설정
    try:
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )  # ①
    except Exception as e:
        print(f"\n[오류] 임베딩 모델 로드에 실패했습니다: {e}")
        print("  인터넷 연결을 확인하거나, 모델이 이미 캐시되어 있는지 확인하십시오.")
        sys.exit(1)

    collection = client.create_collection(
        name=collection_name,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )  # ②

    # 문서를 컬렉션에 추가
    total_chunks = 0
    for doc in documents:
        if use_chunking:
            chunks = chunk_text(doc["content"])  # ③
        else:
            chunks = [doc["content"]]  # 청킹 없이 전체를 하나로

        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc['id']}_chunk_{i}" if use_chunking else doc["id"]
            collection.add(
                documents=[chunk],
                ids=[chunk_id],
                metadatas=[doc["metadata"]],
            )  # ④
            total_chunks += 1

    mode_label = f"{CHUNK_SIZE}자 청킹" if use_chunking else "청킹 없음(전체 문서)"
    print(f"  [완료] {len(documents)}개 문서 → {total_chunks}개 청크 저장 ({mode_label})")
    return collection


def search_documents(
    collection: chromadb.Collection,
    query: str,
    top_k: int = TOP_K,
) -> list[dict]:
    """질문과 가장 유사한 문서 청크를 ChromaDB에서 검색합니다.

    코사인 유사도 기반으로 상위 K개의 관련 문서를 반환합니다.

    Args:
        collection: 검색할 ChromaDB 컬렉션
        query: 검색 쿼리 문자열
        top_k: 반환할 상위 결과 수 (기본: 3)

    Returns:
        검색된 문서 딕셔너리 리스트 (content, metadata, distance 키 포함)
    """
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
    )  # ①

    retrieved = []
    for i, doc_text in enumerate(results["documents"][0]):  # ②
        retrieved.append({
            "content": doc_text,
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i],
        })
    return retrieved  # ③


def build_rag_prompt(retrieved_docs: list[dict], question: str) -> str:
    """검색된 문서를 컨텍스트로 포함한 RAG 프롬프트를 구성합니다.

    Args:
        retrieved_docs: 검색된 문서 딕셔너리 리스트
        question: 사용자 질문 문자열

    Returns:
        RAG 방식으로 구성된 완성된 프롬프트 문자열
    """
    context_parts = []
    for i, doc in enumerate(retrieved_docs, start=1):
        source = doc["metadata"].get("source", "출처 불명")
        context_parts.append(f"[문서 {i} — 출처: {source}]\n{doc['content']}")

    context = "\n\n".join(context_parts)

    return (
        "당신은 사내 인사 정보에 정통한 AI 비서입니다.\n"
        "아래 검색된 사내 문서만을 참고하여 질문에 답변하십시오.\n"
        "문서에 없는 내용은 '관련 문서에서 확인할 수 없습니다.'라고 답변하십시오.\n\n"
        f"[검색된 관련 문서 (상위 {len(retrieved_docs)}개)]\n{context}\n\n"
        f"[질문]\n{question}\n\n"
        "[답변]"
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
        "temperature": 0.3,
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


def ask_llm_with_rag(retrieved_docs: list[dict], question: str) -> str:
    """검색된 문서를 컨텍스트로 포함하여 LLM에 질문합니다.

    Args:
        retrieved_docs: ChromaDB에서 검색된 문서 리스트
        question: 사용자 질문 문자열

    Returns:
        LLM이 생성한 답변 문자열
    """
    prompt = build_rag_prompt(retrieved_docs, question)  # ①

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

def display_rag_result(
    mode_label: str,
    question: str,
    retrieved_docs: list[dict],
    answer: str,
) -> None:
    """RAG 검색 결과와 LLM 응답을 포맷에 맞게 출력합니다.

    Args:
        mode_label: 실험 모드 레이블 (예: '청킹 없음', '500자 청킹')
        question: 사용자 질문 문자열
        retrieved_docs: 검색된 문서 딕셔너리 리스트
        answer: LLM이 생성한 답변 문자열
    """
    print(f"\n{'=' * 60}")
    print(f"[RAG 실험] {mode_label}")
    print(f"{'=' * 60}")
    print(f"\n[질문] {question}")
    print(f"\n[검색된 관련 문서 — 상위 {len(retrieved_docs)}개]")
    for i, doc in enumerate(retrieved_docs, start=1):
        source = doc["metadata"].get("source", "출처 불명")
        similarity = 1 - doc["distance"]  # 코사인 유사도 (1 - 거리)
        print(f"  [{i}] 출처: {source} | 유사도: {similarity:.3f}")
        print(f"      내용 미리보기: {doc['content'][:80].strip()}...")
    print(f"\n[LLM 답변]")
    print("-" * 40)
    print(answer)
    print("-" * 40)


def run_rag_experiment(use_chunking: bool) -> None:
    """RAG 실험을 실행합니다 — 청킹 유무에 따른 비교.

    인메모리 ChromaDB를 생성하고 샘플 문서를 저장한 뒤,
    질문과 관련된 문서를 검색하여 LLM에 전달합니다.

    Args:
        use_chunking: True이면 청킹 적용, False이면 전체 문서 저장
    """
    mode_label = f"{CHUNK_SIZE}자 청킹 적용" if use_chunking else "청킹 없음 (전체 문서)"

    # 인메모리 ChromaDB 클라이언트 생성 (실행 종료 시 데이터 사라짐)
    client = chromadb.Client()  # ①
    collection_name = "ch03_rag_chunked" if use_chunking else "ch03_rag_no_chunk"

    # 문서 저장
    collection = build_chroma_collection(
        client, collection_name, SAMPLE_DOCUMENTS, use_chunking=use_chunking
    )  # ②

    # 질문 관련 문서 검색
    retrieved_docs = search_documents(collection, QUESTION)  # ③

    # LLM으로 답변 생성
    print(f"  [LLM] 답변 생성 중...")
    answer = ask_llm_with_rag(retrieved_docs, QUESTION)  # ④

    display_rag_result(mode_label, QUESTION, retrieved_docs, answer)


def main() -> None:
    """메인 실행 함수 — RAG 미리보기 실습을 실행합니다.

    청킹 없이 전체 문서를 저장한 경우와 청킹을 적용한 경우를 비교합니다.
    """
    print("\n" + "=" * 60)
    print("[실습 3] RAG 미리보기 — 인메모리 ChromaDB 검색+답변")
    print("=" * 60)
    print(f"\n[사용 모델] {LLM_PROVIDER.upper()} / {OLLAMA_MODEL if LLM_PROVIDER == 'ollama' else OPENAI_MODEL}")
    print(f"[임베딩 모델] {EMBEDDING_MODEL}")
    print(f"[데이터베이스] ChromaDB 인메모리 (실행 종료 시 데이터 소멸)")

    # 실험 1: 청킹 없음
    run_rag_experiment(use_chunking=False)

    # 실험 2: 청킹 적용
    run_rag_experiment(use_chunking=True)

    # 비교 분석
    print("\n" + "=" * 60)
    print("[비교 분석]")
    print(f"  청킹 없음: 문서 전체가 하나의 벡터 → 검색 정밀도 낮음")
    print(f"  {CHUNK_SIZE}자 청킹: 작은 단위로 분할 → 관련 부분만 정확히 검색")
    print()
    print("  [핵심 차이]")
    print("  - Context Injection: 모든 문서를 프롬프트에 삽입 → 토큰 폭발")
    print("  - RAG: 관련 문서만 선택하여 삽입 → 효율적, 확장 가능")
    print()
    print("  다음 실습: python src/04_rag_reasoning.py")


if __name__ == "__main__":
    main()
