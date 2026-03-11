"""CH10 RAG 튜닝 — 듀얼모드 CLI 진입점.

두 가지 모드를 지원한다:
  (1) 에이전트 CLI: CH09과 동일한 대화형 Q/A 비서
  (2) 실험 메뉴: RAG 튜닝 실험 선택/실행

실행 방법:
    python -m src.main                 # 메인 메뉴 (모드 선택)
    python -m src.main --agent         # 에이전트 CLI 직접 실행
    python -m src.main --demo          # 에이전트 데모 시나리오
    python -m src.main --experiments   # 실험 메뉴 직접 실행
    python -m src.main --experiment 1  # 특정 실험 직접 실행
"""

import sys
import os
import logging
import importlib

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

# ===================================================================
# (1) 에이전트 CLI 모드 (CH09 동일)
# ===================================================================

DEMO_QUERIES: list[str] = [
    "영업팀 직원 목록을 보여줘",
    "이서연의 휴가 잔여일이 몇 일이야?",
    "이번 달 전체 매출 합계는?",
    "연차 사용 규정이 어떻게 돼?",
    "이서연의 휴가 잔여일과 연차 규정을 함께 알려줘",
]


def print_separator(char: str = "=", width: int = 60) -> None:
    """구분선을 출력합니다."""
    print(char * width)


def print_result(result: dict) -> None:
    """Agent 실행 결과를 가독성 있게 출력합니다."""
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
    """사전 정의된 시나리오를 순서대로 실행합니다."""
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
    """사용자와 대화형으로 질문을 주고받는 CLI를 실행합니다."""
    print("\nQ/A 사내 AI 비서가 준비되었습니다.")
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

        print_separator("-")

        try:
            result = agent.run(query=user_input, chat_history=chat_history)
            print_result(result)

            from langchain_core.messages import HumanMessage, AIMessage
            chat_history.append(HumanMessage(content=user_input))
            chat_history.append(AIMessage(content=result["output"]))

            if len(chat_history) > 20:
                chat_history = chat_history[-20:]

        except Exception as exc:
            logger.error("[main] 질문 처리 오류: %s", exc)
            print(f"\n처리 중 오류가 발생했습니다: {exc}")


def run_agent_cli(demo: bool = False) -> None:
    """에이전트 CLI를 시작합니다."""
    print_separator()
    print("Q/A 사내 AI 비서 — CH10 RAG 튜닝 예제")
    print_separator()

    provider = os.getenv("LLM_PROVIDER", "ollama")
    model = os.getenv("OLLAMA_MODEL", os.getenv("OPENAI_MODEL", "deepseek-r1:8b"))
    print(f"LLM 제공자: {provider} | 모델: {model}")

    try:
        agent = get_agent()
    except SystemExit:
        raise
    except Exception as exc:
        print(f"\nAgent 초기화에 실패했습니다: {exc}")
        print("환경 설정을 확인하고 다시 시도하십시오. (.env.example 참조)")
        sys.exit(1)

    if demo:
        run_demo_mode(agent)
    else:
        run_interactive_mode(agent)

    print_separator()
    print("\n[실행 통계]")
    summary = token_tracker.summary()
    print(f"  총 호출 횟수: {summary['total_calls']}")
    print(f"  총 토큰 사용량: {summary['total_tokens']}")
    print(f"  평균 응답 시간: {summary['avg_latency_ms']:.0f}ms")
    cache_stats = response_cache.stats()
    print(f"  캐시 적중률: {cache_stats['hit_rate_percent']}%")


# ===================================================================
# (2) 실험 메뉴 모드 (CH10 신규)
# ===================================================================

EXPERIMENTS = {
    "1": {
        "name": "청킹 전략 실험",
        "description": "Fixed-size vs Semantic 청킹 비교, 크기/오버랩 실험",
        "module": "tuning.chunk_experiment",
        "func": "run_all_experiments",
    },
    "2": {
        "name": "Retriever 튜닝 실험",
        "description": "k값(3/5/10), Threshold, Metadata Filtering 실험",
        "module": "tuning.retriever_experiment",
        "func": "run_all_retriever_experiments",
    },
    "3": {
        "name": "ReRanker 실험",
        "description": "Cross-Encoder 기반 top_k=20 → top_k=5 재정렬",
        "module": "tuning.reranker",
        "func": "run_reranker_experiment",
    },
    "4": {
        "name": "하이브리드 검색 실험",
        "description": "BM25 + Vector EnsembleRetriever, alpha 파라미터 실험",
        "module": "tuning.hybrid_search",
        "func": "run_hybrid_search_experiment",
    },
    "5": {
        "name": "고급 Retriever 실험",
        "description": "ParentDocument, SelfQuery, ContextualCompression 비교",
        "module": "tuning.advanced_retriever",
        "func": "run_advanced_retriever_experiment",
    },
    "6": {
        "name": "Query Rewrite 실험",
        "description": "HyDE, Multi-Query, 약어/동의어 확장",
        "module": "tuning.query_rewrite",
        "func": "run_query_rewrite_experiment",
    },
    "7": {
        "name": "문서 파싱 비교",
        "description": "라이브러리 vs vLLM(LLaVA) 파싱 전략 비교",
        "module": "tuning.document_parser",
        "func": "run_parser_comparison",
    },
    "8": {
        "name": "문서 캡처 파이프라인",
        "description": "PDF/DOCX/XLSX → 캡처(PNG) + 벡터DB 인제스천",
        "module": "tuning.document_capture",
        "func": "run_capture_pipeline",
    },
    "9": {
        "name": "답변 근거 시스템",
        "description": "비정형(문서+캡처) / 정형(DB) 답변 근거 데모",
        "module": "tuning.evidence_pipeline",
        "func": "run_evidence_demo",
    },
    "10": {
        "name": "평가 프레임워크 데모",
        "description": "Precision@k, Recall@k, 환각률, before/after 비교",
        "module": "src.eval_framework",
        "func": "run_full_evaluation_demo",
    },
}


def run_experiment(experiment_key: str) -> None:
    """선택한 실험을 실행합니다."""
    if experiment_key == "all":
        run_all_experiments()
        return

    if experiment_key not in EXPERIMENTS:
        print(f"잘못된 선택입니다: {experiment_key}")
        print(f"유효한 선택지: {', '.join(EXPERIMENTS.keys())}, all")
        return

    exp = EXPERIMENTS[experiment_key]
    print(f"\n실험 {experiment_key}: {exp['name']} 시작")

    try:
        module = importlib.import_module(exp["module"])
        func = getattr(module, exp["func"])
        func()
    except ModuleNotFoundError as e:
        print(f"모듈을 찾을 수 없습니다: {e}")
        print("requirements.txt에 따라 패키지를 설치하십시오:")
        print("  pip install -r requirements.txt")
    except Exception as e:
        print(f"실험 실행 중 오류 발생: {e}")
        raise


def run_all_experiments() -> None:
    """모든 실험을 순서대로 실행합니다."""
    print("\n전체 실험 순서 실행")
    print("주의: 전체 실행에는 임베딩 모델 다운로드로 인해 시간이 걸릴 수 있습니다.\n")

    for key in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
        exp = EXPERIMENTS[key]
        print(f"\n{'='*50}")
        print(f"실험 {key}: {exp['name']}")
        run_experiment(key)


def run_experiment_menu() -> None:
    """실험 선택 메뉴를 표시하고 실행합니다."""
    print_separator()
    print("CH10 RAG 튜닝 - 실험 선택 메뉴")
    print_separator()
    print("\n이 챕터에서는 RAG 품질을 개선하는 다양한 튜닝 기법을 실험합니다.")
    print("각 실험은 ChromaDB 없이 인메모리 샘플 데이터로 독립 실행 가능합니다.\n")

    print(f"{'번호':^6} {'실험 이름':<25} {'설명'}")
    print("-" * 70)
    for key, exp in EXPERIMENTS.items():
        print(f"  {key:<4} {exp['name']:<25} {exp['description']}")
    print(f"  {'all':<4} {'전체 실험 순서 실행':<25} {'모든 실험을 1~10 순서로 실행'}")
    print("-" * 70)

    try:
        choice = input("\n실험 번호를 입력하십시오 (1~10) 또는 'all' (전체 실행): ").strip().lower()
        if not choice:
            choice = "10"
        run_experiment(choice)
    except KeyboardInterrupt:
        print("\n\n실험이 취소되었습니다.")


# ===================================================================
# (3) 메인 메뉴 (듀얼모드)
# ===================================================================

def main() -> None:
    """메인 실행 함수.

    명령줄 인수에 따라 모드를 선택하거나, 대화형으로 모드를 선택한다.
    """
    # 명령줄 인수 처리
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "--agent":
            run_agent_cli(demo=False)
            return
        elif arg == "--demo":
            run_agent_cli(demo=True)
            return
        elif arg == "--experiments":
            run_experiment_menu()
            return
        elif arg == "--experiment":
            if len(sys.argv) > 2:
                run_experiment(sys.argv[2])
            else:
                print("실험 번호를 지정하십시오. 예: python -m src.main --experiment 1")
            return
        elif arg in EXPERIMENTS or arg == "all":
            # 하위 호환: 실험 번호 직접 전달
            run_experiment(arg)
            return

    # 대화형 모드 선택
    print_separator()
    print("CH10 RAG 튜닝 — 메인 메뉴")
    print_separator()
    print("\n  1. 에이전트 CLI  (Q/A 사내 AI 비서)")
    print("  2. 실험 메뉴    (RAG 튜닝 실험)")
    print("  3. 데모 모드    (에이전트 시나리오 자동 실행)")
    print()

    try:
        choice = input("모드를 선택하십시오 (1/2/3): ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n종료합니다.")
        return

    if choice == "1":
        run_agent_cli(demo=False)
    elif choice == "2":
        run_experiment_menu()
    elif choice == "3":
        run_agent_cli(demo=True)
    else:
        print(f"잘못된 선택입니다: {choice}")


if __name__ == "__main__":
    main()
