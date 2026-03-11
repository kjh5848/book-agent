"""
[Step 2 — 한계] Context Injection 맛보기

이 스크립트는 HR 규정 문서 전체를 프롬프트에 직접 삽입하여
LLM의 응답이 개선되는지 확인합니다.

동시에 토큰 추정치를 계산하여, 문서가 많아질수록 이 방식이
왜 확장 불가능한지 체감합니다.

기대 결과:
  - 01번 실험보다 정확한 답변 생성 (문서를 직접 제공했으므로)
  - 토큰 추정치 출력으로 토큰 한계 경고 확인
  - "문서가 수십 개라면?" 질문을 통해 Context Injection의 한계 체감

실행:
  python src/02_context_injection.py
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

# 컨텍스트 주입 토큰 경고 임계값 (대략적 기준)
TOKEN_WARNING_THRESHOLD: int = 4000

# 01번 실험과 동일한 질문 3개 (비교 목적)
QUESTIONS: list[str] = [
    "우리 회사(테크컴퍼니)의 신입사원 연차 발생 규정이 어떻게 돼?",
    "2024년 4분기 마케팅팀 매출 목표는 얼마야?",
    "사내 보안 USB 정책이 어떻게 돼?",
]

# HR 정책 파일 경로
_HR_POLICY_PATH: Path = Path(__file__).parent.parent / "data" / "sample_hr_policy.txt"


def load_document(file_path: str) -> str:
    """
    지정한 경로의 텍스트 파일을 읽어 문자열로 반환합니다.

    Input  : 텍스트 파일 경로 문자열
    Process: UTF-8 인코딩으로 파일 전체 내용 읽기
    Output : 파일 내용 문자열

    Args:
        file_path: 읽을 파일의 절대 또는 상대 경로

    Returns:
        파일 전체 내용 문자열

    Raises:
        SystemExit: 파일을 찾을 수 없거나 읽기에 실패한 경우
    """

    # --- Input ---
    path = Path(file_path)
    if not path.exists():
        print(f"[오류] 파일을 찾을 수 없습니다: {file_path}")
        print("      data/ 폴더에 sample_hr_policy.txt 파일이 있는지 확인하십시오.")
        sys.exit(1)

    # --- Process ---
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"[오류] 파일 읽기 실패: {e}")
        sys.exit(1)

    # --- Output ---
    return content


def count_tokens(text: str) -> int:
    """
    텍스트의 대략적인 토큰 수를 추정합니다.

    LLM 토큰은 단어나 문자 단위로 분할되며, 정확한 계산에는
    tiktoken 같은 토크나이저가 필요합니다.
    여기서는 '글자 수 / 4'를 영어 기준 근사값으로 사용합니다.
    (한국어는 보통 더 많은 토큰을 소비하므로 실제는 더 높을 수 있음)

    Input  : 토큰 수를 추정할 텍스트 문자열
    Process: len(text) // 4 로 대략적인 토큰 수 계산
    Output : 추정 토큰 수 정수

    Args:
        text: 토큰 수를 추정할 문자열

    Returns:
        대략적인 토큰 수 (양의 정수)
    """

    # --- Input ---
    if not text:
        return 0

    # --- Process ---
    estimated_tokens = len(text) // 4

    # --- Output ---
    return estimated_tokens


def build_prompt(question: str, context: str) -> str:
    """
    질문과 문서 전체를 하나의 프롬프트 문자열로 조합합니다.

    Context Injection 방식은 참고 문서 전체를 프롬프트 앞부분에
    붙여 넣는 가장 단순한 방법입니다.

    Input  : 사용자 질문, 참고 문서 내용 문자열
    Process: 시스템 역할 안내 + 참고 문서 + 질문을 하나의 문자열로 결합
    Output : LLM에 전달할 완성된 프롬프트 문자열

    Args:
        question: 사용자의 질문 문자열
        context: 프롬프트에 삽입할 문서 전체 내용

    Returns:
        완성된 프롬프트 문자열
    """

    # --- Input ---
    if not question.strip():
        raise ValueError("질문이 비어 있습니다.")
    if not context.strip():
        raise ValueError("컨텍스트 문서가 비어 있습니다.")

    # --- Process ---
    prompt = f"""당신은 회사 내부 규정에 대해 답변하는 AI 비서입니다.
아래 [참고 문서]를 바탕으로 질문에 답변하십시오.
참고 문서에 없는 내용은 "해당 내용이 문서에 없습니다"라고 답변하십시오.
반드시 한국어로 답변하십시오.

[참고 문서]
{context}

[질문]
{question}

[답변]"""

    # --- Output ---
    return prompt


def ask_with_context(question: str, context: str) -> dict:
    """
    문서 전체를 프롬프트에 삽입하여 LLM을 호출하고 결과를 반환합니다.

    토큰 추정치를 계산하고 임계값 초과 시 경고를 출력합니다.
    이를 통해 Context Injection의 한계(토큰 제한, 속도 저하)를 체감합니다.

    Input  : 사용자 질문 문자열, 참고 문서 내용 문자열
    Process: 프롬프트 조합 → 토큰 추정 → ChatOllama 호출
    Output : {"response": str, "token_estimate": int, "over_limit": bool}
             (토큰 추정치가 TOKEN_WARNING_THRESHOLD 초과 시 over_limit=True)

    Args:
        question: 사용자의 질문 문자열
        context: 프롬프트에 삽입할 문서 전체 내용

    Returns:
        응답 문자열, 토큰 추정치, 임계값 초과 여부를 담은 딕셔너리

    Raises:
        SystemExit: LLM 호출 중 연결 오류가 발생한 경우
    """

    # --- Input ---
    prompt = build_prompt(question, context)
    token_estimate = count_tokens(prompt)
    over_limit = token_estimate > TOKEN_WARNING_THRESHOLD

    # 토큰 경고 출력
    if over_limit:
        print(f"\n  [토큰 경고] 추정 토큰 수: {token_estimate:,}개")
        print(f"             임계값({TOKEN_WARNING_THRESHOLD:,}개)을 초과했습니다.")
        print("             문서가 많아질수록 이 숫자는 선형으로 증가합니다.")
        print("             실제 LLM의 컨텍스트 한계(예: 4096, 8192 토큰)를")
        print("             초과하면 응답이 잘리거나 오류가 발생합니다.")
    else:
        print(f"\n  [토큰 추정] {token_estimate:,}개 (임계값 {TOKEN_WARNING_THRESHOLD:,}개 이내)")

    # --- Process ---
    try:
        llm = ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0,
        )
        response = llm.invoke(prompt)
    except Exception as e:
        print(f"\n[오류] LLM 호출 중 오류가 발생했습니다: {e}")
        print("      Ollama가 실행 중인지 확인하십시오: ollama serve")
        sys.exit(1)

    # --- Output ---
    return {
        "response": response.content,
        "token_estimate": token_estimate,
        "over_limit": over_limit,
    }


def main() -> None:
    """
    01번 실험과 동일한 질문 3개를 Context Injection 방식으로 실행합니다.

    응답 개선 여부를 확인하고, 토큰 경고를 통해
    이 방식이 왜 확장 불가능한지 체감합니다.

    Input  : sample_hr_policy.txt 문서, QUESTIONS 상수의 질문 목록
    Process: 문서 로드 → 각 질문에 대해 ask_with_context() 호출 → 결과 출력
    Output : 각 질문·응답·토큰 정보를 표준 출력으로 출력
    """

    # --- Input ---
    print("=" * 65)
    print("CH03 실험 2: Context Injection — 응답 개선 + 토큰 한계 체험")
    print("=" * 65)
    print(f"사용 모델  : {OLLAMA_MODEL}")
    print(f"Ollama 서버: {OLLAMA_BASE_URL}")
    print()
    print("이 실험은 HR 규정 문서 전체를 프롬프트에 직접 삽입하여")
    print("응답이 개선되는지 확인하고, 토큰 한계를 체감합니다.\n")

    # HR 문서 로드
    context = load_document(str(_HR_POLICY_PATH))
    doc_length = len(context)
    print(f"[문서 로드] sample_hr_policy.txt ({doc_length:,}자)")
    print(f"           전체 문서를 프롬프트에 직접 삽입합니다.")

    # --- Process ---
    total = len(QUESTIONS)
    for index, question in enumerate(QUESTIONS, start=1):
        print(f"\n{'=' * 65}")
        print(f"질문 {index}/{total}")
        print("=" * 65)
        print(f"질문: {question}")
        print("-" * 65)

        start_time = time.time()
        result = ask_with_context(question, context)
        elapsed = time.time() - start_time

        print(f"\nLLM 답변 ({elapsed:.1f}초):\n")
        print(result["response"])
        print("-" * 65)

        # 질문별 비교 관찰 포인트
        if index == 1:
            print("\n[비교 관찰] 01번 실험(환각)과 비교하십시오.")
            print("  문서를 제공받은 LLM은 정확한 규정을 답변할 수 있습니다.")
            print("  그러나 이 프롬프트 하나의 길이만으로도 수천 토큰입니다.")
        elif index == 2:
            print("\n[비교 관찰] 매출 목표는 HR 문서에 없는 내용입니다.")
            print("  LLM이 '해당 내용이 문서에 없습니다'라고 답변하는지 확인하십시오.")
            print("  Context Injection은 제공된 문서 범위 내에서만 정확합니다.")
        elif index == 3:
            print("\n[비교 관찰] 보안 USB 정책은 HR 문서 제7조에 명시되어 있습니다.")
            print("  문서 전체를 삽입했으므로 정확한 규정을 찾아 답변해야 합니다.")

    # --- Output ---
    # Context Injection의 한계 정리
    final_token_estimate = count_tokens(build_prompt(QUESTIONS[0], context))
    print("\n" + "=" * 65)
    print("실험 2 완료: Context Injection의 한계")
    print("=" * 65)
    print("\n[한계 정리]")
    print(f"  1. 문서 1개에 이미 약 {final_token_estimate:,}개의 토큰을 사용합니다.")
    print("  2. 사내 문서가 수십 개라면 전체를 삽입하는 것은 불가능합니다.")
    print("  3. 문서가 많을수록 응답 속도가 선형으로 저하됩니다.")
    print("  4. LLM의 컨텍스트 한계를 초과하면 문서 내용이 잘립니다.")
    print("\n  → 이것이 RAG(검색 증강 생성)가 필요한 이유입니다.")
    print("    질문과 관련된 문서 조각만 찾아 삽입하면 이 모든 문제가 해결됩니다.")
    print("\n[다음 단계]")
    print("  python src/03_rag_preview.py")
    print("  → 인메모리 ChromaDB로 RAG를 체험합니다.")
    print("  → 청킹 없음 vs 청킹 있음 비교로 검색 정밀도 차이를 확인합니다.\n")


if __name__ == "__main__":
    main()
