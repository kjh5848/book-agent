"""DeepSeek R1 추론 모드 데모 모듈 (섹션 2.4).

DeepSeek R1 모델은 답변 전에 사고 과정을 <think>...</think> 태그로
출력하는 추론 토큰(Reasoning Token) 특성을 가집니다.
단순 답변 모드와 추론 모드를 비교하여 그 차이를 시각적으로 보여줍니다.
"""

import os
import re
from typing import Optional

from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# --- 상수 ---
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# 추론 능력을 테스트하는 질문
REASONING_QUESTION = (
    "우리 팀에 5명의 신입사원이 있습니다. "
    "이 중 2명은 3월 입사, 3명은 6월 입사입니다. "
    "커넥트HR 규정에 따르면 신입사원은 입사 후 매월 1일씩 월차를 받습니다. "
    "12월 31일 기준으로 각 그룹의 총 월차 일수는 얼마이며, "
    "이 규정이 공정한지 분석해 주십시오."
)

# 단순 답변 프롬프트
SIMPLE_PROMPT_TEMPLATE = """다음 질문에 간결하게 답하십시오.

질문: {question}

답변 (계산 과정 없이 결론만):"""

# 추론 유도 프롬프트
REASONING_PROMPT_TEMPLATE = """다음 질문에 단계별로 추론하면서 답하십시오.
먼저 문제를 분석하고, 계산 과정을 보여준 후 결론을 내리십시오.

질문: {question}

단계별 추론:"""

# Mock 응답 — Ollama 미연결 시
MOCK_SIMPLE_RESPONSE = "3월 입사 2명: 20일, 6월 입사 3명: 21일입니다."

MOCK_REASONING_RESPONSE = """<think>
문제를 분석해 보겠습니다.

3월 입사 직원 (2명):
- 3월부터 12월까지는 10개월
- 월 1일씩 → 1인당 10일
- 2명 합계: 20일

6월 입사 직원 (3명):
- 6월부터 12월까지는 7개월
- 월 1일씩 → 1인당 7일
- 3명 합계: 21일

공정성 분석:
- 입사 시기에 따라 연내 사용 가능한 월차 일수가 다르다.
- 3월 입사자는 10일, 6월 입사자는 7일을 받는다.
- 이는 근무 기간에 비례한 부여 방식으로 합리적이다.
- 그러나 연말 채용이 많으면 신입사원이 연내 거의 휴가를 쓸 수 없는 문제가 생긴다.
</think>

[단계별 계산]

1단계: 3월 입사 직원 (2명)
   - 3월 ~ 12월 = 10개월 근무
   - 1인당 월차: 10일
   - 2명 합계: 10일 × 2명 = **20일**

2단계: 6월 입사 직원 (3명)
   - 6월 ~ 12월 = 7개월 근무
   - 1인당 월차: 7일
   - 3명 합계: 7일 × 3명 = **21일**

[공정성 분석]
이 규정은 근무 기간에 비례하여 월차를 부여하므로 기본적으로 공정합니다.
다만, 하반기 신입사원은 연내 활용 가능한 휴가가 적어 실질적 혜택이 줄어드는
구조적 문제가 있습니다. 개선 방안으로 연차를 이월하거나 다음 해 연차에 미리
부여하는 방식을 고려할 수 있습니다."""


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


def extract_thinking_and_answer(response: str) -> tuple[str, str]:
    """DeepSeek R1의 응답에서 추론 과정과 최종 답변을 분리합니다.

    DeepSeek R1은 <think>...</think> 태그 사이에 사고 과정을 출력합니다.
    이 함수는 태그를 파싱하여 추론 과정과 실제 답변을 분리합니다.

    Args:
        response: DeepSeek R1이 생성한 전체 응답 문자열

    Returns:
        (추론 과정 문자열, 최종 답변 문자열) 튜플.
        <think> 태그가 없으면 추론 과정은 빈 문자열로 반환.
    """
    # --- Input ---
    think_pattern = re.compile(r"<think>(.*?)</think>", re.DOTALL)
    match = think_pattern.search(response)

    # --- Process ---
    if match:
        thinking = match.group(1).strip()
        answer = response[match.end():].strip()
    else:
        thinking = ""
        answer = response.strip()

    # --- Output ---
    return thinking, answer


def query_simple_mode(question: str, client: Optional[object]) -> str:
    """단순 답변 모드로 LLM에 질의합니다.

    추론 과정 없이 결론만 요청하는 프롬프트를 사용합니다.

    Args:
        question: 사용자 질문 문자열
        client: Ollama 클라이언트 객체. None이면 Mock 응답 반환.

    Returns:
        LLM 또는 Mock 응답 문자열
    """
    # --- Input ---
    prompt = SIMPLE_PROMPT_TEMPLATE.format(question=question)

    # --- Process ---
    if client is None:
        return MOCK_SIMPLE_RESPONSE
    try:
        return client.invoke(prompt)
    except Exception as e:
        print(f"LLM 질의 중 오류가 발생했습니다: {e}")
        return MOCK_SIMPLE_RESPONSE

    # --- Output ---
    # 반환값은 위에서 처리됨


def query_reasoning_mode(question: str, client: Optional[object]) -> str:
    """추론 모드로 LLM에 질의합니다.

    단계별 사고 과정을 유도하는 프롬프트를 사용합니다.
    DeepSeek R1은 자동으로 <think> 태그를 포함한 응답을 생성합니다.

    Args:
        question: 사용자 질문 문자열
        client: Ollama 클라이언트 객체. None이면 Mock 응답 반환.

    Returns:
        LLM 또는 Mock 응답 문자열
    """
    # --- Input ---
    prompt = REASONING_PROMPT_TEMPLATE.format(question=question)

    # --- Process ---
    if client is None:
        return MOCK_REASONING_RESPONSE
    try:
        return client.invoke(prompt)
    except Exception as e:
        print(f"LLM 추론 질의 중 오류가 발생했습니다: {e}")
        return MOCK_REASONING_RESPONSE

    # --- Output ---
    # 반환값은 위에서 처리됨


def run_reasoning_demo() -> None:
    """DeepSeek R1 추론 모드 비교 데모를 실행합니다.

    단순 답변 모드와 추론(Reasoning) 모드를 비교하여
    DeepSeek R1의 추론 토큰 특성을 시각적으로 보여줍니다.
    """
    print("=" * 60)
    print("Step 4: DeepSeek R1 추론(Reasoning) 모드 활용")
    print("=" * 60)
    print(f"모델: {OLLAMA_MODEL}")
    print()
    print("DeepSeek R1은 답변 전에 <think>...</think> 태그로")
    print("사고 과정(Chain of Thought)을 출력하는 특성이 있습니다.")
    print()

    # --- Input ---
    print("[Ollama 서버 연결 시도 중...]")
    client = create_ollama_client()

    if client is None:
        print("[Mock 모드] Ollama 미연결 — Mock 응답 사용")
    else:
        print("[연결 성공] Ollama 서버 연결됨")
    print()

    print(f"[테스트 질문]\n{REASONING_QUESTION}")
    print()

    # --- Process ---
    # 1단계: 단순 모드
    print("--- 비교 1: 단순 답변 모드 ---")
    simple_response = query_simple_mode(REASONING_QUESTION, client)
    print(f"[응답]\n{simple_response}")
    print()
    print("단점: 계산 근거가 없어 오류 여부를 확인하기 어렵습니다.")
    print()

    # 2단계: 추론 모드
    print("--- 비교 2: DeepSeek R1 추론 모드 ---")
    reasoning_response = query_reasoning_mode(REASONING_QUESTION, client)

    # 추론 과정과 답변 분리
    thinking, final_answer = extract_thinking_and_answer(reasoning_response)

    if thinking:
        print("[추론 과정 (Reasoning Tokens)]")
        print("-" * 40)
        # 추론 과정이 길 경우 처음 300자만 미리보기
        preview = thinking[:300] + ("..." if len(thinking) > 300 else "")
        print(preview)
        print("-" * 40)
        print()

    print("[최종 답변 (사고 과정 제거 후)]")
    print(final_answer)
    print()

    # --- Output ---
    print("=" * 60)
    print("[DeepSeek R1 추론 토큰의 장점]")
    print("=" * 60)
    print("1. 계산 과정을 볼 수 있어 오류를 쉽게 발견할 수 있습니다.")
    print("2. 복잡한 논리 추론에서 일반 LLM보다 정확도가 높습니다.")
    print("3. <think> 태그를 파싱하여 사고 과정만 별도 저장할 수 있습니다.")
    print()
    print("[RAG + 추론 모드 조합]")
    print("RAG로 정확한 문서를 검색하고, DeepSeek R1의 추론 능력으로")
    print("복잡한 규정 해석과 계산 문제를 해결할 수 있습니다.")
    print("=" * 60)
    print()


if __name__ == "__main__":
    run_reasoning_demo()
