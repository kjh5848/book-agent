"""
01_llm_only.py — LLM 단독 질의 (환각 체험)

LLM에 사내 정보를 직접 질문하여 환각(Hallucination) 응답을 체험합니다.
사전 학습 데이터에 없는 사내 비공개 정보는 LLM이 그럴듯하지만 틀린 답변을 생성합니다.

실행 방법:
    python src/01_llm_only.py

필요 환경:
    - Ollama가 실행 중이어야 합니다 (ollama serve)
    - OLLAMA_MODEL 모델이 pull되어 있어야 합니다 (ollama pull deepseek-r1:8b)
"""

import sys
import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드 (프로젝트 루트 기준)
load_dotenv(Path(__file__).parent.parent / ".env")

# --- 설정 상수 ---
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:8b")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

REQUEST_TIMEOUT = 120  # 초 (LLM 응답 대기 최대 시간)


# =============================================================================
# === INPUT ===
# =============================================================================

def build_prompt(question: str) -> str:
    """사용자 질문을 LLM 프롬프트로 변환합니다.

    Args:
        question: 사용자가 입력한 질문 문자열

    Returns:
        LLM에 전달할 완성된 프롬프트 문자열
    """
    return (
        "당신은 사내 인사 정보에 정통한 AI 비서입니다. "
        "질문에 최대한 성실하게 답변하십시오.\n\n"
        f"질문: {question}\n\n"
        "답변:"
    )


# =============================================================================
# === PROCESS ===
# =============================================================================

def call_ollama(prompt: str) -> str:
    """Ollama API에 HTTP 요청을 보내 LLM 응답을 받아옵니다.

    Ollama의 /api/generate 엔드포인트를 직접 호출합니다.
    stream=False로 설정하여 전체 응답을 한 번에 받습니다.

    Args:
        prompt: LLM에 전달할 프롬프트 문자열

    Returns:
        LLM이 생성한 응답 문자열

    Raises:
        SystemExit: Ollama 서버 연결 실패 또는 응답 오류 시 종료
    """
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)  # ①
        response.raise_for_status()  # ②
    except requests.exceptions.ConnectionError:
        print("\n[오류] Ollama 서버에 연결할 수 없습니다.")
        print("  해결 방법: 터미널에서 'ollama serve' 명령을 먼저 실행하십시오.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("\n[오류] Ollama 응답 시간이 초과되었습니다.")
        print(f"  현재 타임아웃: {REQUEST_TIMEOUT}초")
        print("  해결 방법: 더 작은 모델(deepseek-r1:1.5b)을 사용하거나 타임아웃을 늘리십시오.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"\n[오류] Ollama API 응답 오류: {e}")
        print(f"  모델 '{OLLAMA_MODEL}'이 pull되어 있는지 확인하십시오.")
        print(f"  명령: ollama pull {OLLAMA_MODEL}")
        sys.exit(1)

    data = response.json()  # ③
    return data.get("response", "")  # ④


def call_openai(prompt: str) -> str:
    """OpenAI API에 HTTP 요청을 보내 LLM 응답을 받아옵니다.

    LLM_PROVIDER=openai 설정 시 Ollama 대신 이 함수가 호출됩니다.

    Args:
        prompt: LLM에 전달할 프롬프트 문자열

    Returns:
        LLM이 생성한 응답 문자열

    Raises:
        SystemExit: API 키 미설정 또는 연결 오류 시 종료
    """
    if not OPENAI_API_KEY:
        print("\n[오류] OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("  .env 파일에 OPENAI_API_KEY를 입력하십시오. (.env.example 참조)")
        sys.exit(1)

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": OPENAI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        print("\n[오류] OpenAI API 서버에 연결할 수 없습니다.")
        print("  인터넷 연결을 확인하십시오.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"\n[오류] OpenAI API 응답 오류: {e}")
        print("  API 키가 유효한지, 잔액이 충분한지 확인하십시오.")
        sys.exit(1)

    data = response.json()
    return data["choices"][0]["message"]["content"]


def ask_llm(question: str) -> str:
    """LLM_PROVIDER 설정에 따라 적절한 LLM API를 호출합니다.

    .env의 LLM_PROVIDER 값(ollama/openai)에 따라 자동으로 제공자를 전환합니다.

    Args:
        question: 사용자 질문 문자열

    Returns:
        LLM 응답 문자열

    Raises:
        SystemExit: 지원하지 않는 LLM_PROVIDER 설정 시 종료
    """
    prompt = build_prompt(question)  # ①

    if LLM_PROVIDER == "ollama":
        return call_ollama(prompt)  # ②
    elif LLM_PROVIDER == "openai":
        return call_openai(prompt)  # ③
    else:
        print(f"\n[오류] 지원하지 않는 LLM 제공자입니다: '{LLM_PROVIDER}'")
        print("  .env 파일의 LLM_PROVIDER를 'ollama' 또는 'openai'로 설정하십시오.")
        sys.exit(1)


# =============================================================================
# === OUTPUT ===
# =============================================================================

def display_result(question: str, answer: str) -> None:
    """질문과 LLM 응답을 포맷에 맞게 출력합니다.

    Args:
        question: 사용자 질문 문자열
        answer: LLM이 생성한 응답 문자열
    """
    print("\n" + "=" * 60)
    print("[실습 1] LLM 단독 질의 — 사내 정보 질문하기")
    print("=" * 60)
    print(f"\n[사용 모델] {LLM_PROVIDER.upper()} / {OLLAMA_MODEL if LLM_PROVIDER == 'ollama' else OPENAI_MODEL}")
    print(f"\n[질문]\n{question}")
    print("\n[LLM 응답]")
    print("-" * 40)
    print(answer)
    print("-" * 40)
    print("\n[분석]")
    print("  위 응답은 그럴듯하게 보이지만, 실제 사내 데이터와 다릅니다.")
    print("  LLM은 학습 데이터에 없는 사내 비공개 정보를 알 수 없어")
    print("  그럴듯한 내용을 '만들어내는' 환각(Hallucination)을 일으킵니다.")
    print("\n  다음 실습: python src/02_context_injection.py")


def main() -> None:
    """메인 실행 함수 — LLM 단독 질의 실습을 실행합니다."""
    # 사내 정보 질문 (LLM이 알 수 없는 정보)
    question = "김철수 사원의 남은 연차는 며칠인가요?"

    print("\n[실습 시작] LLM 단독 질의")
    print(f"  LLM 제공자: {LLM_PROVIDER.upper()}")
    print(f"  질문: {question}")
    print("\n  LLM에 질문 중... (최대 {timeout}초 대기)".format(timeout=REQUEST_TIMEOUT))

    answer = ask_llm(question)  # ①
    display_result(question, answer)  # ②


if __name__ == "__main__":
    main()
