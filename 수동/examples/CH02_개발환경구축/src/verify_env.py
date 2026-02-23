"""verify_env.py — 개발 환경 전체 동작 확인 스크립트

이 스크립트는 2장에서 구축한 모든 환경이 정상적으로 동작하는지
단계별로 점검합니다.

2장 학습 목표 달성 기준:
    - Ollama 서버가 실행 중이고 지정 모델에 응답하는가
    - PostgreSQL 컨테이너가 구동 중이고 접속에 성공하는가
    - 모든 Python 패키지가 정상 임포트되는가
    - .env 설정이 올바르게 로딩되는가

사용법:
    python src/verify_env.py
"""

import sys
import subprocess
from pathlib import Path


def check_python_version() -> bool:
    """Python 버전이 3.11 이상인지 확인합니다.

    Returns:
        버전 요건을 충족하면 True, 아니면 False
    """

    # --- Input ---
    major = sys.version_info.major
    minor = sys.version_info.minor

    # --- Process ---
    version_str = f"{major}.{minor}.{sys.version_info.micro}"
    is_ok = major == 3 and minor >= 11

    # --- Output ---
    if is_ok:
        print(f"  [OK] Python {version_str}")
    else:
        print(f"  [FAIL] Python {version_str} — Python 3.11 이상이 필요합니다.")
    return is_ok


def check_env_file() -> bool:
    """프로젝트 루트에 .env 파일이 존재하는지 확인합니다.

    Returns:
        .env 파일이 있으면 True, 없으면 False
    """

    # --- Input ---
    env_path = Path(__file__).parent.parent / ".env"

    # --- Process ---
    exists = env_path.exists()

    # --- Output ---
    if exists:
        print(f"  [OK] .env 파일 확인: {env_path}")
    else:
        print(f"  [FAIL] .env 파일이 없습니다: {env_path}")
        print("         cp .env.example .env 명령으로 생성하십시오.")
    return exists


def check_config_loading() -> bool:
    """config.py가 환경 변수를 정상적으로 로딩하는지 확인합니다.

    Returns:
        설정 로딩에 성공하면 True, 실패하면 False
    """

    # --- Input ---
    try:
        from config import print_config_summary, LLM_PROVIDER, POSTGRES_HOST

        # --- Process ---
        # 주요 설정값이 비어 있지 않은지 확인합니다.
        if not LLM_PROVIDER or not POSTGRES_HOST:
            raise ValueError("핵심 환경 변수가 비어 있습니다.")

        # --- Output ---
        print(f"  [OK] 환경 변수 로딩 성공 (LLM_PROVIDER={LLM_PROVIDER})")
        return True

    except Exception as e:
        print(f"  [FAIL] 환경 변수 로딩 실패: {e}")
        return False


def check_ollama() -> bool:
    """Ollama CLI가 설치되어 있고 서버가 실행 중인지 확인합니다.

    Returns:
        Ollama 서버가 응답하면 True, 아니면 False
    """

    # --- Input ---
    try:
        from config import OLLAMA_BASE_URL
        import httpx

        # --- Process ---
        # Ollama API 엔드포인트에 GET 요청을 보냅니다.
        response = httpx.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5.0)
        response.raise_for_status()
        models = response.json().get("models", [])
        model_names = [m.get("name", "") for m in models]

        # --- Output ---
        print(f"  [OK] Ollama 서버 응답 확인 (URL: {OLLAMA_BASE_URL})")
        if model_names:
            print(f"       다운로드된 모델: {', '.join(model_names)}")
        else:
            print("       [주의] 다운로드된 모델이 없습니다.")
            print("              ollama pull deepseek-r1 명령으로 모델을 받으십시오.")
        return True

    except ImportError:
        print("  [SKIP] httpx 패키지가 설치되지 않았습니다. (requirements.txt 설치 필요)")
        return False
    except Exception as e:
        print(f"  [FAIL] Ollama 서버에 연결할 수 없습니다: {e}")
        print("         'ollama serve' 명령으로 서버를 먼저 실행하십시오.")
        return False


def check_postgres() -> bool:
    """PostgreSQL 컨테이너에 접속할 수 있는지 확인합니다.

    Returns:
        접속에 성공하면 True, 실패하면 False
    """

    # --- Input ---
    try:
        from config import get_postgres_url
        import psycopg2

        # --- Process ---
        conn_url = get_postgres_url()
        conn = psycopg2.connect(conn_url, connect_timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        # --- Output ---
        print(f"  [OK] PostgreSQL 접속 성공")
        print(f"       {version[:60]}...")
        return True

    except ImportError:
        print("  [SKIP] psycopg2 패키지가 설치되지 않았습니다. (requirements.txt 설치 필요)")
        return False
    except Exception as e:
        print(f"  [FAIL] PostgreSQL 접속 실패: {e}")
        print("         docker-compose up -d 명령으로 컨테이너를 먼저 실행하십시오.")
        return False


def check_python_packages() -> bool:
    """주요 Python 패키지가 임포트 가능한지 확인합니다.

    Returns:
        모든 패키지 임포트에 성공하면 True, 하나라도 실패하면 False
    """

    # --- Input ---
    packages_to_check = [
        ("dotenv", "python-dotenv"),
        ("langchain", "langchain"),
        ("chromadb", "chromadb"),
        ("psycopg2", "psycopg2-binary"),
        ("httpx", "httpx"),
        ("fastapi", "fastapi"),
    ]

    # --- Process ---
    all_ok = True
    for module_name, package_name in packages_to_check:
        try:
            __import__(module_name)
            print(f"  [OK] {package_name}")
        except ImportError:
            print(f"  [FAIL] {package_name} — pip install {package_name} 으로 설치하십시오.")
            all_ok = False

    # --- Output ---
    return all_ok


def main() -> None:
    """환경 점검 전체 절차를 순서대로 실행합니다."""

    print()
    print("=" * 55)
    print("  2장 개발 환경 구축 — 동작 확인")
    print("  AI 업무 비서 구축: RAG + MCP 실전 가이드")
    print("=" * 55)

    results: dict[str, bool] = {}

    # 1. Python 버전 확인
    print()
    print("[1] Python 버전 확인")
    results["python_version"] = check_python_version()

    # 2. .env 파일 존재 확인
    print()
    print("[2] .env 파일 확인")
    results["env_file"] = check_env_file()

    # 3. 환경 변수 로딩 확인
    print()
    print("[3] 환경 변수 로딩 (config.py)")
    results["config_loading"] = check_config_loading()

    # 4. Python 패키지 설치 확인
    print()
    print("[4] Python 패키지 설치 확인")
    results["packages"] = check_python_packages()

    # 5. Ollama 서버 확인
    print()
    print("[5] Ollama 서버 연결 확인")
    results["ollama"] = check_ollama()

    # 6. PostgreSQL 접속 확인
    print()
    print("[6] PostgreSQL 접속 확인")
    results["postgres"] = check_postgres()

    # 최종 결과 출력
    print()
    print("=" * 55)
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed

    if failed == 0:
        print(f"  결과: 전체 통과 ({passed}/{total})")
        print()
        print("  개발 환경이 정상적으로 구축되었습니다.")
        print("  3장으로 넘어가십시오.")
    else:
        print(f"  결과: {passed}/{total} 통과, {failed}개 항목 미완료")
        print()
        print("  위의 [FAIL] 항목을 해결한 뒤 다시 실행하십시오.")
        print("  트러블슈팅은 README.md의 '자주 묻는 오류' 섹션을 참조하십시오.")
    print("=" * 55)
    print()


if __name__ == "__main__":
    main()
