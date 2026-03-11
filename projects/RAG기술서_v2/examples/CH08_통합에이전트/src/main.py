"""CH08 통합 에이전트 진입점 — 10개 대표 시나리오 실행.

커넥트HR 사내 AI 비서가 다양한 질문 유형에 어떻게 대응하는지
10개 시나리오를 순서대로 실행하여 확인합니다.

시나리오 유형:
  - 정형 (structured): DB에서 직원/연차/매출 데이터 조회
  - 비정형 (unstructured): 사내 문서에서 정책/규정 검색
  - 복합 (hybrid): DB 조회 + 문서 검색을 모두 수행

실행 전 준비사항 (모두 필수):
  1. docker-compose up -d     (PostgreSQL)
  2. ollama serve             (Ollama 서버)
  3. ollama pull deepseek-r1  (모델 다운로드)
  4. CH06 예제 실행 완료     (ChromaDB 벡터 DB 구축)

챕터 8.4: 대표 질문 시나리오 10개 실습
"""

import sys
import os
from pathlib import Path

# src 폴더를 Python 경로에 추가 (상대 임포트 지원)
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from agent import IntegratedAgent, _check_ollama_available

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DB_NAME = os.getenv("POSTGRES_DB", "connecthr")

# ============================================================
# 10개 대표 시나리오 정의
# ============================================================

SCENARIOS: list[dict] = [
    {
        "id": 1,
        "type": "정형",
        "description": "직원 연차 조회",
        "question": "이서연 씨의 이번 달 남은 연차 일수는?",
    },
    {
        "id": 2,
        "type": "정형",
        "description": "부서 매출 조회",
        "question": "개발팀 2024년 1월 매출은 얼마인가요?",
    },
    {
        "id": 3,
        "type": "비정형",
        "description": "연차 신청 절차 문의",
        "question": "연차 신청은 어떻게 하나요?",
    },
    {
        "id": 4,
        "type": "비정형",
        "description": "육아휴직 규정 문의",
        "question": "육아휴직 규정이 어떻게 되나요?",
    },
    {
        "id": 5,
        "type": "정형",
        "description": "직원 급여 조회",
        "question": "김도현 팀장님의 기본 급여는?",
    },
    {
        "id": 6,
        "type": "복합",
        "description": "연차 사용 현황 + 연차 신청 방법",
        "question": "박민준 과장님이 올해 사용한 연차 일수와 연차 신청 방법을 알려주세요.",
    },
    {
        "id": 7,
        "type": "비정형",
        "description": "IT 보안 VPN 규정 문의",
        "question": "IT 보안 정책에서 VPN 사용 규정은?",
    },
    {
        "id": 8,
        "type": "정형",
        "description": "영업팀 4분기 매출 합계",
        "question": "2024년 4분기 영업팀 매출 합계는?",
    },
    {
        "id": 9,
        "type": "비정형",
        "description": "신입사원 온보딩 절차 문의",
        "question": "신입사원 온보딩 절차가 어떻게 되나요?",
    },
    {
        "id": 10,
        "type": "복합",
        "description": "직원 부서 조회 + 해당 부서 매출 조회",
        "question": "이서연의 부서와 그 부서의 올해 매출은?",
    },
]


def preflight_check() -> None:
    """실행 전 필수 서비스 연결을 점검합니다.

    Ollama, PostgreSQL, ChromaDB 세 가지를 순서대로 확인합니다.
    하나라도 준비되지 않으면 설정 방법을 안내하고 즉시 종료합니다.

    Raises:
        SystemExit: 필수 서비스 미준비 시
    """

    # --- Input ---
    print("  [사전 점검] 필수 서비스 연결 확인 중...")
    errors: list[str] = []

    # --- Process ---
    # 1. Ollama 확인
    if _check_ollama_available():
        print(f"  ✓ Ollama: {OLLAMA_BASE_URL}")
    else:
        errors.append(
            f"  ✗ Ollama 미연결 ({OLLAMA_BASE_URL})\n"
            "      → ollama serve 실행 후 재시도하십시오.\n"
            f"      → ollama pull {OLLAMA_MODEL} 로 모델도 다운로드하십시오."
        )

    # 2. PostgreSQL 확인
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
            user=os.getenv("POSTGRES_USER", "admin"),
            password=os.getenv("POSTGRES_PASSWORD", "password"),
            connect_timeout=3,
        )
        conn.close()
        print(f"  ✓ PostgreSQL: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    except Exception as e:
        errors.append(
            f"  ✗ PostgreSQL 미연결 ({DB_HOST}:{DB_PORT}/{DB_NAME}): {e}\n"
            "      → docker-compose up -d 실행 후 재시도하십시오."
        )

    # 3. ChromaDB 확인
    chroma_path = Path(CHROMA_PERSIST_DIR)
    if chroma_path.exists():
        print(f"  ✓ ChromaDB: {CHROMA_PERSIST_DIR}")
    else:
        errors.append(
            f"  ✗ ChromaDB 미구축 ({CHROMA_PERSIST_DIR})\n"
            "      → CH06 예제를 먼저 실행하십시오:\n"
            "        cd ../CH06_벡터DB구축 && python src/main.py"
        )

    # --- Output ---
    if errors:
        print()
        print("  [오류] 다음 서비스를 먼저 준비하십시오:")
        print()
        for err in errors:
            print(err)
        print()
        sys.exit(1)

    print("  [사전 점검] 모든 서비스 준비 완료.\n")


def print_banner() -> None:
    """실행 배너를 출력합니다."""

    print()
    print("=" * 65)
    print("  CH08 통합 에이전트 — MCP + RAG 통합 시나리오 실습")
    print("  커넥트HR 사내 AI 비서 (10개 대표 질문)")
    print("=" * 65)
    print()
    print("  에이전트 구성:")
    print("  - DB 도구 (MCP): 직원 정보, 연차 잔액, 부서 매출 조회")
    print("  - RAG 도구    : 사내 문서 (정책/규정/절차) 검색")
    print("  - 라우터      : 질문 유형 자동 분류 (정형/비정형/복합)")
    print()


def print_scenario_result(scenario: dict, result: dict) -> None:
    """시나리오 실행 결과를 출력합니다.

    Args:
        scenario: 시나리오 정의 딕셔너리
        result: 에이전트 실행 결과 딕셔너리
    """

    # --- Input ---
    sid = scenario["id"]
    s_type = scenario["type"]
    s_desc = scenario["description"]

    # --- Process ---
    print(f"\n{'─' * 65}")
    print(f"  시나리오 {sid:02d} [{s_type}] {s_desc}")
    print(f"{'─' * 65}")
    print(f"  질문 : {result['question']}")
    print(f"  분류 : {result['query_type']} (신뢰도 {result['confidence']:.0%}, 방법: {result['method']})")
    print(f"  모드 : {result['mode']}")
    print()
    print("  [답변]")
    # 답변 줄 단위로 들여쓰기 출력
    for line in result["answer"].split("\n"):
        print(f"  {line}")

    # --- Output ---
    # 콘솔 출력 완료


def run_all_scenarios(agent: IntegratedAgent) -> None:
    """10개 대표 시나리오를 순서대로 실행합니다.

    Args:
        agent: 초기화된 IntegratedAgent 인스턴스
    """

    # --- Input ---
    total = len(SCENARIOS)
    success_count = 0

    print(f"\n  총 {total}개 시나리오를 실행합니다.")

    # --- Process ---
    for scenario in SCENARIOS:
        question = scenario["question"]
        try:
            result = agent.run(question)
            print_scenario_result(scenario, result)
            success_count += 1
        except ValueError as e:
            print(f"\n  [오류] 시나리오 {scenario['id']}: {e}")
        except Exception as e:
            print(f"\n  [오류] 시나리오 {scenario['id']} 실행 중 예외 발생: {e}")

    # --- Output ---
    print()
    print("=" * 65)
    print(f"  실행 완료: {success_count}/{total}개 시나리오 성공")
    print("=" * 65)


def main() -> None:
    """CH08 통합 에이전트 메인 함수.

    에이전트를 초기화하고 10개 대표 시나리오를 순서대로 실행합니다.

    실행 전 준비사항 (모두 필수):
      1. docker-compose up -d     (PostgreSQL 실행)
      2. ollama serve             (Ollama 서버 실행)
      3. ollama pull deepseek-r1  (모델 다운로드)
      4. CH06 예제 실행 완료     (ChromaDB 벡터 DB 구축)
    """

    # --- Input ---
    print_banner()

    # --- Process ---
    # 사전 점검: 모든 서비스 연결 확인
    preflight_check()

    print("  에이전트 초기화 중...")
    try:
        agent = IntegratedAgent()
    except RuntimeError as e:
        print(f"  [오류] 에이전트 초기화 실패:\n  {e}")
        sys.exit(1)

    run_all_scenarios(agent)

    # --- Output ---
    print()
    print("  [완료] CH08 통합 에이전트 실습이 종료되었습니다.")
    print("  다음 챕터(CH09)에서 이 에이전트를 프로덕션 수준으로 발전시킵니다.")


if __name__ == "__main__":
    main()
