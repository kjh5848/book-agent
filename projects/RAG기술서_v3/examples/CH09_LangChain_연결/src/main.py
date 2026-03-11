"""
CH09 LangChain 연결 전략 — CLI 실행 진입점.

Q/A 사내 AI AI 비서 LangChain Agent를 대화형 CLI로 실행합니다.
Agent 초기화, Router 동작, Tool 실행 결과를 터미널에서 확인할 수 있습니다.

실행 방법:
    python -m src.main
    (또는 프로젝트 루트에서) python src/main.py
"""

import sys
import os
import logging

# sys.path에 프로젝트 루트 추가 (패키지 임포트 지원)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from dotenv import load_dotenv

from src.monitoring import setup_logging, token_tracker
from src.cache import response_cache, embedding_cache
from src.agent_config import get_agent

# --- 로깅 설정 ---
load_dotenv()
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
USE_JSON_LOG = os.getenv("USE_JSON_LOG", "false").lower() == "true"
LOG_FILE = os.getenv("LOG_FILE", "")

setup_logging(
    level=LOG_LEVEL,
    use_json=USE_JSON_LOG,
    log_file=LOG_FILE if LOG_FILE else None,
)

logger = logging.getLogger(__name__)

# --- 대표 질문 시나리오 ---
DEMO_QUERIES: list[str] = [
    "영업팀 직원 목록을 보여줘",
    "이서연의 휴가 잔여일이 몇 일이야?",
    "이번 달 전체 매출 합계는?",
    "연차 사용 규정이 어떻게 돼?",
    "이서연의 휴가 잔여일과 연차 규정을 함께 알려줘",
]


def print_separator(char: str = "=", width: int = 60) -> None:
    """구분선을 출력합니다.

    Args:
        char: 구분선에 사용할 문자
        width: 구분선 길이
    """
    print(char * width)


def print_result(result: dict) -> None:
    """Agent 실행 결과를 가독성 있게 출력합니다.

    Args:
        result: Agent.run()이 반환한 결과 딕셔너리
    """
    print(f"\n[라우팅 경로] {result.get('route', 'unknown')}")
    if result.get("from_cache"):
        print("[캐시] 이전 응답을 재사용했습니다.")

    print("\n[AI 답변]")
    print(result["output"])

    steps = result.get("intermediate_steps", [])
    if steps:
        print(f"\n[도구 호출 내역] {len(steps)}건")
        for i, (action, tool_output) in enumerate(steps, 1):
            tool_name = getattr(action, "tool", str(action))
            print(f"  {i}. {tool_name} → {str(tool_output)[:100]}...")


def run_demo_mode(agent: object) -> None:
    """사전 정의된 시나리오를 순서대로 실행합니다.

    Args:
        agent: ConnectHRAgent 인스턴스
    """
    print("\n대화형 모드를 종료하고 데모 시나리오를 실행합니다.")
    print(f"총 {len(DEMO_QUERIES)}개 시나리오 실행\n")

    for i, query in enumerate(DEMO_QUERIES, 1):
        print_separator()
        print(f"[시나리오 {i}/{len(DEMO_QUERIES)}] {query}")
        print_separator("-")

        try:
            result = agent.run(query, use_cache=(i > 1))
            print_result(result)
        except Exception as exc:
            logger.error("[main] 시나리오 %d 실행 오류: %s", i, exc)
            print(f"오류 발생: {exc}")

        print()


def run_interactive_mode(agent: object) -> None:
    """사용자와 대화형으로 질문을 주고받는 CLI를 실행합니다.

    Args:
        agent: ConnectHRAgent 인스턴스
    """
    print("\nQ/A 사내 AI AI 비서가 준비되었습니다.")
    print("종료하려면 'q' 또는 'quit'를 입력하십시오.")
    print("데모 시나리오를 보려면 'demo'를 입력하십시오.")
    print("캐시 통계를 보려면 'stats'를 입력하십시오.")
    print_separator()

    chat_history: list = []

    while True:
        try:
            user_input = input("\n질문: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n종료합니다.")
            break

        if not user_input:
            continue

        if user_input.lower() in ("q", "quit", "exit"):
            print("종료합니다.")
            break

        if user_input.lower() == "demo":
            run_demo_mode(agent)
            continue

        if user_input.lower() == "stats":
            print("\n[응답 캐시 통계]")
            print(response_cache.stats())
            print("\n[임베딩 캐시 통계]")
            print(embedding_cache.stats())
            print("\n[토큰 사용량 요약]")
            print(token_tracker.summary())
            continue

        # --- INPUT ---
        print_separator("-")

        try:
            # --- PROCESS ---
            result = agent.run(query=user_input, chat_history=chat_history)
            print_result(result)

            # 대화 히스토리 업데이트 (멀티턴)
            from langchain_core.messages import HumanMessage, AIMessage
            chat_history.append(HumanMessage(content=user_input))
            chat_history.append(AIMessage(content=result["output"]))

            # 히스토리 최대 10턴 유지
            if len(chat_history) > 20:
                chat_history = chat_history[-20:]

        except Exception as exc:
            logger.error("[main] 질문 처리 오류: %s", exc)
            print(f"\n처리 중 오류가 발생했습니다: {exc}")


def main() -> None:
    """메인 실행 함수.

    Agent를 초기화하고 대화형 CLI를 시작합니다.
    """
    print_separator()
    print("Q/A 사내 AI AI 비서 — CH09 LangChain 연결 전략 예제")
    print_separator()

    # --- INPUT: 환경 확인 ---
    provider = os.getenv("LLM_PROVIDER", "ollama")
    model = os.getenv("OLLAMA_MODEL", os.getenv("OPENAI_MODEL", "deepseek-r1:8b"))
    print(f"LLM 제공자: {provider} | 모델: {model}")

    # --- PROCESS: Agent 초기화 ---
    try:
        agent = get_agent()
    except SystemExit:
        raise
    except Exception as exc:
        print(f"\nAgent 초기화에 실패했습니다: {exc}")
        print("환경 설정을 확인하고 다시 시도하십시오. (.env.example 참조)")
        sys.exit(1)

    # --- OUTPUT: CLI 실행 ---
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_demo_mode(agent)
    else:
        run_interactive_mode(agent)

    # 실행 후 통계 출력
    print_separator()
    print("\n[실행 통계]")
    summary = token_tracker.summary()
    print(f"  총 호출 횟수: {summary['total_calls']}")
    print(f"  총 토큰 사용량: {summary['total_tokens']}")
    print(f"  평균 응답 시간: {summary['avg_latency_ms']:.0f}ms")
    cache_stats = response_cache.stats()
    print(f"  캐시 적중률: {cache_stats['hit_rate_percent']}%")


if __name__ == "__main__":
    main()
