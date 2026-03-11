"""
[Step 1 — 실패] LLM 단독 질의: 환각(Hallucination) 체험

이 스크립트는 사내 비공개 정보를 ChatOllama에 컨텍스트 없이
직접 질문하여, LLM 단독 사용 시 발생하는 환각(Hallucination) 현상을
직접 체험합니다.

기대 결과:
  - 사내 고유 정보(연차 규정, 매출 목표, 보안 USB 정책)에 대해
    LLM이 학습 데이터에 없는 내용을 자신 있게 지어내는 환각 현상 관찰

실행:
  python src/01_llm_only.py
"""

import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain_ollama import ChatOllama

# --- 환경 변수 로드 ---
_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)

# --- 상수 정의 ---
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "deepseek-r1:1.5b")

# 환각을 유발할 사내 정보 질문 3개
# (LLM은 '테크컴퍼니' 내부 정보를 학습한 적이 없으므로 답변 전체가 허구일 수 있음)
QUESTIONS: list[str] = [
    "우리 회사(테크컴퍼니)의 신입사원 연차 발생 규정이 어떻게 돼?",
    "2024년 4분기 마케팅팀 매출 목표는 얼마야?",
    "사내 보안 USB 정책이 어떻게 돼?",
]


def ask_llm(question: str) -> str:
    """
    ChatOllama DeepSeek R1을 단독 호출하여 응답을 반환합니다.

    사내 비공개 정보를 묻는 질문을 아무런 참고 문서 없이 LLM에 그대로 전달합니다.
    이 방식은 LLM이 학습 데이터에서 관련 정보를 '기억'해내도록 강요하며,
    학습 데이터에 없는 사내 고유 정보에 대해서는 환각이 발생합니다.

    Input  : 사내 정보를 묻는 질문 문자열
    Process: ChatOllama.invoke()로 컨텍스트 없이 질문을 전달하고 응답 추출
    Output : LLM 응답 문자열

    Args:
        question: 사내 정보를 묻는 질문 문자열

    Returns:
        LLM 응답 문자열

    Raises:
        SystemExit: Ollama 서버 연결 실패 또는 모델을 찾을 수 없는 경우
    """

    # --- Input ---
    if not question or not question.strip():
        raise ValueError("질문이 비어 있습니다. 질문 내용을 입력하십시오.")

    # --- Process ---
    try:
        llm = ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0,  # 재현 가능한 결과를 위해 고정
        )
        response = llm.invoke(question)
    except Exception as e:
        print(f"\n[오류] LLM 호출 중 오류가 발생했습니다: {e}")
        print("      Ollama가 실행 중인지 확인하십시오: ollama serve")
        print(f"      모델이 다운로드되어 있는지 확인하십시오: ollama pull {OLLAMA_MODEL}")
        sys.exit(1)

    # --- Output ---
    return response.content


def main() -> None:
    """
    환각을 유발하는 3가지 질문을 순서대로 LLM에 실행합니다.

    각 질문 후 LLM의 응답과 왜 이 응답이 신뢰할 수 없는지
    관찰 포인트 메시지를 함께 출력합니다.

    Input  : QUESTIONS 상수에 정의된 3개의 사내 정보 질문
    Process: 각 질문을 ask_llm()으로 순차 호출하고 결과 출력
    Output : 각 질문·응답·주의 메시지를 표준 출력으로 출력
    """

    # --- Input ---
    print("=" * 65)
    print("CH03 실험 1: LLM 단독 질의 — 환각(Hallucination) 체험")
    print("=" * 65)
    print(f"사용 모델  : {OLLAMA_MODEL}")
    print(f"Ollama 서버: {OLLAMA_BASE_URL}")
    print()
    print("이 실험은 컨텍스트(참고 문서) 없이 LLM에게 사내 비공개 정보를")
    print("질문하여 환각 현상을 직접 체험합니다.")
    print("LLM은 '테크컴퍼니'의 내부 정보를 학습한 적이 없으므로")
    print("어떤 응답이 나오는지 주의 깊게 관찰하십시오.\n")

    # --- Process ---
    total = len(QUESTIONS)
    for index, question in enumerate(QUESTIONS, start=1):
        print(f"\n{'=' * 65}")
        print(f"질문 {index}/{total}")
        print("=" * 65)
        print(f"질문: {question}")
        print("-" * 65)

        start_time = time.time()
        answer = ask_llm(question)
        elapsed = time.time() - start_time

        print(f"LLM 답변 ({elapsed:.1f}초):\n")
        print(answer)
        print("-" * 65)

        # 각 질문별 환각 관찰 포인트 안내
        if index == 1:
            print("\n[환각 관찰 포인트]")
            print("  '테크컴퍼니'의 연차 규정은 사내 취업규칙에만 존재합니다.")
            print("  LLM이 일반적인 근로기준법 내용으로 대체하거나,")
            print("  실제 규정과 다른 내용을 자신 있게 답변하면 환각입니다.")
        elif index == 2:
            print("\n[환각 관찰 포인트]")
            print("  '2024년 4분기 마케팅팀 매출 목표'는 사내 기밀 정보입니다.")
            print("  LLM이 이 정보에 접근한 적이 없으므로 응답 전체가 허구입니다.")
            print("  이것이 '환각(Hallucination)' — 없는 사실을 자신있게 말합니다.")
        elif index == 3:
            print("\n[환각 관찰 포인트]")
            print("  보안 USB 정책도 사내 고유 규정입니다.")
            print("  일반적인 보안 관행을 설명하거나 내용을 지어낼 수 있습니다.")

    # --- Output ---
    print("\n" + "=" * 65)
    print("실험 1 완료")
    print("=" * 65)
    print("\n[핵심 결론]")
    print("  LLM은 학습 데이터에 없는 사내 정보에 대해 신뢰할 수 없는 답변을 생성합니다.")
    print("  이것이 '환각(Hallucination)'이며, RAG가 필요한 근본 이유입니다.\n")
    print("[다음 단계]")
    print("  python src/02_context_injection.py")
    print("  → 문서를 프롬프트에 직접 삽입하면 어떻게 달라지는지 확인합니다.\n")


if __name__ == "__main__":
    main()
