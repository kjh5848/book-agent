"""프롬프트 변형 비교 실험 모듈입니다.

세 가지 프롬프트 전략(기본형, 근거 우선형, 무지 인정형)으로 동일한 질문을
Ollama LLM에 전달하여 응답을 비교합니다.
"""

import os
import logging
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# --- 상수 ---
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "deepseek-r1:1.5b")

# 세 가지 프롬프트 변형 정의
PROMPT_VARIANTS: dict[str, str] = {
    "baseline": (
        "당신은 AI 비서입니다. 주어진 문서를 참고하여 답하십시오.\n\n"
        "참고 문서:\n{context}\n\n"
        "질문: {question}\n\n"
        "답변:"
    ),
    "evidence_first": (
        "당신은 문서 기반 QA 시스템입니다. 반드시 아래 문서에서 근거를 찾아 인용한 뒤 답하십시오.\n\n"
        "참고 문서:\n{context}\n\n"
        "질문: {question}\n\n"
        "지시사항:\n"
        "1. 먼저 관련 문서 구절을 인용하십시오 (따옴표 사용).\n"
        "2. 인용 근거를 바탕으로 최종 답변을 작성하십시오.\n\n"
        "인용:\n답변:"
    ),
    "admit_ignorance": (
        "당신은 신뢰도 높은 AI 비서입니다. 아래 문서에서 답을 찾을 수 없으면 "
        "'해당 정보를 문서에서 찾을 수 없습니다'라고 명확히 밝히십시오. "
        "절대 추측으로 답하지 마십시오.\n\n"
        "참고 문서:\n{context}\n\n"
        "질문: {question}\n\n"
        "답변:"
    ),
}


def _call_ollama(prompt: str, model: str = LLM_MODEL_NAME) -> str:
    """Ollama /api/generate 엔드포인트를 호출하여 텍스트를 생성합니다.

    Args:
        prompt: LLM에 전달할 완성된 프롬프트 문자열
        model: 사용할 Ollama 모델명 (기본값: 환경변수 LLM_MODEL_NAME)

    Returns:
        LLM이 생성한 응답 텍스트 문자열

    Raises:
        RuntimeError: Ollama 서버 연결 실패 또는 응답 파싱 오류 시
    """
    # --- Input ---
    if not prompt.strip():
        raise ValueError("프롬프트가 비어 있습니다. 질문과 컨텍스트를 확인하십시오.")

    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    # --- Process ---
    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        generated_text: str = data.get("response", "").strip()
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            f"Ollama 서버({OLLAMA_BASE_URL})에 연결할 수 없습니다.\n"
            "Ollama가 실행 중인지 확인하십시오: 'ollama serve'"
        ) from exc
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(
            f"Ollama API 호출 중 HTTP 오류가 발생했습니다: {exc}\n"
            f"모델 '{model}'이 설치됐는지 확인하십시오: 'ollama pull {model}'"
        ) from exc
    except (KeyError, ValueError) as exc:
        raise RuntimeError(
            f"Ollama 응답 파싱 중 오류가 발생했습니다: {exc}"
        ) from exc

    # --- Output ---
    return generated_text


def compare_prompts(question: str, context: str) -> dict[str, str]:
    """세 프롬프트 변형으로 동일 질문을 실행하여 응답을 비교 반환합니다.

    PROMPT_VARIANTS에 정의된 baseline, evidence_first, admit_ignorance
    세 가지 프롬프트 전략에 동일한 질문과 컨텍스트를 삽입하여
    각각 LLM을 호출하고 결과를 딕셔너리로 반환합니다.

    Args:
        question: 사용자 질문 문자열
        context: 검색된 문서 컨텍스트 문자열 (여러 청크를 합친 텍스트)

    Returns:
        프롬프트 변형명을 키로 하고 LLM 응답을 값으로 하는 딕셔너리::

            {
                "baseline": "기본형 응답 텍스트",
                "evidence_first": "근거 우선형 응답 텍스트",
                "admit_ignorance": "무지 인정형 응답 텍스트"
            }

    Raises:
        ValueError: question 또는 context가 비어 있는 경우
        RuntimeError: 모든 프롬프트 변형 호출 실패 시
    """
    # --- Input ---
    if not question.strip():
        raise ValueError("질문이 비어 있습니다. 질문을 입력하십시오.")
    if not context.strip():
        raise ValueError("컨텍스트가 비어 있습니다. 검색된 문서가 없습니다.")

    results: dict[str, str] = {}
    failed_variants: list[str] = []

    # --- Process ---
    print(f"\n[프롬프트 비교] 질문: {question[:50]}...")
    print(f"  컨텍스트 길이: {len(context)}자")
    print(f"  모델: {LLM_MODEL_NAME}")
    print("-" * 40)

    for variant_name, template in PROMPT_VARIANTS.items():
        print(f"  [{variant_name}] 호출 중...", end=" ", flush=True)
        try:
            filled_prompt = template.format(context=context, question=question)
            response = _call_ollama(filled_prompt)
            results[variant_name] = response
            preview = response[:60].replace("\n", " ")
            print(f"완료 (응답: {preview}...)")
        except (RuntimeError, ValueError) as exc:
            logger.error("프롬프트 변형 '%s' 호출 실패: %s", variant_name, exc)
            results[variant_name] = f"[오류] {exc}"
            failed_variants.append(variant_name)
            print(f"실패")

    if len(failed_variants) == len(PROMPT_VARIANTS):
        raise RuntimeError(
            "모든 프롬프트 변형 호출이 실패했습니다. "
            "Ollama 서버 상태를 확인하십시오."
        )

    if failed_variants:
        logger.warning(
            "일부 프롬프트 변형 호출 실패: %s", ", ".join(failed_variants)
        )

    # --- Output ---
    return results


def run_prompt_comparison(
    test_cases: list[dict[str, str]],
) -> list[dict[str, Any]]:
    """여러 테스트 케이스에 대해 프롬프트 비교를 실행합니다.

    각 테스트 케이스의 question과 context로 compare_prompts를 호출하고
    모든 결과를 리스트로 반환합니다.

    Args:
        test_cases: question과 context 키를 포함하는 딕셔너리 리스트

    Returns:
        각 테스트 케이스의 question, context, responses(세 변형 응답)를
        포함하는 딕셔너리 리스트

    Raises:
        ValueError: test_cases가 비어 있는 경우
    """
    # --- Input ---
    if not test_cases:
        raise ValueError("테스트 케이스 리스트가 비어 있습니다.")

    all_results: list[dict[str, Any]] = []

    # --- Process ---
    print("=" * 60)
    print("프롬프트 변형 비교 실험 시작")
    print(f"총 {len(test_cases)}개 테스트 케이스")
    print("=" * 60)

    for i, case in enumerate(test_cases, 1):
        question = case.get("question", "")
        context = case.get("context", "")

        print(f"\n[{i}/{len(test_cases)}] 테스트 케이스")

        try:
            responses = compare_prompts(question, context)
            all_results.append({
                "question": question,
                "context": context,
                "responses": responses,
                "status": "success",
            })
        except (ValueError, RuntimeError) as exc:
            logger.error("테스트 케이스 %d 처리 실패: %s", i, exc)
            all_results.append({
                "question": question,
                "context": context,
                "responses": {},
                "status": "error",
                "error": str(exc),
            })

    # --- Output ---
    success_count = sum(1 for r in all_results if r["status"] == "success")
    print(f"\n완료: {success_count}/{len(test_cases)} 성공")
    return all_results
