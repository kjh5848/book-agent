"""
CH04 베이스 시스템 — 메인 진입점

사용 방법:
    python src/main.py [명령]

명령:
    schema   — DB 스키마 분석 리포트 생성 (기본값)
    api      — FastAPI CRUD 서버 실행 안내 출력
    mcp      — MCP 개념 데모 실행

챕터 4: 베이스 시스템 확보
"""

import sys
import subprocess
import os

from dotenv import load_dotenv

load_dotenv()


def run_schema_viewer() -> None:
    """DB 스키마 분석 도구를 실행합니다."""
    from src.schema_viewer import main as schema_main
    schema_main()


def run_api_guide() -> None:
    """FastAPI CRUD 서버 실행 방법을 안내합니다."""
    print("=" * 60)
    print("  커넥트HR CRUD API 서버 실행 방법")
    print("=" * 60)
    print()
    print("1. 가상환경이 활성화된 상태에서 아래 명령을 실행하십시오:")
    print()
    print("   uvicorn src.crud_api:app --reload --port 8000")
    print()
    print("2. 서버가 실행되면 아래 URL에서 API를 테스트할 수 있습니다:")
    print()
    print("   Swagger UI:  http://localhost:8000/docs")
    print("   ReDoc:       http://localhost:8000/redoc")
    print()
    print("3. 주요 엔드포인트:")
    print("   GET /employees              — 직원 목록")
    print("   GET /employees/{id}         — 직원 상세")
    print("   GET /leave-balance/{emp_id} — 연차 잔액")
    print("   GET /sales/summary          — 매출 요약")
    print("   GET /health                 — 서버 상태")
    print()


def run_mcp_demo() -> None:
    """MCP 개념 데모를 실행합니다."""
    from src.mcp_intro import main as mcp_main
    mcp_main()


def print_usage() -> None:
    """사용법을 출력합니다."""
    print("사용법: python src/main.py [명령]")
    print()
    print("명령:")
    print("  schema  — DB 스키마 분석 리포트 생성 (기본값)")
    print("  api     — FastAPI CRUD 서버 실행 방법 안내")
    print("  mcp     — MCP 개념 데모 실행")
    print()
    print("예시:")
    print("  python src/main.py schema")
    print("  python src/main.py api")
    print("  python src/main.py mcp")


def main() -> None:
    """메인 함수: 명령줄 인자에 따라 실습 모듈을 실행합니다.

    Args 없음. sys.argv를 직접 파싱합니다.
    """
    # --- Input ---
    command = sys.argv[1] if len(sys.argv) > 1 else "schema"

    # --- Process ---
    dispatch = {
        "schema": run_schema_viewer,
        "api":    run_api_guide,
        "mcp":    run_mcp_demo,
    }

    if command not in dispatch:
        print(f"[오류] 알 수 없는 명령: '{command}'")
        print()
        print_usage()
        sys.exit(1)

    # --- Output ---
    dispatch[command]()


if __name__ == "__main__":
    main()
