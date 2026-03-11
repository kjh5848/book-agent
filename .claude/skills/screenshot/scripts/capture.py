#!/usr/bin/env python3
"""
capture.py — 챕터별 터미널 스크린샷 배치 생성 스크립트

사용법:
    # 단일 스크린샷
    python capture.py single \
      --cmd "python src/main.py" \
      --cwd /path/to/CH06 \
      --png /path/to/assets/CH06/06_main-pipeline.png \
      --title "전체 파이프라인 실행"

    # 단일 스크린샷 (venv 사용)
    python capture.py single \
      --cmd "python src/main.py" \
      --cwd /path/to/CH06 \
      --venv .venv \
      --png /path/to/assets/CH06/06_main-pipeline.png \
      --title "전체 파이프라인 실행"

    # JSON 배치 (여러 스크린샷 한 번에)
    python capture.py batch --config screenshots.json

screenshots.json 예시:
    {
      "cwd": "/path/to/examples/CH06_VectorDB_구축",
      "assets_dir": "/path/to/assets/CH06",
      "venv": ".venv",
      "timeout": 120,
      "screenshots": [
        {
          "cmd": "python src/main.py",
          "filename": "06_main-pipeline.png",
          "title": "전체 파이프라인 실행"
        },
        {
          "cmd": "python src/cli_search.py --query '연차 사용 규정' --top-k 3",
          "filename": "06_cli-search.png",
          "title": "CLI 검색 결과"
        }
      ]
    }
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def find_terminal_screenshot_py() -> str:
    """terminal_screenshot.py 경로를 자동 탐색한다."""
    # 이 스크립트 기준으로 상위 탐색
    current = Path(__file__).resolve()
    for parent in current.parents:
        candidate = parent / ".claude" / "skills" / "lab-report" / "scripts" / "terminal_screenshot.py"
        if candidate.exists():
            return str(candidate)
    raise FileNotFoundError(
        "terminal_screenshot.py를 찾을 수 없습니다. "
        ".claude/skills/lab-report/scripts/terminal_screenshot.py 경로를 확인하십시오."
    )


def resolve_command(cmd: str, cwd: str, venv: str = None) -> tuple[str, str]:
    """실제 실행 명령어와 표시용 명령어를 반환한다.

    Args:
        cmd: 사용자가 지정한 명령어 (예: "python src/main.py")
        cwd: 작업 디렉토리
        venv: 가상환경 폴더명 (예: ".venv")

    Returns:
        (actual_command, display_command) 튜플
    """
    display_cmd = cmd

    if venv:
        venv_python = os.path.join(cwd, venv, "bin", "python")
        if os.path.isfile(venv_python):
            # "python src/main.py" → "/path/.venv/bin/python src/main.py"
            actual_cmd = cmd.replace("python ", f"{venv_python} ", 1)
        else:
            print(f"[WARN] venv python 없음: {venv_python}, 시스템 python 사용")
            actual_cmd = cmd
    else:
        actual_cmd = cmd

    return actual_cmd, display_cmd


def capture_single(
    cmd: str,
    cwd: str,
    png_path: str,
    title: str = "Terminal",
    venv: str = None,
    timeout: int = 120,
) -> dict:
    """단일 스크린샷을 생성한다.

    Returns:
        {"file": str, "size_kb": int, "status": "OK"|"FAIL", "error": str|None}
    """
    script = find_terminal_screenshot_py()
    actual_cmd, display_cmd = resolve_command(cmd, cwd, venv)

    # 출력 디렉토리 생성
    Path(png_path).parent.mkdir(parents=True, exist_ok=True)

    args = [
        sys.executable, script,
        actual_cmd,
        "--png", png_path,
        "--display", display_cmd,
        "--cwd", cwd,
        "--title", title,
        "--timeout", str(timeout),
    ]

    print(f"\n{'='*60}")
    print(f"  📸 {title}")
    print(f"{'='*60}")
    print(f"  명령어: {display_cmd}")
    print(f"  경로: {cwd}")
    print(f"  출력: {png_path}")

    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout + 30,  # 스크립트 자체 타임아웃 + 여유
        )
        # 스크립트 출력 표시
        if result.stdout:
            for line in result.stdout.strip().split("\n"):
                print(f"  {line}")
        if result.stderr:
            for line in result.stderr.strip().split("\n"):
                print(f"  [stderr] {line}")

    except subprocess.TimeoutExpired:
        return {
            "file": png_path,
            "size_kb": 0,
            "status": "FAIL",
            "error": f"타임아웃 ({timeout+30}초)",
        }
    except Exception as e:
        return {
            "file": png_path,
            "size_kb": 0,
            "status": "FAIL",
            "error": str(e),
        }

    # 검증
    png = Path(png_path)
    if not png.exists():
        return {
            "file": png_path,
            "size_kb": 0,
            "status": "FAIL",
            "error": "PNG 파일이 생성되지 않음",
        }

    size_kb = png.stat().st_size // 1024
    if size_kb < 5:
        return {
            "file": png_path,
            "size_kb": size_kb,
            "status": "FAIL",
            "error": f"파일 크기 너무 작음 ({size_kb}KB < 5KB)",
        }

    print(f"  ✅ OK ({size_kb}KB)")
    return {
        "file": png_path,
        "size_kb": size_kb,
        "status": "OK",
        "error": None,
    }


def capture_batch(config_path: str) -> list[dict]:
    """JSON 설정 파일로 배치 캡처를 수행한다."""
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    cwd = config["cwd"]
    assets_dir = config.get("assets_dir", ".")
    venv = config.get("venv")
    timeout = config.get("timeout", 120)

    results = []
    for shot in config["screenshots"]:
        png_path = os.path.join(assets_dir, shot["filename"])
        result = capture_single(
            cmd=shot["cmd"],
            cwd=cwd,
            png_path=png_path,
            title=shot.get("title", "Terminal"),
            venv=venv,
            timeout=shot.get("timeout", timeout),
        )
        results.append(result)

    return results


def print_summary(results: list[dict]):
    """결과 요약 테이블을 출력한다."""
    print(f"\n{'='*60}")
    print("  📊 캡처 결과 요약")
    print(f"{'='*60}")
    print(f"  {'파일':<40} {'크기':>6} {'상태':>6}")
    print(f"  {'-'*40} {'-'*6} {'-'*6}")

    ok_count = 0
    fail_count = 0
    for r in results:
        filename = Path(r["file"]).name
        size = f"{r['size_kb']}KB"
        status = r["status"]
        if status == "OK":
            ok_count += 1
            print(f"  {filename:<40} {size:>6} {'✅ OK':>6}")
        else:
            fail_count += 1
            print(f"  {filename:<40} {size:>6} {'❌ FAIL':>6}")
            if r["error"]:
                print(f"    → {r['error']}")

    print(f"\n  총 {len(results)}개: ✅ {ok_count}개 성공, ❌ {fail_count}개 실패")


def main():
    parser = argparse.ArgumentParser(
        description="터미널 스크린샷 배치 생성"
    )
    subparsers = parser.add_subparsers(dest="mode", help="실행 모드")

    # single 모드
    single_parser = subparsers.add_parser("single", help="단일 스크린샷 생성")
    single_parser.add_argument("--cmd", required=True, help="실행할 명령어")
    single_parser.add_argument("--cwd", required=True, help="작업 디렉토리")
    single_parser.add_argument("--png", required=True, help="출력 PNG 경로")
    single_parser.add_argument("--title", default="Terminal", help="창 제목")
    single_parser.add_argument("--venv", default=None, help="가상환경 폴더명")
    single_parser.add_argument("--timeout", type=int, default=120, help="타임아웃(초)")

    # batch 모드
    batch_parser = subparsers.add_parser("batch", help="JSON 설정 파일로 배치 캡처")
    batch_parser.add_argument("--config", required=True, help="JSON 설정 파일 경로")

    args = parser.parse_args()

    if not args.mode:
        parser.print_help()
        return 1

    if args.mode == "single":
        result = capture_single(
            cmd=args.cmd,
            cwd=args.cwd,
            png_path=args.png,
            title=args.title,
            venv=args.venv,
            timeout=args.timeout,
        )
        print_summary([result])
        return 0 if result["status"] == "OK" else 1

    elif args.mode == "batch":
        results = capture_batch(args.config)
        print_summary(results)
        fail_count = sum(1 for r in results if r["status"] != "OK")
        return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
