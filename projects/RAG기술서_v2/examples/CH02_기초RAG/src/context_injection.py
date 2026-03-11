"""컨텍스트 직접 주입 모듈 — 프롬프트에 문서 삽입 (섹션 2.2).

사내 HR 규정 문서를 프롬프트에 직접 삽입하여 LLM이 정확한 답변을
생성하도록 합니다. 이 방식은 정확도를 높이지만, 문서가 많아질수록
토큰 한계와 비용 문제가 발생하는 '반쪽 성공' 방법입니다.
"""

import os
from typing import Optional

from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# --- 상수 ---
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# 하드코딩된 HR 규정 문서 컨텍스트 (실제 사내 문서 일부를 시뮬레이션)
HR_CONTEXT: str = """
[커넥트HR 인사 규정 - 연차 및 휴가 정책 v2.3]

제1조 (연차유급휴가)
1. 신입사원(근속 1년 미만)은 입사 후 매월 1일씩 월차를 부여하여 최대 11일 사용 가능합니다.
2. 근속 1년 이상 직원은 연 15일의 연차유급휴가를 부여합니다.
3. 근속 3년 이상부터는 2년마다 1일씩 추가하여 최대 25일까지 부여합니다.
4. 미사용 연차는 연말 정산 시 통상임금으로 지급합니다.

제2조 (여름 휴가 지원금)
1. 전 직원에게 여름 휴가 지원금으로 1인당 30만원을 지급합니다.
2. 지급 시기는 매년 6월 마지막 주 급여일입니다.
3. 근속 기간에 관계없이 동일 금액을 지급합니다.

제3조 (재택근무)
1. 재택근무 신청은 근무일 기준 2일 전까지 팀장에게 서면 승인을 받아야 합니다.
2. 재택근무는 월 최대 6일까지 허용됩니다.
3. 중요 회의 또는 프로젝트 마감일에는 재택근무를 사용할 수 없습니다.

[문서 번호: HR-2024-003, 작성일: 2024-01-15, 작성자: HR팀]
"""

# 컨텍스트 없을 때 사용할 질문
TEST_QUESTION: str = "커넥트HR의 연차 규정에서 신입사원 1년차 연차 일수는 몇 일입니까?"

# Mock 응답 — Ollama 미연결 시
MOCK_RESPONSE_WITHOUT_CONTEXT: str = (
    "커넥트HR의 신입사원 연차는 근로기준법에 따라 15일입니다. "
    "단, 1년차에는 월 1일씩 부여되는 월차를 포함하여 최대 11일까지 사용할 수 있습니다."
)
MOCK_RESPONSE_WITH_CONTEXT: str = (
    "제공된 커넥트HR 인사 규정(제1조)에 따르면, 신입사원(근속 1년 미만)은 "
    "입사 후 매월 1일씩 월차를 부여받아 최대 11일을 사용할 수 있습니다. "
    "근속 1년 이상이 되면 연 15일의 연차유급휴가가 부여됩니다."
)


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


def query_without_context(question: str, client: Optional[object]) -> str:
    """컨텍스트 없이 LLM에 질의합니다.

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
        return MOCK_RESPONSE_WITHOUT_CONTEXT
    try:
        return client.invoke(prompt)
    except Exception as e:
        print(f"LLM 질의 중 오류가 발생했습니다: {e}")
        return MOCK_RESPONSE_WITHOUT_CONTEXT


def query_with_context(question: str, context: str, client: Optional[object]) -> str:
    """컨텍스트를 프롬프트에 직접 삽입하여 LLM에 질의합니다.

    사내 문서 전체를 프롬프트에 포함하여 정확도를 높입니다.
    문서가 많아질수록 토큰 수가 급증하는 한계가 있습니다.

    Args:
        question: 사용자 질문 문자열
        context: 프롬프트에 삽입할 참고 문서 텍스트
        client: Ollama 클라이언트 객체. None이면 Mock 모드로 동작.

    Returns:
        LLM 또는 Mock 응답 문자열
    """
    # --- Input ---
    prompt = f"""다음 참고 문서를 바탕으로 질문에 정확하게 답하십시오.
문서에 없는 내용은 답변하지 마십시오.

[참고 문서]
{context}

[질문]
{question}

[답변]"""

    # --- Process ---
    if client is None:
        return MOCK_RESPONSE_WITH_CONTEXT
    try:
        return client.invoke(prompt)
    except Exception as e:
        print(f"LLM 질의 중 오류가 발생했습니다: {e}")
        return MOCK_RESPONSE_WITH_CONTEXT

    # --- Output ---
    # 반환값은 위에서 처리됨


def calculate_token_estimate(text: str) -> int:
    """텍스트의 예상 토큰 수를 계산합니다.

    영어 기준으로 1토큰 ≈ 4글자를 적용합니다.
    한국어는 1토큰 ≈ 2글자로 계산하므로 실제 토큰 수는 더 많을 수 있습니다.

    Args:
        text: 토큰 수를 측정할 텍스트

    Returns:
        예상 토큰 수 정수값
    """
    # --- Input ---
    char_count = len(text)

    # --- Process ---
    # 한국어 문서는 1토큰 ≈ 2글자 기준 적용
    estimated_tokens = char_count // 2

    # --- Output ---
    return estimated_tokens


def run_context_injection_demo() -> None:
    """컨텍스트 주입 비교 데모를 실행합니다.

    동일한 질문에 대해 컨텍스트 없는 응답과
    컨텍스트 있는 응답을 비교하여 출력합니다.
    """
    print("=" * 60)
    print("Step 2: 컨텍스트 직접 주입 — 반쪽 성공 체험")
    print("=" * 60)
    print(f"모델: {OLLAMA_MODEL}")
    print()

    # --- Input ---
    print("[Ollama 서버 연결 시도 중...]")
    client = create_ollama_client()

    if client is None:
        print("[Mock 모드] Ollama 미연결 — Mock 응답을 사용합니다.")
    else:
        print("[연결 성공] Ollama 서버에 정상 연결되었습니다.")
    print()

    question = TEST_QUESTION
    print(f"[테스트 질문] {question}")
    print()

    # --- Process ---
    # 1단계: 컨텍스트 없이 질의
    print("--- 시도 1: 컨텍스트 없이 직접 질의 ---")
    response_without = query_without_context(question, client)
    print(f"[응답]\n{response_without}")
    print()
    print("결과: 환각 가능성 높음 — LLM이 실제 규정을 모르기 때문에 추측합니다.")
    print()

    # 2단계: 컨텍스트 주입 후 질의
    print("--- 시도 2: HR 규정 문서를 프롬프트에 직접 삽입 ---")
    context_tokens = calculate_token_estimate(HR_CONTEXT)
    question_tokens = calculate_token_estimate(question)
    total_tokens = context_tokens + question_tokens

    print(f"[토큰 사용량 예측]")
    print(f"  - 컨텍스트 문서: 약 {context_tokens}토큰")
    print(f"  - 질문: 약 {question_tokens}토큰")
    print(f"  - 합계: 약 {total_tokens}토큰")
    print()

    response_with = query_with_context(question, HR_CONTEXT, client)
    print(f"[응답]\n{response_with}")
    print()

    # --- Output ---
    print("결과: 정확한 답변 — 하지만 토큰 비용이 발생합니다.")
    print()
    print("=" * 60)
    print("[Context Injection의 한계]")
    print("=" * 60)
    print("문제 1: 문서가 100개라면 모든 문서를 프롬프트에 넣어야 합니다.")
    print("        → 토큰 수가 수십만 개로 급증합니다.")
    print()
    print("문제 2: LLM마다 처리 가능한 최대 토큰(컨텍스트 윈도우)이 제한됩니다.")
    print("        DeepSeek R1: 약 128,000 토큰 한계")
    print()
    print("문제 3: 문서 3,000페이지를 매번 넣으면 응답 시간이 크게 늘어납니다.")
    print()
    print("[해결책] 관련 문서만 선택적으로 검색하는 RAG가 필요합니다.")
    print("         다음 단계에서 ChromaDB로 기초 RAG를 구현합니다.\n")


if __name__ == "__main__":
    run_context_injection_demo()
