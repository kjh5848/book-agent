"""RAG 시스템 평가 모듈입니다.

테스트셋을 로드하여 RAG 체인의 검색 정확도, 답변 키워드 포함 여부,
할루시네이션 발생 여부를 자동으로 평가하고 보고서를 생성합니다.
"""

import json
import os
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# --- 상수 ---
DEFAULT_TESTSET_PATH: str = os.getenv("TESTSET_PATH", "./data/testset.json")
EVAL_OUTPUT_DIR: str = "./outputs/eval_results"

# 할루시네이션 탐지 지시어 목록 (LLM이 없는 정보를 만들어낼 때 자주 쓰는 표현)
HALLUCINATION_INDICATORS: list[str] = [
    "아마도",
    "추측",
    "~일 것입니다",
    "~인 것 같습니다",
    "정확하지 않지만",
    "확실하지 않지만",
    "일반적으로",
    "보통은",
]

# 무지 인정 표현 (올바른 동작으로 간주)
IGNORANCE_PHRASES: list[str] = [
    "찾을 수 없습니다",
    "문서에 없습니다",
    "해당 정보가 없습니다",
    "알 수 없습니다",
    "정보가 부족합니다",
]


@dataclass
class TestCase:
    """테스트 케이스 데이터 클래스입니다.

    Attributes:
        question: 평가에 사용할 질문 문자열
        expected_answer_keywords: 올바른 답변에 반드시 포함되어야 할 키워드 리스트
        expected_source_file: 답변 근거가 있어야 할 원본 파일명
    """

    question: str
    expected_answer_keywords: list[str]
    expected_source_file: str


@dataclass
class EvalResult:
    """단일 테스트 케이스 평가 결과 데이터 클래스입니다.

    Attributes:
        test_case: 평가에 사용된 테스트 케이스
        retrieved_docs: 검색된 문서 텍스트 리스트
        generated_answer: LLM이 생성한 답변 문자열
        retrieval_correct: 정답 소스 파일이 검색 결과에 포함됐는지 여부
        answer_contains_keywords: 답변에 모든 기대 키워드가 포함됐는지 여부
        hallucination_detected: 할루시네이션 지시어가 감지됐는지 여부
    """

    test_case: TestCase
    retrieved_docs: list[str]
    generated_answer: str
    retrieval_correct: bool
    answer_contains_keywords: bool
    hallucination_detected: bool


def load_testset(path: str = DEFAULT_TESTSET_PATH) -> list[TestCase]:
    """JSON 파일에서 테스트 케이스를 로드합니다.

    JSON 배열에서 question, expected_answer_keywords,
    expected_source_file 필드를 읽어 TestCase 객체 리스트로 반환합니다.

    Args:
        path: testset.json 파일 경로 (기본값: 환경변수 TESTSET_PATH)

    Returns:
        TestCase 객체 리스트

    Raises:
        FileNotFoundError: 파일이 존재하지 않는 경우
        ValueError: JSON 형식이 올바르지 않거나 필수 필드가 누락된 경우
    """
    # --- Input ---
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"테스트셋 파일을 찾을 수 없습니다: {path}\n"
            "data/testset.json 파일이 존재하는지 확인하십시오."
        )

    # --- Process ---
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_data: list[dict] = json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"testset.json 파일 파싱에 실패했습니다: {exc}\n"
            "JSON 형식이 올바른지 확인하십시오."
        ) from exc

    test_cases: list[TestCase] = []
    for i, item in enumerate(raw_data):
        missing_fields = [
            field for field in ("question", "expected_answer_keywords", "expected_source_file")
            if field not in item
        ]
        if missing_fields:
            raise ValueError(
                f"테스트 케이스 {i + 1}번에 필수 필드가 누락되었습니다: "
                f"{', '.join(missing_fields)}"
            )
        test_cases.append(
            TestCase(
                question=item["question"],
                expected_answer_keywords=item["expected_answer_keywords"],
                expected_source_file=item["expected_source_file"],
            )
        )

    # --- Output ---
    print(f"테스트셋 로드 완료: {len(test_cases)}개 케이스 ({path})")
    return test_cases


def _detect_hallucination(answer: str) -> bool:
    """답변에서 할루시네이션 지시어를 탐지합니다.

    HALLUCINATION_INDICATORS 목록의 표현이 포함되어 있고
    IGNORANCE_PHRASES(올바른 모름 표현)가 없는 경우 할루시네이션으로 판정합니다.

    Args:
        answer: 평가할 LLM 답변 문자열

    Returns:
        할루시네이션이 감지되면 True, 그렇지 않으면 False
    """
    # --- Input ---
    if not answer.strip():
        return False

    # --- Process ---
    # 올바른 모름 표현이 있으면 할루시네이션 아님
    for phrase in IGNORANCE_PHRASES:
        if phrase in answer:
            return False

    # 할루시네이션 지시어 탐지
    for indicator in HALLUCINATION_INDICATORS:
        if indicator in answer:
            return True

    # --- Output ---
    return False


def _check_retrieval_correct(
    retrieved_docs: list[str],
    metadatas: list[dict],
    expected_source_file: str,
) -> bool:
    """검색된 문서 메타데이터에서 정답 소스 파일 포함 여부를 확인합니다.

    Args:
        retrieved_docs: 검색된 문서 텍스트 리스트
        metadatas: 각 문서의 메타데이터 딕셔너리 리스트
        expected_source_file: 기대하는 원본 파일명 (확장자 포함)

    Returns:
        정답 소스 파일이 검색 결과에 포함되면 True, 그렇지 않으면 False
    """
    # --- Input ---
    if not retrieved_docs:
        return False

    # --- Process ---
    # 메타데이터에서 source 필드 확인
    for meta in metadatas:
        source = meta.get("source", "")
        if expected_source_file in source:
            return True

    # 메타데이터가 없으면 문서 내용으로 휴리스틱 판단
    # (파일명 앞부분을 키워드로 사용)
    source_keyword = expected_source_file.replace(".pdf", "").replace("_", " ")
    for doc in retrieved_docs:
        if any(kw in doc for kw in source_keyword.split()[:3]):
            return True

    # --- Output ---
    return False


def evaluate_single(
    test_case: TestCase,
    chain: Any,
    retriever: Any,
) -> EvalResult:
    """단일 테스트 케이스를 평가합니다.

    retriever로 관련 문서를 검색하고 chain으로 답변을 생성한 뒤,
    검색 정확도, 키워드 포함 여부, 할루시네이션을 판정합니다.

    Args:
        test_case: 평가할 테스트 케이스 객체
        chain: LangChain QA 체인 (invoke 메서드 지원 필요)
        retriever: LangChain 리트리버 (invoke 또는 get_relevant_documents 지원 필요)

    Returns:
        평가 결과가 담긴 EvalResult 객체

    Raises:
        RuntimeError: 체인 또는 리트리버 호출 실패 시
    """
    # --- Input ---
    question = test_case.question

    # --- Process ---
    # 1단계: 문서 검색
    retrieved_texts: list[str] = []
    retrieved_metadatas: list[dict] = []
    try:
        if hasattr(retriever, "invoke"):
            docs = retriever.invoke(question)
        else:
            docs = retriever.get_relevant_documents(question)

        for doc in docs:
            retrieved_texts.append(doc.page_content)
            retrieved_metadatas.append(doc.metadata if hasattr(doc, "metadata") else {})
    except Exception as exc:
        raise RuntimeError(
            f"문서 검색 중 오류가 발생했습니다: {exc}\n"
            "리트리버 설정을 확인하십시오."
        ) from exc

    # 2단계: 답변 생성
    generated_answer = ""
    try:
        result = chain.invoke({"query": question})
        if isinstance(result, dict):
            generated_answer = result.get("result", result.get("answer", str(result)))
        else:
            generated_answer = str(result)
    except Exception as exc:
        raise RuntimeError(
            f"답변 생성 중 오류가 발생했습니다: {exc}\n"
            "LLM 체인 설정을 확인하십시오."
        ) from exc

    # 3단계: 평가 판정
    retrieval_correct = _check_retrieval_correct(
        retrieved_texts, retrieved_metadatas, test_case.expected_source_file
    )

    answer_lower = generated_answer.lower()
    answer_contains_keywords = all(
        kw.lower() in answer_lower
        for kw in test_case.expected_answer_keywords
    )

    hallucination_detected = _detect_hallucination(generated_answer)

    # --- Output ---
    return EvalResult(
        test_case=test_case,
        retrieved_docs=retrieved_texts,
        generated_answer=generated_answer,
        retrieval_correct=retrieval_correct,
        answer_contains_keywords=answer_contains_keywords,
        hallucination_detected=hallucination_detected,
    )


def run_evaluation(
    testset: list[TestCase],
    chain: Any,
    retriever: Any,
) -> dict[str, Any]:
    """전체 테스트셋을 평가하고 집계 결과를 반환합니다.

    각 테스트 케이스에 대해 evaluate_single을 호출하고 검색 정확도,
    키워드 포함률, 할루시네이션 발생률을 집계합니다.

    Args:
        testset: 평가할 TestCase 객체 리스트
        chain: LangChain QA 체인 객체
        retriever: LangChain 리트리버 객체

    Returns:
        평가 집계 결과 딕셔너리::

            {
                "total": int,
                "retrieval_accuracy": float,
                "keyword_accuracy": float,
                "hallucination_rate": float,
                "details": list[dict],  # 각 케이스의 EvalResult
                "timestamp": str,
            }

    Raises:
        ValueError: testset이 비어 있는 경우
    """
    # --- Input ---
    if not testset:
        raise ValueError("테스트셋이 비어 있습니다. testset.json을 확인하십시오.")

    print("\n" + "=" * 60)
    print("RAG 시스템 평가 시작")
    print(f"총 {len(testset)}개 테스트 케이스")
    print("=" * 60)

    # --- Process ---
    results: list[EvalResult] = []
    failed_cases: list[int] = []

    for i, test_case in enumerate(testset, 1):
        print(f"\n[{i:02d}/{len(testset):02d}] {test_case.question[:50]}...")
        try:
            result = evaluate_single(test_case, chain, retriever)
            results.append(result)

            status_icons = []
            status_icons.append("O" if result.retrieval_correct else "X")
            status_icons.append("O" if result.answer_contains_keywords else "X")
            status_icons.append("H" if result.hallucination_detected else "-")
            print(
                f"       검색:{status_icons[0]}  키워드:{status_icons[1]}  "
                f"할루시네이션:{status_icons[2]}"
            )
        except RuntimeError as exc:
            logger.error("테스트 케이스 %d 평가 실패: %s", i, exc)
            failed_cases.append(i)

    if not results:
        raise RuntimeError(
            "모든 테스트 케이스 평가에 실패했습니다. "
            "체인과 리트리버 설정을 확인하십시오."
        )

    # 집계 계산
    total = len(results)
    retrieval_correct_count = sum(1 for r in results if r.retrieval_correct)
    keyword_correct_count = sum(1 for r in results if r.answer_contains_keywords)
    hallucination_count = sum(1 for r in results if r.hallucination_detected)

    retrieval_accuracy = retrieval_correct_count / total
    keyword_accuracy = keyword_correct_count / total
    hallucination_rate = hallucination_count / total

    # 상세 결과 직렬화
    details: list[dict] = []
    for r in results:
        details.append({
            "question": r.test_case.question,
            "expected_keywords": r.test_case.expected_answer_keywords,
            "expected_source": r.test_case.expected_source_file,
            "generated_answer": r.generated_answer,
            "retrieved_docs_count": len(r.retrieved_docs),
            "retrieval_correct": r.retrieval_correct,
            "answer_contains_keywords": r.answer_contains_keywords,
            "hallucination_detected": r.hallucination_detected,
        })

    eval_summary: dict[str, Any] = {
        "total": total,
        "failed_cases": failed_cases,
        "retrieval_accuracy": round(retrieval_accuracy, 4),
        "keyword_accuracy": round(keyword_accuracy, 4),
        "hallucination_rate": round(hallucination_rate, 4),
        "details": details,
        "timestamp": datetime.now().isoformat(),
    }

    # --- Output ---
    print("\n" + "=" * 60)
    print("평가 결과 요약")
    print("=" * 60)
    print(f"  검색 정확도(Retrieval Accuracy): {retrieval_accuracy:.1%}")
    print(f"  키워드 포함률(Keyword Accuracy): {keyword_accuracy:.1%}")
    print(f"  할루시네이션 발생률:             {hallucination_rate:.1%}")
    if failed_cases:
        print(f"  평가 실패 케이스: {failed_cases}")
    return eval_summary


def save_report(eval_result: dict[str, Any], output_path: str) -> None:
    """평가 결과를 JSON 파일로 저장합니다.

    출력 디렉토리가 없으면 자동 생성하고, 평가 결과 딕셔너리를
    들여쓰기가 적용된 UTF-8 JSON 파일로 저장합니다.

    Args:
        eval_result: run_evaluation이 반환한 평가 결과 딕셔너리
        output_path: 저장할 JSON 파일의 절대 또는 상대 경로

    Raises:
        ValueError: eval_result가 비어 있는 경우
        OSError: 파일 저장 중 권한 또는 디스크 공간 오류 발생 시
    """
    # --- Input ---
    if not eval_result:
        raise ValueError("저장할 평가 결과가 비어 있습니다.")

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # --- Process ---
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(eval_result, f, ensure_ascii=False, indent=2)
    except OSError as exc:
        raise OSError(
            f"평가 보고서 저장에 실패했습니다: {exc}\n"
            f"경로 및 권한을 확인하십시오: {output_path}"
        ) from exc

    # --- Output ---
    print(f"\n평가 보고서 저장 완료: {output_path}")
    total = eval_result.get("total", 0)
    retrieval_acc = eval_result.get("retrieval_accuracy", 0.0)
    keyword_acc = eval_result.get("keyword_accuracy", 0.0)
    hallucination_rate = eval_result.get("hallucination_rate", 0.0)
    print(f"  총 케이스: {total}개")
    print(f"  검색 정확도: {retrieval_acc:.1%}")
    print(f"  키워드 포함률: {keyword_acc:.1%}")
    print(f"  할루시네이션 발생률: {hallucination_rate:.1%}")
