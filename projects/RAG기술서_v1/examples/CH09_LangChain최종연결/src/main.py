"""
CH09 LangChain 최종 연결 — 진입점.

AI 업무 비서 v2 대화 루프를 실행합니다.
사용자가 질문을 입력하면 LangChain AgentExecutor가 적절한 도구를 자동 선택하여
답변을 생성하고, 응답 시간과 캐시 상태를 표시합니다.

실행 방법:
    python src/main.py

종료 방법:
    'exit' 또는 'quit' 입력 후 Enter

전제 조건:
    - CH04 FastAPI 서버 (http://localhost:8000) 실행 중
    - CH07 ChromaDB 구축 완료
    - Ollama 서버 및 모델 준비 완료
"""

import sys
import uuid

from src.agent import build_agent, run_with_metrics
from src.config import AppConfig, load_config, setup_cache, setup_logging
from src.monitor import MetricsCollector


def print_header(config: AppConfig) -> None:
    """애플리케이션 시작 헤더를 콘솔에 출력합니다.

    모델 이름, 타임아웃, 캐시 활성화 여부 등 주요 설정을 표시합니다.

    Args:
        config: 애플리케이션 설정 객체.

    Returns:
        None
    """
    # --- Input ---
    model_name = config.llm.model
    timeout = config.llm.timeout
    cache_status = "ON" if config.enable_cache else "OFF"

    # --- Process ---
    print("=" * 50)
    print("  AI 업무 비서 v2 (LangChain Agent)")
    print("=" * 50)
    print(f"  설정: {model_name} | Timeout {timeout}s | 캐시 {cache_status}")
    print("  도구: 연차 조회 / 매출 조회 / 직원 정보 / 사내 문서 검색")
    print("  종료: 'exit' 또는 'quit' 입력")
    print("=" * 50)

    # --- Output ---


def run_conversation_loop(config: AppConfig) -> None:
    """대화 루프를 실행합니다.

    사용자 질문을 반복적으로 입력받아 에이전트에 전달하고 답변을 출력합니다.
    'exit' 또는 'quit' 입력 시 세션 통계를 출력하고 종료합니다.

    Args:
        config: 애플리케이션 설정 객체.

    Returns:
        None
    """
    # --- Input ---
    logger = setup_logging(config)
    collector = MetricsCollector()
    session_id = str(uuid.uuid4())[:8]

    # --- Process ---
    # 에이전트 초기화
    logger.info("에이전트 초기화 시작 — 세션 ID: %s", session_id)
    try:
        agent = build_agent(config)
        logger.info("에이전트 초기화 완료")
    except RuntimeError as exc:
        print(f"\n에이전트 초기화에 실패했습니다: {exc}")
        print("설정을 확인하고 다시 시도하십시오.")
        sys.exit(1)

    print("\n준비 완료. 질문을 입력하십시오.\n")

    # 대화 루프
    while True:
        try:
            user_input = input("질문: ").strip()
        except (KeyboardInterrupt, EOFError):
            # Ctrl+C 또는 입력 스트림 종료 처리
            print("\n\n인터럽트가 감지되었습니다. 세션을 종료합니다.")
            break

        # 빈 입력 무시
        if not user_input:
            continue

        # 종료 명령 처리
        if user_input.lower() in ("exit", "quit"):
            print("\n세션을 종료합니다.")
            break

        # 에이전트 실행 및 답변 출력
        print()
        answer = run_with_metrics(
            agent=agent,
            question=user_input,
            collector=collector,
            session_id=session_id,
        )
        print(f"\n답변: {answer}\n")
        print("-" * 50)

    # 세션 종료 시 통계 출력
    collector.print_summary()

    # --- Output ---


def main() -> None:
    """AI 업무 비서 v2 메인 진입점입니다.

    설정 로드 → 캐시 설정 → 헤더 출력 → 대화 루프 순서로 실행합니다.

    Returns:
        None
    """
    # --- Input ---
    config = load_config()

    # --- Process ---
    # 캐시 설정 (SQLiteCache 초기화)
    setup_cache(config)

    # 헤더 출력
    print_header(config)

    # 대화 루프 실행
    run_conversation_loop(config)

    # --- Output ---


if __name__ == "__main__":
    main()
