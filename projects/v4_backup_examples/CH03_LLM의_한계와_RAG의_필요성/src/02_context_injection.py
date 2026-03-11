"""
02_context_injection.py — Context Injection 맛보기 (토큰 한계 체감)

프롬프트에 사내 문서를 직접 삽입하여 LLM이 정확한 답변을 할 수 있게 합니다.
단, 문서가 많아질수록 프롬프트가 길어져 토큰 한계에 도달하는 문제를 체험합니다.

실행 방법:
    python src/02_context_injection.py

필요 환경:
    - Ollama가 실행 중이어야 합니다 (ollama serve)
    - OLLAMA_MODEL 모델이 pull되어 있어야 합니다 (ollama pull deepseek-r1:8b)
"""

import sys
import os
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

REQUEST_TIMEOUT = 120  # 초


# =============================================================================
# === INPUT ===
# =============================================================================

# 인라인 사내 문서 샘플 — 실제 사내 시스템에서는 DB나 파일에서 로드합니다
DOCUMENT_HR_LEAVE = """
[문서 1: 인사팀 — 직원 연차 현황 (2025년 기준)]
직원명: 김철수
부서: 개발팀
입사일: 2021-03-15
연차 총일수: 15일
사용 연차: 9일
남은 연차: 6일
만료 예정일: 2025-12-31

직원명: 이영희
부서: 마케팅팀
입사일: 2019-07-01
연차 총일수: 15일
사용 연차: 12일
남은 연차: 3일
만료 예정일: 2025-12-31

직원명: 박민수
부서: 영업팀
입사일: 2023-01-10
연차 총일수: 11일
사용 연차: 5일
남은 연차: 6일
만료 예정일: 2025-12-31
"""

DOCUMENT_HR_POLICY = """
[문서 2: 취업규칙 — 연차 유급휴가 규정 (제15조)]
1. 1년 이상 근속한 직원에게는 15일의 연차 유급휴가를 부여한다.
2. 1년 미만 근속 직원에게는 매월 개근 시 1일의 월차를 부여한다.
3. 연차는 당해 연도 12월 31일까지 사용하여야 하며, 미사용 연차는 수당으로 지급한다.
4. 연차 사용 신청은 사용 예정일 3일 전에 팀장 승인을 받아야 한다.
5. 병가, 경조사 등 특별 휴가는 별도 규정에 따른다.
6. 육아휴직 후 복직 시 연차는 법령에 따라 별도 산정한다.
"""

DOCUMENT_IT_GUIDE = """
[문서 3: IT팀 — 사내 시스템 사용 가이드 (v2.3)]
1. 사내 포털 접속: https://hr.company.internal (VPN 필수)
2. 연차 신청: 포털 로그인 → 근태관리 → 연차신청 → 날짜 선택 → 팀장 결재
3. 급여명세서 조회: 포털 → 급여관리 → 명세서조회 (매월 25일 업데이트)
4. 비밀번호 분실: IT 헬프데스크 내선 1234 또는 it-help@company.com
5. 노트북 지급 기준: 입사 첫날 지급, 분실 시 경위서 제출 후 재지급
6. 보안 정책: 외부 USB 사용 금지, 개인 이메일 업무 활용 금지, 화면보호기 5분 설정
"""

# 문서 목록 — 순서대로 하나씩 프롬프트에 추가하며 토큰 한계를 체감합니다
ALL_DOCUMENTS = [
    ("문서 1: 직원 연차 현황", DOCUMENT_HR_LEAVE),
    ("문서 2: 연차 유급휴가 규정", DOCUMENT_HR_POLICY),
    ("문서 3: IT 시스템 사용 가이드", DOCUMENT_IT_GUIDE),
]

# 질문
QUESTION = "김철수 사원의 남은 연차는 며칠인가요?"


# =============================================================================
# === PROCESS ===
# =============================================================================

def estimate_token_count(text: str) -> int:
    """텍스트의 대략적인 토큰 수를 추정합니다.

    실제 토크나이저 없이 간단한 규칙으로 추정합니다.
    한국어는 1글자 = 약 1.5~2토큰, 영어는 1단어 = 약 1.3토큰으로 근사합니다.

    Args:
        text: 토큰 수를 추정할 텍스트 문자열

    Returns:
        추정 토큰 수 (정수)
    """
    # 간단한 추정: 한국어 문자 수 × 2 + 영단어 수 × 1.3
    korean_chars = sum(1 for c in text if "\uac00" <= c <= "\ud7a3")
    other_words = len([w for w in text.split() if not any("\uac00" <= c <= "\ud7a3" for c in w)])
    return int(korean_chars * 2 + other_words * 1.3)


def build_context_prompt(documents: list[tuple[str, str]], question: str) -> str:
    """문서 목록을 프롬프트에 직접 삽입하여 Context Injection 프롬프트를 구성합니다.

    Args:
        documents: (문서명, 문서내용) 튜플의 리스트
        question: 사용자 질문 문자열

    Returns:
        문서가 삽입된 완성된 프롬프트 문자열
    """
    context_parts = []
    for doc_name, doc_content in documents:
        context_parts.append(f"=== {doc_name} ===\n{doc_content.strip()}")

    context = "\n\n".join(context_parts)  # ①

    prompt = (  # ②
        "당신은 사내 인사 정보에 정통한 AI 비서입니다.\n"
        "아래 제공된 사내 문서만을 참고하여 질문에 답변하십시오.\n"
        "문서에 없는 내용은 '문서에서 확인할 수 없습니다.'라고 답변하십시오.\n\n"
        f"[참고 문서]\n{context}\n\n"
        f"[질문]\n{question}\n\n"
        "[답변]"
    )
    return prompt


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
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"\n[오류] Ollama API 응답 오류: {e}")
        print(f"  모델 '{OLLAMA_MODEL}'이 pull되어 있는지 확인하십시오.")
        sys.exit(1)

    data = response.json()  # ③
    return data.get("response", "")  # ④


def call_openai(prompt: str) -> str:
    """OpenAI API에 HTTP 요청을 보내 LLM 응답을 받아옵니다.

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

    data = response.json()
    return data["choices"][0]["message"]["content"]


def ask_llm_with_context(documents: list[tuple[str, str]], question: str) -> tuple[str, str, int]:
    """문서를 프롬프트에 삽입하여 LLM에 질문합니다.

    Args:
        documents: (문서명, 문서내용) 튜플의 리스트
        question: 사용자 질문 문자열

    Returns:
        (LLM 응답 문자열, 사용된 프롬프트 문자열, 추정 토큰 수) 튜플
    """
    prompt = build_context_prompt(documents, question)  # ①
    token_estimate = estimate_token_count(prompt)  # ②

    if LLM_PROVIDER == "ollama":
        answer = call_ollama(prompt)  # ③
    elif LLM_PROVIDER == "openai":
        answer = call_openai(prompt)
    else:
        print(f"\n[오류] 지원하지 않는 LLM 제공자입니다: '{LLM_PROVIDER}'")
        sys.exit(1)

    return answer, prompt, token_estimate


# =============================================================================
# === OUTPUT ===
# =============================================================================

def display_step_result(
    step: int,
    doc_names: list[str],
    answer: str,
    token_estimate: int,
    model_context_limit: int = 4096,
) -> None:
    """각 단계의 Context Injection 결과를 출력합니다.

    Args:
        step: 현재 단계 번호 (1부터 시작)
        doc_names: 현재 단계에서 사용한 문서명 목록
        answer: LLM이 생성한 응답 문자열
        token_estimate: 추정 토큰 수
        model_context_limit: 모델의 대략적 컨텍스트 한계 (기본 4096토큰)
    """
    usage_pct = (token_estimate / model_context_limit) * 100
    warning = " ⚠ 컨텍스트 한계 초과 위험!" if usage_pct > 80 else ""

    print(f"\n{'=' * 60}")
    print(f"[단계 {step}] 삽입 문서: {', '.join(doc_names)}")
    print(f"  추정 토큰 수: {token_estimate:,}개 ({usage_pct:.1f}% / {model_context_limit:,}){warning}")
    print(f"\n[LLM 응답]")
    print("-" * 40)
    print(answer)
    print("-" * 40)


def main() -> None:
    """메인 실행 함수 — Context Injection 단계별 실습을 실행합니다.

    문서를 하나씩 추가하며 LLM 응답의 정확도가 향상되는 과정과,
    동시에 토큰 사용량이 증가하여 한계에 도달하는 문제를 체험합니다.
    """
    print("\n" + "=" * 60)
    print("[실습 2] Context Injection — 프롬프트에 문서 직접 삽입하기")
    print("=" * 60)
    print(f"\n[사용 모델] {LLM_PROVIDER.upper()} / {OLLAMA_MODEL if LLM_PROVIDER == 'ollama' else OPENAI_MODEL}")
    print(f"[질문] {QUESTION}")

    # 단계별 누적 실험: 문서를 하나씩 추가하며 실행
    for step, (doc_name, _) in enumerate(ALL_DOCUMENTS, start=1):
        current_docs = ALL_DOCUMENTS[:step]  # ①
        doc_names = [name for name, _ in current_docs]

        print(f"\n\n--- [단계 {step}] 문서 {step}개 삽입 중... ---")
        answer, _, token_estimate = ask_llm_with_context(current_docs, QUESTION)  # ②
        display_step_result(step, doc_names, answer, token_estimate)  # ③

    # 최종 분석 출력
    print("\n" + "=" * 60)
    print("[분석 요약]")
    print("  - 문서 1 삽입 후: 김철수 사원의 정확한 연차 정보 응답 가능")
    print("  - 문서 2~3 추가 시: 토큰 수가 급격히 증가")
    print("  - 실제 사내 시스템에는 수천~수만 개의 문서가 있습니다.")
    print("  - 모든 문서를 프롬프트에 삽입하는 것은 불가능합니다.")
    print()
    print("  [결론] Context Injection은 임시방편입니다.")
    print("  문서가 많아질수록 토큰 한계를 초과하고 응답 속도가 느려집니다.")
    print("  해결책 → 다음 실습: python src/03_rag_preview.py")


if __name__ == "__main__":
    main()
