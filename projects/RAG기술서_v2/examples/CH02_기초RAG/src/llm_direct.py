"""LLM 단독 질의 모듈 — Ollama + DeepSeek R1 직접 질의 (섹션 2.1).

Ollama 서버에 연결하여 사내 규정 관련 질문을 직접 전송합니다.
학습 데이터에 없는 사내 규정에 대해 LLM이 환각 응답을 생성하는
현상을 재현하고, 이를 통해 RAG 도입 필요성을 체감합니다.
"""

import os
import sys
from typing import Optional

from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# --- 상수 ---
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# 환각을 유도하는 질문 목록 (사내 규정이므로 LLM 학습 데이터에 없음)
HALLUCINATION_QUESTIONS: list[str] = [
    "커넥트HR의 연차 규정에서 신입사원 1년차 연차 일수는 몇 일입니까?",
    "커넥트HR 직원의 여름 휴가 지원금은 얼마입니까?",
    "커넥트HR에서 재택근무 신청은 며칠 전에 해야 합니까?",
]

# Mock 응답 — Ollama 미연결 시 환각 패턴 시뮬레이션
MOCK_HALLUCINATION_RESPONSES: list[str] = [
    "커넥트HR의 신입사원 연차는 근로기준법에 따라 15일입니다. 단, 1년차에는 월 1일씩 부여되는 월차를 포함하여 최대 11일까지 사용할 수 있습니다.",
    "커넥트HR 직원의 여름 휴가 지원금은 1인당 50만원이며, 7월 중 지급됩니다. 단, 3년 이상 근속자는 70만원을 받을 수 있습니다.",
    "커넥트HR의 재택근무 신청은 최소 3일 전에 팀장 승인을 받아야 하며, 월 최대 8일까지 허용됩니다.",
]


def create_ollama_client() -> Optional[object]:
    """Ollama 클라이언트를 생성합니다.

    Returns:
        Ollama 클라이언트 객체. 연결 실패 시 None 반환.
    """
    try:
        from langchain_ollama import OllamaLLM

        client = OllamaLLM(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
        # 간단한 연결 테스트
        client.invoke("안녕")
        return client
    except Exception:
        return None


def query_llm_directly(question: str, client: Optional[object]) -> str:
    """LLM에 컨텍스트 없이 직접 질의합니다.

    사내 규정처럼 학습 데이터에 없는 정보를 질문하여
    LLM이 환각 응답을 생성하는 현상을 재현합니다.

    Args:
        question: 사용자 질문 문자열
        client: Ollama 클라이언트 객체. None이면 Mock 모드로 동작.

    Returns:
        LLM 또는 Mock 응답 문자열
    """
    # --- Input ---
    prompt = f"""다음 질문에 답하십시오.

질문: {question}

답변:"""

    # --- Process ---
    if client is None:
        # Mock 모드: 질문 인덱스에 따라 환각 패턴 응답 반환
        question_index = HALLUCINATION_QUESTIONS.index(question) if question in HALLUCINATION_QUESTIONS else 0
        response = MOCK_HALLUCINATION_RESPONSES[question_index % len(MOCK_HALLUCINATION_RESPONSES)]
    else:
        try:
            response = client.invoke(prompt)
        except Exception as e:
            print(f"LLM 질의 중 오류가 발생했습니다: {e}")
            response = MOCK_HALLUCINATION_RESPONSES[0]

    # --- Output ---
    return response


def run_llm_only_demo() -> None:
    """LLM 단독 질의 데모를 실행합니다.

    세 가지 사내 규정 질문을 LLM에 직접 질의하고,
    각 응답 후 환각 가능성 경고를 출력합니다.
    """
    print("=" * 60)
    print("Step 1: LLM 단독 질의 — 환각(Hallucination) 체험")
    print("=" * 60)
    print(f"모델: {OLLAMA_MODEL}")
    print(f"서버: {OLLAMA_BASE_URL}")
    print()

    # --- Input ---
    print("[Ollama 서버 연결 시도 중...]")
    client = create_ollama_client()

    if client is None:
        print("[Mock 모드] Ollama 서버에 연결할 수 없습니다.")
        print("  실제 Ollama 실행 방법: ollama serve && ollama pull deepseek-r1")
        print("  현재는 환각 패턴을 시뮬레이션하는 Mock 응답을 사용합니다.")
    else:
        print("[연결 성공] Ollama 서버에 정상 연결되었습니다.")
    print()

    # --- Process ---
    for i, question in enumerate(HALLUCINATION_QUESTIONS, start=1):
        print(f"[질문 {i}] {question}")
        print("-" * 40)

        response = query_llm_directly(question, client)

        print(f"[LLM 응답]\n{response}")
        print()

        # --- Output ---
        print("경고: 이 답변은 정확하지 않을 수 있습니다.")
        print("      LLM은 사내 규정을 학습한 적이 없으므로,")
        print("      유사한 패턴으로 추측한 내용을 사실처럼 답변합니다.")
        print("      이것이 바로 '환각(Hallucination)'입니다.")
        print("=" * 60)
        print()

    print("[결론] LLM 단독 질의만으로는 사내 규정을 정확히 알 수 없습니다.")
    print("       다음 단계에서 컨텍스트를 직접 주입해 보겠습니다.\n")


if __name__ == "__main__":
    run_llm_only_demo()
