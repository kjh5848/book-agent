"""CH01 최종 완성본 미리보기 데모 스크립트.

이 책을 완독했을 때 완성되는 AI 업무 비서 시스템의 전체 아키텍처와
각 챕터에서 구현할 기능을 미리 확인합니다.
"""

import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv


# --- 상수 ---
STAGE_INFO: list[dict[str, str]] = [
    {
        "stage": "Stage 1: 비전 및 기초 (CH01-02)",
        "desc": "목표 확인 + DeepSeek-R1으로 기초 RAG 실습",
        "chapters": "CH01, CH02",
    },
    {
        "stage": "Stage 2: 인프라 및 표준화 (CH03-05)",
        "desc": "개발 환경 구축 + 베이스 시스템 확보 + 사내 문서 표준화",
        "chapters": "CH03, CH04, CH05",
    },
    {
        "stage": "Stage 3: 지식 검색 엔진 (CH06-07)",
        "desc": "벡터 DB 구축 + RAG Q&A 파이프라인 구현",
        "chapters": "CH06, CH07",
    },
    {
        "stage": "Stage 4: 지능형 에이전트 (CH08-10)",
        "desc": "MCP+RAG 통합 에이전트 + 프로덕션 연결 + 시스템 튜닝",
        "chapters": "CH08, CH09, CH10",
    },
]

CHAPTER_PREVIEW: list[dict[str, str]] = [
    {
        "ch": "CH01",
        "title": "이 책의 목표와 최종 완성본 미리보기",
        "feature": "전체 아키텍처 이해 + 최종 데모 체험",
    },
    {
        "ch": "CH02",
        "title": "DeepSeek-R1으로 시작하는 기초 RAG 정복",
        "feature": "LLM 환각 체험 + 기초 RAG 구현",
    },
    {
        "ch": "CH03",
        "title": "개발 환경 구축",
        "feature": "Ollama + PostgreSQL + Python 가상환경 설정",
    },
    {
        "ch": "CH04",
        "title": "베이스 시스템 확보",
        "feature": "사내 DB 스키마 분석 + CRUD API + MCP 개념",
    },
    {
        "ch": "CH05",
        "title": "사내 문서 표준화",
        "feature": "PDF/Word/Markdown 전처리 파이프라인",
    },
    {
        "ch": "CH06",
        "title": "벡터 DB 구축",
        "feature": "텍스트 추출 + 청킹 + 임베딩 + ChromaDB 저장",
    },
    {
        "ch": "CH07",
        "title": "RAG Q&A 엔진 구현",
        "feature": "LangChain RAG 파이프라인 + 출처 표시",
    },
    {
        "ch": "CH08",
        "title": "통합 에이전트 설계 (MCP + RAG)",
        "feature": "정형 DB + 비정형 문서 동시 질의",
    },
    {
        "ch": "CH09",
        "title": "LangChain 최종 연결",
        "feature": "Router/Agent/RAG Chain/MCP Tool 프로덕션 연결",
    },
    {
        "ch": "CH10",
        "title": "RAG 시스템 튜닝",
        "feature": "ReRanker + Hybrid Search + 평가 체계",
    },
]

MOCK_QA_PAIRS: list[dict[str, str]] = [
    {
        "question": "김철수 사원의 남은 연차는 며칠인가요?",
        "source": "정형 데이터 (PostgreSQL)",
        "route": "MCP Tool -> SQL 조회",
        "answer": (
            "김철수 사원의 남은 연차는 12일입니다. "
            "(2024년 기준, 총 15일 중 3일 사용)"
        ),
    },
    {
        "question": "연차 규정에서 특별휴가 신청 조건은 무엇인가요?",
        "source": "비정형 데이터 (ChromaDB 벡터 검색)",
        "route": "RAG Chain -> 문서 검색 -> LLM 생성",
        "answer": (
            "특별휴가는 결혼, 출산, 사망 등 경조사 발생 시 신청 가능합니다. "
            "최소 3일 전 팀장 승인이 필요합니다. "
            "[출처: HR_취업규칙_v1.0.pdf, 15페이지]"
        ),
    },
    {
        "question": "올해 3분기 영업팀 매출 현황과 관련 보고서를 알려주세요.",
        "source": "정형 + 비정형 (복합 질의)",
        "route": "AI 에이전트 -> MCP Tool + RAG Chain 동시 호출",
        "answer": (
            "3분기 영업팀 매출: 2억 3,500만 원 (목표 대비 94%). "
            "관련 보고서에 따르면 계약 지연이 주요 원인으로 분석됩니다. "
            "[출처: FIN_매출현황_v1.0.pdf, 3페이지]"
        ),
    },
]


def load_env_config() -> dict[str, str]:
    """환경 변수를 로드하여 설정 딕셔너리를 반환합니다.

    .env 파일 또는 시스템 환경 변수에서 설정값을 읽어옵니다.

    Returns:
        설정값 딕셔너리 (ollama_base_url, ollama_model, demo_mode)
    """
    # --- Input ---
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()

    # --- Process ---
    config = {
        "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        "ollama_model": os.getenv("OLLAMA_MODEL", "deepseek-r1"),
        "demo_mode": os.getenv("DEMO_MODE", "mock"),
    }

    # --- Output ---
    return config


def check_ollama_connection(base_url: str) -> bool:
    """Ollama 서버 연결 상태를 확인합니다.

    Args:
        base_url: Ollama 서버 주소 (예: http://localhost:11434)

    Returns:
        연결 성공 여부 (True: 연결됨, False: 연결 안 됨)
    """
    # --- Input ---
    health_url = f"{base_url}/api/tags"

    # --- Process ---
    try:
        response = requests.get(health_url, timeout=3)
        connected = response.status_code == 200
    except (requests.ConnectionError, requests.Timeout):
        connected = False

    # --- Output ---
    return connected


def print_separator(char: str = "=", width: int = 60) -> None:
    """구분선을 출력합니다.

    Args:
        char: 구분선에 사용할 문자 (기본값: '=')
        width: 구분선 너비 (기본값: 60)
    """
    print(char * width)


def print_connection_status(base_url: str, model: str, is_connected: bool) -> None:
    """Ollama 연결 상태를 사용자 친화적으로 출력합니다.

    Args:
        base_url: Ollama 서버 주소
        model: 사용할 LLM 모델 이름
        is_connected: 연결 성공 여부
    """
    # --- Input ---
    status_icon = "[연결됨]" if is_connected else "[연결 안 됨]"
    status_msg = "정상 연결" if is_connected else "오프라인 (데모 모드로 계속 진행)"

    # --- Process ---
    print_separator()
    print("  Ollama 연결 상태 확인")
    print_separator()
    print(f"  서버 주소  : {base_url}")
    print(f"  모델       : {model}")
    print(f"  상태       : {status_icon} {status_msg}")

    if not is_connected:
        print()
        print("  [안내] Ollama가 실행되지 않아도 이 데모는 정상 동작합니다.")
        print("  [안내] 실제 LLM 응답은 CH02부터 단계별로 구현합니다.")

    # --- Output ---
    print_separator()
    print()


def print_architecture_diagram() -> None:
    """전체 시스템 아키텍처를 ASCII 다이어그램으로 출력합니다."""
    # --- Input ---
    diagram = """
  +---------------------------------------------------------+
  |              AI 업무 비서 전체 시스템 아키텍처              |
  +---------------------------------------------------------+
  |                                                         |
  |   [사용자 질문]                                          |
  |        |                                               |
  |        v                                               |
  |   [LangChain Agent]  <-- 질문 유형 분석 및 라우팅         |
  |        |                                               |
  |   +----+----+                                          |
  |   |         |                                          |
  |   v         v                                          |
  | [MCP      [RAG                                         |
  |  Tool]     Chain]                                      |
  |   |         |                                          |
  |   v         v                                          |
  | [PostgreSQL] [ChromaDB]                                |
  | (정형 데이터)  (비정형 문서)                              |
  |   |         |                                          |
  |   +----+----+                                          |
  |        |                                               |
  |        v                                               |
  |   [DeepSeek R1] <-- 최종 응답 생성 (Ollama 로컬 실행)    |
  |        |                                               |
  |        v                                               |
  |   [최종 답변 + 출처]                                     |
  |                                                         |
  +---------------------------------------------------------+
    """

    # --- Process ---
    print_separator()
    print("  시스템 아키텍처 한눈에 보기")
    print_separator()

    # --- Output ---
    print(diagram)


def print_stage_roadmap() -> None:
    """챕터별 학습 로드맵을 단계별로 출력합니다."""
    # --- Input ---
    # STAGE_INFO 상수 사용

    # --- Process ---
    print_separator()
    print("  이 책의 학습 로드맵 (4단계)")
    print_separator()
    print()

    for idx, stage in enumerate(STAGE_INFO, start=1):
        print(f"  [{idx}단계] {stage['stage']}")
        print(f"         -> {stage['desc']}")
        print(f"         -> 챕터: {stage['chapters']}")
        print()

    # --- Output ---
    print_separator()
    print()


def print_chapter_preview() -> None:
    """각 챕터에서 구현할 핵심 기능을 미리보기로 출력합니다."""
    # --- Input ---
    # CHAPTER_PREVIEW 상수 사용

    # --- Process ---
    print_separator()
    print("  챕터별 구현 기능 미리보기")
    print_separator()
    print()

    for item in CHAPTER_PREVIEW:
        print(f"  {item['ch']} | {item['title']}")
        print(f"       기능: {item['feature']}")
        print()

    # --- Output ---
    print_separator()
    print()


def simulate_qa_flow(qa: dict[str, str], delay: float = 0.3) -> None:
    """단일 Q&A 흐름을 시뮬레이션하여 출력합니다.

    Args:
        qa: 질문/출처/라우팅/답변 정보를 담은 딕셔너리
        delay: 단계별 출력 딜레이 (초, 기본값: 0.3)
    """
    # --- Input ---
    question = qa["question"]
    source = qa["source"]
    route = qa["route"]
    answer = qa["answer"]

    # --- Process ---
    print(f"  [질문] {question}")
    time.sleep(delay)

    print(f"  [데이터 출처] {source}")
    time.sleep(delay)

    print(f"  [처리 경로] {route}")
    time.sleep(delay)

    print()
    print("  [AI 답변]")
    print(f"  {answer}")
    time.sleep(delay)

    # --- Output ---
    print()


def print_mock_qa_demo() -> None:
    """최종 Q&A 시스템 흐름을 mock 데이터로 시뮬레이션합니다.

    실제 LLM 없이도 동작하며, 정형/비정형/복합 질의 3가지 유형을 시연합니다.
    """
    # --- Input ---
    # MOCK_QA_PAIRS 상수 사용

    # --- Process ---
    print_separator()
    print("  최종 완성 시스템 Q&A 데모 (Mock 시뮬레이션)")
    print_separator()
    print()
    print("  [안내] 이 데모는 실제 LLM 없이 동작하는 시뮬레이션입니다.")
    print("  [안내] 이 책을 완독하면 아래와 같은 실제 응답을 받을 수 있습니다.")
    print()

    for idx, qa in enumerate(MOCK_QA_PAIRS, start=1):
        print(f"  --- 시나리오 {idx} ---")
        simulate_qa_flow(qa)

    # --- Output ---
    print_separator()
    print()


def print_completion_message() -> None:
    """데모 완료 메시지와 다음 단계 안내를 출력합니다."""
    # --- Input ---
    # 없음

    # --- Process / Output ---
    print_separator()
    print("  이 책을 마치면 할 수 있는 것")
    print_separator()
    print()
    print("  [1] 사내 문서(PDF/Word/Markdown) 를 벡터 DB에 자동 색인")
    print("  [2] 자연어 질문으로 사내 규정 즉시 검색 (30초 이내)")
    print("  [3] 정형 DB + 비정형 문서를 동시에 질의하는 통합 에이전트 운영")
    print("  [4] 출처 표시가 포함된 신뢰 가능한 AI 답변 제공")
    print("  [5] ReRanker, Hybrid Search로 검색 정확도 튜닝")
    print()
    print("  다음 단계: CH02 'DeepSeek-R1으로 시작하는 기초 RAG 정복' 으로 이동하세요.")
    print()
    print_separator()


def main() -> None:
    """CH01 미리보기 데모의 진입점.

    환경 변수를 로드하고 전체 아키텍처, 로드맵, 챕터 미리보기,
    Q&A 시뮬레이션을 순서대로 출력합니다.
    """
    # --- Input ---
    config = load_env_config()

    print()
    print("=" * 60)
    print("  AI 업무 비서 구축: RAG + MCP 실전 가이드")
    print("  CH01 최종 완성본 미리보기 데모")
    print("=" * 60)
    print()

    # --- Process ---
    # 1. Ollama 연결 상태 확인
    is_connected = check_ollama_connection(config["ollama_base_url"])
    print_connection_status(
        base_url=config["ollama_base_url"],
        model=config["ollama_model"],
        is_connected=is_connected,
    )

    # 2. 전체 시스템 아키텍처 출력
    print_architecture_diagram()

    # 3. 학습 로드맵 출력
    print_stage_roadmap()

    # 4. 챕터별 기능 미리보기 출력
    print_chapter_preview()

    # 5. Q&A 흐름 시뮬레이션
    print_mock_qa_demo()

    # 6. 완료 메시지
    print_completion_message()

    # --- Output ---
    print("  데모 실행 완료.")
    print()


if __name__ == "__main__":
    main()
