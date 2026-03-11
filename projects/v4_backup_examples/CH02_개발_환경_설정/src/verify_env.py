"""개발 환경 검증 모듈.

Python 버전, Docker, Ollama, PostgreSQL 네 가지 항목을 순서대로 점검하고
각 항목의 PASS / FAIL 결과를 터미널에 출력합니다.
모든 항목이 PASS여야 다음 챕터 실습을 진행할 수 있습니다.
"""

import subprocess
import sys

import psycopg2
import requests
from dotenv import load_dotenv
import os

load_dotenv()


# ─── 결과 출력 헬퍼 ──────────────────────────────────────────────────────────

def _print_pass(item: str, detail: str = "") -> None:
    """PASS 메시지를 초록색 체크마크와 함께 출력합니다.

    Args:
        item: 검증 항목 이름
        detail: 부가 정보 (버전, URL 등)
    """
    suffix = f"  ({detail})" if detail else ""
    print(f"  [PASS] {item}{suffix}")


def _print_fail(item: str, reason: str, fix: str) -> None:
    """FAIL 메시지를 원인과 해결 방법과 함께 출력합니다.

    Args:
        item: 검증 항목 이름
        reason: 실패 원인 설명
        fix: 독자가 취해야 할 조치 안내
    """
    print(f"  [FAIL] {item}")
    print(f"         원인  : {reason}")
    print(f"         해결  : {fix}")


# ─── 검증 함수 ───────────────────────────────────────────────────────────────

def check_python_version() -> bool:
    """Python 버전이 3.10 이상인지 확인합니다.

    현재 실행 중인 Python 인터프리터의 버전 정보를 sys.version_info로 읽어
    메이저.마이너 버전이 (3, 10) 이상인지 비교합니다.

    Returns:
        Python 3.10+ 이면 True, 미만이면 False

    Example:
        >>> result = check_python_version()
        # Python 3.11.9 인 경우 True 반환
    """
    # === INPUT ===
    major = sys.version_info.major
    minor = sys.version_info.minor
    version_str = f"{major}.{minor}.{sys.version_info.micro}"

    # === PROCESS ===
    is_ok = (major, minor) >= (3, 10)

    # === OUTPUT ===
    if is_ok:
        _print_pass("Python 버전", version_str)
    else:
        _print_fail(
            "Python 버전",
            reason=f"현재 버전이 {version_str}입니다. Python 3.10 이상이 필요합니다.",
            fix="https://www.python.org/downloads/ 에서 Python 3.10+ 를 다운로드하십시오.",
        )

    return is_ok


def check_docker() -> bool:
    """Docker 데몬이 실행 중인지 확인합니다.

    `docker version` 명령을 서브프로세스로 실행하여 반환 코드를 확인합니다.
    명령이 성공하면 Docker 가 설치·실행 중인 것으로 판단합니다.

    Returns:
        Docker 가 정상 동작하면 True, 그렇지 않으면 False
    """
    # === INPUT ===
    command = ["docker", "version", "--format", "{{.Client.Version}}"]

    # === PROCESS ===
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10,
        )
        is_ok = result.returncode == 0
        version_str = result.stdout.strip() if is_ok else ""
    except FileNotFoundError:
        is_ok = False
        version_str = ""
    except subprocess.TimeoutExpired:
        is_ok = False
        version_str = ""

    # === OUTPUT ===
    if is_ok:
        _print_pass("Docker", f"v{version_str}" if version_str else "실행 중")
    else:
        _print_fail(
            "Docker",
            reason="Docker 가 설치되지 않았거나 데몬이 실행 중이 아닙니다.",
            fix=(
                "Docker Desktop 을 설치하고 실행하십시오. "
                "(https://www.docker.com/products/docker-desktop/)"
            ),
        )

    return is_ok


def check_ollama() -> bool:
    """Ollama 서버에 HTTP 요청을 보내 연결 가능 여부를 확인합니다.

    .env 의 OLLAMA_BASE_URL 을 읽어 /api/tags 엔드포인트를 호출합니다.
    HTTP 200 응답이 오면 PASS, 연결 실패·타임아웃·오류 응답이면 FAIL 입니다.

    Returns:
        Ollama 서버가 응답하면 True, 그렇지 않으면 False
    """
    # === INPUT ===
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    tags_url = f"{base_url}/api/tags"

    # === PROCESS ===
    try:
        response = requests.get(tags_url, timeout=5)
        is_ok = response.status_code == 200
        if is_ok:
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
        else:
            model_names = []
    except requests.exceptions.ConnectionError:
        is_ok = False
        model_names = []
    except requests.exceptions.Timeout:
        is_ok = False
        model_names = []
    except Exception:
        is_ok = False
        model_names = []

    # === OUTPUT ===
    if is_ok:
        model_info = ", ".join(model_names) if model_names else "모델 없음"
        _print_pass("Ollama", f"{base_url}  모델: [{model_info}]")
    else:
        _print_fail(
            "Ollama",
            reason=f"'{base_url}' 에 연결할 수 없습니다.",
            fix=(
                "터미널에서 'ollama serve' 를 실행하십시오. "
                "미설치 시 https://ollama.com 에서 다운로드하십시오."
            ),
        )

    return is_ok


def check_postgresql() -> bool:
    """PostgreSQL 서버에 psycopg2 로 연결을 시도합니다.

    .env 의 POSTGRES_* 환경 변수로 연결 정보를 읽어 psycopg2.connect() 를
    호출합니다. 연결 성공 시 PASS, 연결 실패 시 FAIL 을 출력합니다.

    Returns:
        PostgreSQL 에 연결 가능하면 True, 그렇지 않으면 False
    """
    # === INPUT ===
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    dbname = os.getenv("POSTGRES_DB", "connect_hr")
    user = os.getenv("POSTGRES_USER", "connect_hr")
    password = os.getenv("POSTGRES_PASSWORD", "connect_hr_pass")

    # === PROCESS ===
    try:
        conn = psycopg2.connect(
            host=host,
            port=int(port),
            dbname=dbname,
            user=user,
            password=password,
            connect_timeout=5,
        )
        conn.close()
        is_ok = True
    except psycopg2.OperationalError as e:
        is_ok = False
        error_detail = str(e).strip()
    except Exception as e:
        is_ok = False
        error_detail = str(e).strip()

    # === OUTPUT ===
    if is_ok:
        _print_pass("PostgreSQL", f"{host}:{port}/{dbname}")
    else:
        _print_fail(
            "PostgreSQL",
            reason=f"'{host}:{port}/{dbname}' 에 연결할 수 없습니다.",
            fix=(
                "docker-compose.yml 이 있는 폴더에서 "
                "'docker compose up -d' 를 실행하여 PostgreSQL 컨테이너를 시작하십시오."
            ),
        )

    return is_ok


# ─── 메인 실행부 ─────────────────────────────────────────────────────────────

def run_all_checks() -> None:
    """모든 환경 검증 항목을 순서대로 실행하고 최종 결과를 출력합니다.

    Python → Docker → Ollama → PostgreSQL 순서로 각 항목을 점검합니다.
    전부 PASS 이면 '모든 환경 검증 완료' 메시지를 출력하고,
    하나라도 FAIL 이면 실패한 항목 수와 조치 안내를 출력합니다.
    """
    # === INPUT ===
    print("=" * 55)
    print("  커넥트HR AI 비서 — 개발 환경 검증")
    print("=" * 55)

    # === PROCESS ===
    checks: list[tuple[str, bool]] = [
        ("Python 3.10+", check_python_version()),
        ("Docker",       check_docker()),
        ("Ollama",       check_ollama()),
        ("PostgreSQL",   check_postgresql()),
    ]

    total = len(checks)
    passed = sum(1 for _, result in checks if result)
    failed = total - passed

    # === OUTPUT ===
    print("=" * 55)
    print(f"  결과: {passed}/{total} 항목 통과")

    if failed == 0:
        print()
        print("  모든 환경 검증이 완료되었습니다.")
        print("  CH03 실습으로 진행하십시오.")
    else:
        print()
        print(f"  {failed}개 항목이 실패했습니다.")
        print("  위의 [FAIL] 항목 해결 방법을 참고하여 환경을 수정한 뒤")
        print("  다시 'python src/verify_env.py' 를 실행하십시오.")

    print("=" * 55)


if __name__ == "__main__":
    run_all_checks()
