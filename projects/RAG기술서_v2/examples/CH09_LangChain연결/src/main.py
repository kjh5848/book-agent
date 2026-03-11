"""CH09 메인 진입점 — 프로덕션 수준 에이전트 실행.

AgentConfig를 로드하고 로깅·캐시·토큰 추적기를 초기화한 뒤,
5개 테스트 질문을 실행합니다.
실행 완료 후 토큰 사용 리포트를 출력하고
outputs/session_log.json 파일로 저장합니다.

챕터 9.1~9.4: 전체 통합 실행 예시
"""

import json
import sys
import time
from pathlib import Path

# 현재 스크립트 위치를 sys.path에 추가 (모듈 import 보장)
_SRC_DIR = Path(__file__).parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from dotenv import load_dotenv

from agent_config import AgentConfig, build_agent
from monitoring import ResponseCache, TokenUsageTracker, setup_logging

load_dotenv()

# ============================================================
# 테스트 질문 목록
# ============================================================

TEST_QUESTIONS: list[str] = [
    "이서연의 현재 잔여 연차는 며칠입니까?",
    "개발팀에 소속된 직원 목록을 알려주십시오.",
    "영업팀의 2024년 연간 매출 합계는 얼마입니까?",
    "김도현 팀장의 직급과 기본급을 알려주십시오.",
    "이서연의 현재 잔여 연차는 며칠입니까?",  # 캐시 히트 확인용 중복 질문
]

# ============================================================
# 출력 경로
# ============================================================

OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
SESSION_LOG_PATH = OUTPUT_DIR / "session_log.json"
TOKEN_REPORT_PATH = OUTPUT_DIR / "token_report.json"


def _print_banner() -> None:
    """실행 시작 배너를 출력합니다."""
    print("=" * 60)
    print("  CH09 LangChain 최종 연결 — 프로덕션 에이전트 실행")
    print("  커넥트HR AI 업무 비서 (운영 설정 적용)")
    print("=" * 60)
    print()


def _print_result(idx: int, result: dict) -> None:
    """단일 질문 처리 결과를 출력합니다.

    Args:
        idx:    질문 순번 (1-based)
        result: run() 반환 딕셔너리
    """

    # --- Input ---
    question = result["question"]
    answer   = result["answer"]
    mode     = result["mode"]
    cached   = result.get("from_cache", False)

    # --- Process ---
    cache_tag = " [캐시 히트]" if cached else ""
    print(f"[Q{idx}]{cache_tag} {question}")
    print(f"  모드: {mode}")
    print(f"  답변: {answer}")
    print()

    # --- Output ---
    # 사이드 이펙트: 콘솔 출력


def main() -> None:
    """프로덕션 에이전트를 초기화하고 테스트 질문을 실행합니다.

    Raises:
        SystemExit: 치명적 오류 발생 시 종료 코드 1로 종료
    """

    # --- Input ---
    _print_banner()

    # 1단계: 운영 설정 로드
    try:
        config = AgentConfig()
    except ValueError as exc:
        print(f"[오류] 설정 값이 올바르지 않습니다: {exc}")
        print(".env 파일의 값을 확인하십시오. (.env.example 참조)")
        sys.exit(1)

    # --- Process ---
    # 2단계: 로깅 초기화
    logger = setup_logging(
        log_level=config.log_level,
        log_file=config.log_file,
    )
    logger.info("CH09 에이전트 시작")
    logger.info(
        "설정: 모델=%s, timeout=%ds, retries=%d, cache_ttl=%ds",
        config.ollama_model,
        config.llm_timeout,
        config.llm_max_retries,
        config.cache_ttl,
    )

    # 3단계: 모니터링 컴포넌트 초기화
    cache = ResponseCache(maxsize=256, ttl=config.cache_ttl)
    token_tracker = TokenUsageTracker()

    # 4단계: 에이전트 빌드
    print("에이전트를 초기화합니다...")
    agent = build_agent(config=config, cache=cache, token_tracker=token_tracker)
    print(f"초기화 완료: {'Mock 모드' if agent.is_mock_mode else 'Ollama 모드'}")
    print()

    # 5단계: 테스트 질문 실행
    print(f"총 {len(TEST_QUESTIONS)}개 질문을 실행합니다.")
    print("-" * 60)

    session_results: list[dict] = []
    total_start = time.perf_counter()

    for idx, question in enumerate(TEST_QUESTIONS, start=1):
        try:
            result = agent.run(question)
            _print_result(idx, result)
            session_results.append(
                {
                    "index":      idx,
                    "question":   result["question"],
                    "answer":     result["answer"],
                    "mode":       result["mode"],
                    "from_cache": result.get("from_cache", False),
                }
            )
        except ValueError as exc:
            logger.warning("질문 처리 중 오류 (Q%d): %s", idx, exc)
            session_results.append(
                {
                    "index":    idx,
                    "question": question,
                    "error":    str(exc),
                    "mode":     "error",
                }
            )

    total_elapsed = time.perf_counter() - total_start

    # 6단계: 토큰 사용 리포트 출력
    print("=" * 60)
    print("  토큰 사용 리포트")
    print("=" * 60)
    token_summary = token_tracker.get_summary()
    print(f"  총 LLM 호출 횟수:  {token_summary['total_calls']}회")
    print(f"  총 입력 토큰:      {token_summary['total_prompt_tokens']:,}")
    print(f"  총 생성 토큰:      {token_summary['total_completion_tokens']:,}")
    print(f"  총 토큰:           {token_summary['total_tokens']:,}")
    print(f"  추정 비용:         {token_summary['estimated_cost_krw']:.2f}원 (로컬 LLM)")
    print()

    cache_stats = cache.get_stats()
    print("  캐시 통계")
    print(f"  - 히트:    {cache_stats['hits']}회")
    print(f"  - 미스:    {cache_stats['misses']}회")
    print(f"  - 히트율:  {cache_stats['hit_rate'] * 100:.1f}%")
    print()
    print(f"  전체 실행 시간: {total_elapsed:.2f}초")
    print("=" * 60)

    # 7단계: 세션 로그 저장
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    session_log = {
        "session_info": {
            "model":         config.ollama_model,
            "total_elapsed": round(total_elapsed, 3),
            "question_count": len(TEST_QUESTIONS),
        },
        "results":       session_results,
        "token_summary": token_summary,
        "cache_stats":   cache_stats,
    }

    with open(SESSION_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(session_log, f, ensure_ascii=False, indent=2)

    token_tracker.save_report(str(TOKEN_REPORT_PATH))

    logger.info("세션 로그 저장 완료: %s", SESSION_LOG_PATH)
    logger.info("토큰 리포트 저장 완료: %s", TOKEN_REPORT_PATH)
    print(f"\n세션 로그: {SESSION_LOG_PATH}")
    print(f"토큰 리포트: {TOKEN_REPORT_PATH}")

    # --- Output ---
    # 사이드 이펙트: outputs/ 파일 저장


if __name__ == "__main__":
    main()
