"""
개발 환경 설치 상태 점검 스크립트.

Ollama 실행 여부, 모델 다운로드, PostgreSQL 연결,
Python 버전, ChromaDB 임포트를 순서대로 점검하고
PASS/FAIL 결과를 출력합니다.

실행 방법:
    python src/setup_check.py
"""

import sys
import importlib
from pathlib import Path

# 상위 디렉토리를 경로에 추가 (src/ 내에서 env_config 임포트)
sys.path.insert(0, str(Path(__file__).parent))

import requests
from env_config import load_env, build_config, AppConfig

# --- 상수 정의 ---
REQUIRED_PYTHON_MAJOR: int = 3
REQUIRED_PYTHON_MINOR: int = 11
CHECK_TIMEOUT_SEC: int = 5  # HTTP 요청 타임아웃 (초)


def check_python_version() -> tuple[bool, str]:
    """Python 버전이 3.11 이상인지 확인합니다.

    Returns:
        (통과 여부, 상세 메시지) 튜플
    """
    # --- Input ---
    major = sys.version_info.major
    minor = sys.version_info.minor
    version_str = f"{major}.{minor}.{sys.version_info.micro}"

    # --- Process ---
    is_pass = (major, minor) >= (REQUIRED_PYTHON_MAJOR, REQUIRED_PYTHON_MINOR)

    # --- Output ---
    if is_pass:
        return True, f"버전: {version_str}"
    else:
        return False, (
            f"버전: {version_str} — Python 3.11 이상이 필요합니다. "
            "https://www.python.org/downloads/ 에서 최신 버전을 설치하십시오."
        )


def check_ollama_running(base_url: str) -> tuple[bool, str]:
    """Ollama 서버가 실행 중인지 HTTP 요청으로 확인합니다.

    Args:
        base_url: Ollama 서버 기본 URL (예: http://localhost:11434)

    Returns:
        (통과 여부, 상세 메시지) 튜플
    """
    # --- Input ---
    health_url = f"{base_url.rstrip('/')}/api/tags"

    # --- Process ---
    try:
        response = requests.get(health_url, timeout=CHECK_TIMEOUT_SEC)
        is_pass = response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False, (
            f"URL: {base_url} — Ollama 서버에 연결할 수 없습니다. "
            "터미널에서 'ollama serve' 명령을 실행한 뒤 다시 시도하십시오."
        )
    except requests.exceptions.Timeout:
        return False, (
            f"URL: {base_url} — 연결 시간 초과 ({CHECK_TIMEOUT_SEC}초). "
            "Ollama 서버가 응답하지 않습니다."
        )

    # --- Output ---
    if is_pass:
        return True, f"URL: {base_url}"
    else:
        return False, f"URL: {base_url} — 응답 코드: {response.status_code}"


def check_ollama_model(base_url: str, model_name: str) -> tuple[bool, str]:
    """지정된 Ollama 모델이 로컬에 다운로드되어 있는지 확인합니다.

    Args:
        base_url: Ollama 서버 기본 URL
        model_name: 확인할 모델 이름 (예: deepseek-r1)

    Returns:
        (통과 여부, 상세 메시지) 튜플
    """
    # --- Input ---
    tags_url = f"{base_url.rstrip('/')}/api/tags"

    # --- Process ---
    try:
        response = requests.get(tags_url, timeout=CHECK_TIMEOUT_SEC)
        if response.status_code != 200:
            return False, (
                f"모델: {model_name} — Ollama 태그 목록을 가져올 수 없습니다. "
                "먼저 Ollama 실행 여부를 확인하십시오."
            )

        data = response.json()
        available_models: list[str] = [m["name"] for m in data.get("models", [])]

        # 모델명 앞부분만 비교 (예: deepseek-r1 이면 deepseek-r1:latest 도 허용)
        is_pass = any(
            m == model_name or m.startswith(f"{model_name}:")
            for m in available_models
        )

    except requests.exceptions.RequestException as e:
        return False, f"모델: {model_name} — 요청 중 오류 발생: {e}"

    # --- Output ---
    if is_pass:
        return True, f"모델: {model_name}"
    else:
        return False, (
            f"모델: {model_name} — 다운로드된 모델 목록: {available_models or '없음'}. "
            f"'ollama pull {model_name}' 명령으로 모델을 다운로드하십시오."
        )


def check_postgres_connection(
    host: str,
    port: int,
    dbname: str,
    user: str,
    password: str,
) -> tuple[bool, str]:
    """PostgreSQL에 실제로 연결을 시도하여 접속 가능 여부를 확인합니다.

    Args:
        host: PostgreSQL 호스트 주소
        port: 포트 번호
        dbname: 데이터베이스명
        user: 사용자 이름
        password: 비밀번호

    Returns:
        (통과 여부, 상세 메시지) 튜플
    """
    # --- Input ---
    try:
        import psycopg2
    except ImportError:
        return False, (
            "psycopg2 패키지가 설치되지 않았습니다. "
            "'pip install psycopg2-binary' 를 실행하십시오."
        )

    # --- Process ---
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
            connect_timeout=CHECK_TIMEOUT_SEC,
        )
        conn.close()
        is_pass = True
        detail = f"호스트: {host}:{port} / DB: {dbname}"
    except psycopg2.OperationalError as e:
        is_pass = False
        detail = (
            f"호스트: {host}:{port} / DB: {dbname} — 연결 실패: {e}. "
            "'docker-compose up -d' 명령으로 PostgreSQL 컨테이너를 시작하십시오."
        )

    # --- Output ---
    return is_pass, detail


def check_chromadb_import() -> tuple[bool, str]:
    """ChromaDB 패키지가 정상적으로 임포트되는지 확인합니다.

    Python 3.11 환경에서 동작이 보장됩니다.
    패키지 미설치 또는 의존성 오류 시 FAIL을 반환합니다.

    Returns:
        (통과 여부, 상세 메시지) 튜플
    """
    # --- Input ---
    module_name = "chromadb"

    # --- Process ---
    try:
        chromadb = importlib.import_module(module_name)
        version = getattr(chromadb, "__version__", "버전 정보 없음")
        is_pass = True
        detail = f"버전: {version}"
    except ImportError as e:
        is_pass = False
        detail = (
            f"임포트 실패 (패키지 미설치): {e}. "
            "'pip install chromadb' 명령으로 설치하십시오."
        )
    except Exception as e:
        # Pydantic 버전 충돌 등 임포트 시 발생하는 런타임 오류를 처리합니다.
        is_pass = False
        detail = (
            f"임포트 중 오류 발생: {type(e).__name__}: {e}. "
            "Python 3.11 환경에서 실행하고 있는지 확인하십시오. "
            "'pip install --upgrade chromadb pydantic' 을 시도해 보십시오."
        )

    # --- Output ---
    return is_pass, detail


def print_check_result(index: int, total: int, label: str, is_pass: bool, detail: str) -> None:
    """단일 점검 항목의 결과를 포맷에 맞춰 출력합니다.

    Args:
        index: 현재 항목 번호 (1부터 시작)
        total: 전체 항목 수
        label: 점검 항목 이름
        is_pass: 통과 여부
        detail: 상세 메시지
    """
    # --- Input / Process / Output ---
    status = "PASS" if is_pass else "FAIL"
    print(f"\n[{index}/{total}] {label}...")
    print(f"  {detail}")
    print(f"  결과: {status}")


def run_all_checks() -> int:
    """모든 환경 점검 항목을 순서대로 실행하고 결과를 요약합니다.

    각 항목은 독립적으로 실행되며, 하나가 실패해도 나머지 항목을 계속 점검합니다.

    Returns:
        실패한 항목 수. 0이면 전체 PASS.
    """
    # --- Input ---
    print("=== 개발 환경 점검 시작 ===")

    # 환경 변수 로딩 (.env 없어도 기본값으로 진행)
    load_env()

    try:
        config = build_config()
    except Exception as e:
        print(f"\n경고: 환경 변수 로딩 중 오류가 발생했습니다: {e}")
        print("기본값으로 점검을 진행합니다.")
        config = AppConfig()

    # --- Process ---
    # 각 항목을 독립적으로 실행하기 위해 함수 호출을 리스트 내부에서 직접 수행합니다.
    check_items: list[tuple[str, callable]] = [
        ("Python 버전 확인", check_python_version),
        ("Ollama 실행 여부 확인", lambda: check_ollama_running(config.ollama_base_url)),
        ("DeepSeek R1 모델 확인", lambda: check_ollama_model(config.ollama_base_url, config.ollama_model)),
        (
            "PostgreSQL 연결 테스트",
            lambda: check_postgres_connection(
                host=config.postgres_host,
                port=config.postgres_port,
                dbname=config.postgres_db,
                user=config.postgres_user,
                password=config.postgres_password,
            ),
        ),
        ("ChromaDB 임포트 테스트", check_chromadb_import),
    ]

    total = len(check_items)
    fail_count = 0

    for idx, (label, check_fn) in enumerate(check_items, start=1):
        try:
            is_pass, detail = check_fn()
        except Exception as e:
            is_pass = False
            detail = f"점검 중 예상치 못한 오류: {type(e).__name__}: {e}"

        print_check_result(idx, total, label, is_pass, detail)
        if not is_pass:
            fail_count += 1

    # --- Output ---
    pass_count = total - fail_count
    print(f"\n=== 점검 완료 ===")
    print(f"PASS: {pass_count} / {total}")

    if fail_count == 0:
        print("모든 환경 항목이 정상입니다. 다음 챕터로 진행하십시오.")
    else:
        print(
            f"FAIL 항목 {fail_count}개가 있습니다. "
            "위의 안내 메시지를 참고하여 문제를 해결한 뒤 다시 실행하십시오."
        )

    return fail_count


if __name__ == "__main__":
    fail_count = run_all_checks()
    # 실패 항목이 있으면 종료 코드 1로 반환 (CI/CD 연동 시 활용)
    sys.exit(0 if fail_count == 0 else 1)
