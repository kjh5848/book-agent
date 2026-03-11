"""
CH06 터미널 RAG 쿼리 스크립트.

ChromaDB에 저장된 벡터를 검색하고 Ollama LLM으로 답변을 생성합니다.
main.py로 벡터 저장 후 이 스크립트로 질의응답을 실습할 수 있습니다.

실행:
    python scripts/query.py "연차 신청은 어떻게 하나요?"
    python scripts/query.py "보안 USB 분실" --dept HR
    python scripts/query.py "교육비 한도" --top-k 5
    python scripts/query.py "연차 신청" --no-llm

사전 준비:
    Ollama 서버가 실행 중이어야 합니다 (ollama serve).
    main.py 실행으로 ChromaDB가 먼저 생성되어 있어야 합니다.
"""

import argparse
import os
import sys

import requests
from dotenv import load_dotenv

# 프로젝트 루트(scripts/의 상위)를 Python 경로에 추가 — src 모듈 접근
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.embedder import embed_single  # noqa: E402
from src.store import create_collection, get_client, search  # noqa: E402

load_dotenv()

_OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
_CHAT_MODEL: str = os.getenv("CHAT_MODEL", "deepseek-r1:1.5b")


def chat_with_context(question: str, context_chunks: list[dict]) -> str:
    """검색된 청크를 컨텍스트로 Ollama /api/chat을 호출하여 답변을 생성합니다.

    검색 결과를 시스템 프롬프트에 포함하여 LLM이 문서 기반으로만 답변하도록 유도합니다.
    LangChain 없이 requests로 /api/chat을 직접 호출하는 방식입니다.

    Args:
        question: 사용자 질문 문자열.
        context_chunks: search()가 반환한 청크 딕셔너리 리스트.
                        각 요소는 {text, metadata, distance} 구조여야 합니다.

    Returns:
        LLM이 생성한 답변 문자열.

    Raises:
        ConnectionError: Ollama 서버에 연결할 수 없을 때.
        RuntimeError: Ollama API가 오류 응답을 반환했을 때.
    """
    # --- Input ---
    context_parts = []
    for i, chunk in enumerate(context_chunks, 1):
        source = chunk["metadata"].get("source", "unknown")
        dept = chunk["metadata"].get("department", "")
        context_parts.append(f"[출처 {i}] {source} (부서: {dept})\n{chunk['text']}")
    context_text = "\n\n".join(context_parts)

    # --- Process ---
    system_prompt = (
        "당신은 사내 문서를 기반으로 질문에 답하는 어시스턴트입니다. "
        "제공된 문서 내용만을 근거로 한국어로 답변하십시오. "
        "문서에 없는 내용은 '문서에서 확인할 수 없습니다'라고 답하십시오."
    )
    user_prompt = (
        f"다음 문서를 참고하여 질문에 답하십시오.\n\n"
        f"{context_text}\n\n"
        f"질문: {question}"
    )

    url = f"{_OLLAMA_BASE_URL}/api/chat"
    payload = {
        "model": _CHAT_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            f"Ollama 서버({_OLLAMA_BASE_URL})에 연결할 수 없습니다.\n"
            "다음 명령으로 서버를 먼저 실행하십시오:\n"
            "  ollama serve"
        )
    except requests.exceptions.Timeout:
        raise RuntimeError(
            "Ollama 서버 응답 시간이 초과되었습니다. "
            "서버 상태를 확인하거나 잠시 후 다시 시도하십시오."
        )

    if response.status_code != 200:
        raise RuntimeError(
            f"Ollama API 오류 (상태 코드: {response.status_code}): {response.text}"
        )

    result = response.json()
    answer = result.get("message", {}).get("content", "")
    if not answer:
        raise RuntimeError(
            f"Ollama API 응답에서 답변을 추출할 수 없습니다.\n응답: {result}"
        )

    # --- Output ---
    return answer.strip()


def main() -> None:
    """터미널 RAG 쿼리 메인 함수.

    argparse로 질문과 옵션을 받아 아래 순서로 실행합니다:
        [1/3] 질문 임베딩  — Ollama /api/embeddings 직접 호출
        [2/3] 벡터 검색   — ChromaDB 코사인 유사도 검색
        [3/3] LLM 답변    — Ollama /api/chat 직접 호출 (--no-llm 시 생략)

    Returns:
        None.
    """
    # --- Input ---
    parser = argparse.ArgumentParser(
        description="CH06 터미널 RAG 쿼리 — ChromaDB 검색 + Ollama LLM 답변",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "실행 예시:\n"
            "  python scripts/query.py '연차 신청은 어떻게 하나요?'\n"
            "  python scripts/query.py '보안 USB 분실' --dept HR\n"
            "  python scripts/query.py '교육비 한도' --top-k 5\n"
            "  python scripts/query.py '연차 신청' --no-llm\n"
        ),
    )
    parser.add_argument("question", help="질문 텍스트")
    parser.add_argument(
        "--dept",
        default=None,
        metavar="DEPT",
        help="부서 필터 (예: HR, FIN). 지정하지 않으면 전체 검색.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        metavar="K",
        help="검색 결과 수 (기본값: 3)",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="LLM 답변 없이 검색 결과만 출력합니다.",
    )
    args = parser.parse_args()

    print("=" * 65)
    print("  CH06 터미널 RAG 쿼리")
    print("=" * 65)
    print(f"\n  질문: {args.question}")
    if args.dept:
        print(f"  부서 필터: {args.dept}")
    print(f"  검색 수: {args.top_k}")
    if args.no_llm:
        print("  모드: 검색 전용 (--no-llm)")
    print()

    # --- Process ---
    # 1. ChromaDB 연결
    persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./outputs/chroma_db")
    if not os.path.isabs(persist_dir):
        persist_dir = os.path.join(_PROJECT_ROOT, persist_dir.lstrip("./"))

    collection_name = os.getenv("COLLECTION_NAME", "rag_docs")

    try:
        client = get_client(persist_dir=persist_dir)
        collection = create_collection(client, name=collection_name)
    except RuntimeError as e:
        print(f"[오류] ChromaDB 연결 실패: {e}")
        print("main.py를 먼저 실행하여 벡터 DB를 생성하십시오.")
        sys.exit(1)

    if collection.count() == 0:
        print("[오류] ChromaDB에 저장된 문서가 없습니다.")
        print("main.py를 먼저 실행하여 벡터 DB를 생성하십시오.")
        sys.exit(1)

    # 2. 질문 임베딩
    print("[1/3] 질문 임베딩 중...")
    try:
        query_embedding = embed_single(args.question)
    except ConnectionError as e:
        print(f"\n[오류] {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"\n[오류] 임베딩 실패: {e}")
        sys.exit(1)

    # 3. 벡터 검색
    print("[2/3] 관련 문서 검색 중...")
    results = search(
        collection,
        query_embedding=query_embedding,
        k=args.top_k,
        filter_dept=args.dept,
    )

    if not results:
        print("\n관련 문서를 찾을 수 없습니다.")
        if args.dept:
            print(
                f"(부서 필터 '{args.dept}'로 검색했습니다. "
                "다른 부서를 시도하거나 필터를 제거하십시오.)"
            )
        sys.exit(0)

    # 검색 결과 출력
    print(f"\n[검색 결과 — {len(results)}개]")
    print("-" * 65)
    for i, res in enumerate(results, 1):
        source = res["metadata"].get("source", "unknown")
        dept = res["metadata"].get("department", "")
        page = res["metadata"].get("page", "")
        dist = res["distance"]
        preview = res["text"][:80].replace("\n", " ")
        page_info = f" | p.{page}" if page else ""
        print(f"  [{i}] 거리={dist:.4f} | {source}{page_info} | 부서={dept}")
        print(f"       {preview}...")
        print()

    if args.no_llm:
        print("(--no-llm 플래그: LLM 답변 생략)")
        sys.exit(0)

    # 4. LLM 답변 생성
    print(f"[3/3] LLM 답변 생성 중... (모델: {_CHAT_MODEL})")
    print("      (처음 실행 시 모델 로딩으로 수십 초가 소요될 수 있습니다)\n")

    try:
        answer = chat_with_context(args.question, results)
    except ConnectionError as e:
        print(f"\n[오류] {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"\n[오류] LLM 답변 생성 실패: {e}")
        sys.exit(1)

    # --- Output ---
    print("=" * 65)
    print("  답변")
    print("=" * 65)
    print(answer)
    print()
    print("[참고 문서]")
    for i, res in enumerate(results, 1):
        source = res["metadata"].get("source", "unknown")
        dept = res["metadata"].get("department", "")
        page = res["metadata"].get("page", "")
        page_info = f" p.{page}" if page else ""
        print(f"  [{i}] {source}{page_info} (부서: {dept})")
    print()


if __name__ == "__main__":
    main()
