"""CH02 기초 RAG — 전체 3단계 실행 진입점.

이 스크립트는 LLM 단독 질의 → 컨텍스트 주입 → 기초 RAG의
3단계 실습을 순서대로 실행합니다. 각 단계의 출력을 비교하여
RAG가 필요한 이유와 작동 방식을 체감할 수 있습니다.

실행 방법:
    python src/main.py              # 전체 4단계 실행
    python src/main.py --step 1     # 1단계(LLM 단독)만 실행
    python src/main.py --step 2     # 2단계(Context Injection)만 실행
    python src/main.py --step 3     # 3단계(기초 RAG)만 실행
    python src/main.py --step 4     # 4단계(추론 모드)만 실행
"""

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

# --- 환경 변수 로드 ---
load_dotenv()

# 소스 디렉토리를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).parent))

from context_injection import run_context_injection_demo
from llm_direct import run_llm_only_demo
from reasoning_demo import run_reasoning_demo
from simple_rag import run_simple_rag_demo


def parse_arguments() -> argparse.Namespace:
    """커맨드라인 인수를 파싱합니다.

    Returns:
        파싱된 인수 Namespace 객체
    """
    # --- Input ---
    parser = argparse.ArgumentParser(
        description="CH02 기초 RAG — LLM 단독 질의부터 RAG까지 3단계 실습",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
실행 예시:
  python src/main.py              전체 4단계 순서대로 실행
  python src/main.py --step 1    Step 1: LLM 단독 질의 (환각 체험)
  python src/main.py --step 2    Step 2: Context Injection (반쪽 성공)
  python src/main.py --step 3    Step 3: 기초 RAG (ChromaDB + LLM)
  python src/main.py --step 4    Step 4: DeepSeek R1 추론 모드
        """,
    )

    # --- Process ---
    parser.add_argument(
        "--step",
        type=int,
        choices=[1, 2, 3, 4],
        help="실행할 단계 번호 (1~4). 생략 시 전체 단계 실행.",
    )

    # --- Output ---
    return parser.parse_args()


def print_chapter_header() -> None:
    """챕터 헤더를 출력합니다."""
    print()
    print("*" * 60)
    print("  AI 업무 비서 구축: RAG + MCP 실전 가이드")
    print("  CH02: DeepSeek-R1으로 시작하는 기초 RAG 정복")
    print("*" * 60)
    print()
    print("이 실습에서는 이서연의 시행착오를 따라갑니다:")
    print("  Step 1: LLM 단독 질의 → 환각 발생 (실패)")
    print("  Step 2: 컨텍스트 직접 주입 → 정확하지만 비효율 (반쪽 성공)")
    print("  Step 3: 기초 RAG → 검색 + LLM = 정확한 답변 (성공!)")
    print("  Step 4: DeepSeek R1 추론 모드 → 근거 있는 답변 (심화)")
    print()


def run_step(step_number: int) -> None:
    """지정된 단계를 실행합니다.

    Args:
        step_number: 실행할 단계 번호 (1~4)

    Raises:
        ValueError: 유효하지 않은 단계 번호인 경우
    """
    # --- Input ---
    step_functions = {
        1: run_llm_only_demo,
        2: run_context_injection_demo,
        3: run_simple_rag_demo,
        4: run_reasoning_demo,
    }

    # --- Process ---
    if step_number not in step_functions:
        raise ValueError(f"유효하지 않은 단계 번호입니다: {step_number} (1~4만 가능)")

    step_func = step_functions[step_number]

    # --- Output ---
    step_func()


def run_all_steps() -> None:
    """전체 4단계를 순서대로 실행합니다.

    각 단계 사이에 구분선을 출력하여 단계 전환을 명확히 보여줍니다.
    """
    # --- Input ---
    total_steps = 4

    # --- Process ---
    for step_number in range(1, total_steps + 1):
        try:
            run_step(step_number)
            if step_number < total_steps:
                input(f"\n[Enter 키를 누르면 Step {step_number + 1}로 넘어갑니다...]\n")
        except KeyboardInterrupt:
            print("\n\n실습이 중단되었습니다.")
            sys.exit(0)

    # --- Output ---
    print("\n" + "=" * 60)
    print("  CH02 전체 실습 완료!")
    print("=" * 60)
    print()
    print("핵심 정리:")
    print("  - LLM 단독: 환각 발생 → 사내 규정 답변 불가")
    print("  - Context Injection: 정확하지만 토큰 비용 급증")
    print("  - 기초 RAG: 관련 문서만 검색 → 정확 + 효율")
    print("  - DeepSeek R1 추론: 근거 있는 복잡한 분석 가능")
    print()
    print("다음 챕터(CH03)에서 실제 개발 환경을 구축합니다.")
    print()


def main() -> None:
    """메인 진입점 — 인수에 따라 단계별 또는 전체 실행합니다."""
    # --- Input ---
    args = parse_arguments()

    print_chapter_header()

    # --- Process ---
    if args.step is not None:
        # 특정 단계만 실행
        print(f"[Step {args.step}만 실행합니다]")
        print()
        try:
            run_step(args.step)
        except ValueError as e:
            print(f"오류: {e}")
            sys.exit(1)
    else:
        # 전체 단계 실행
        print("[전체 4단계를 순서대로 실행합니다]")
        print("각 단계 사이에 Enter 키를 눌러 진행합니다.")
        print()
        run_all_steps()

    # --- Output ---
    # 실행 완료 후 종료


if __name__ == "__main__":
    main()
