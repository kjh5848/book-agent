#!/usr/bin/env python3
"""
terminal_screenshot.py — 명령어 실행 결과를 터미널 스타일 PNG 스크린샷으로 저장

사용법:
    # HTML만 생성
    python terminal_screenshot.py "python src/main.py" --output screenshot.html

    # HTML + PNG 동시 생성 (Playwright로 .terminal 요소만 캡처)
    python terminal_screenshot.py "python src/main.py" --output screenshot.html --png result.png

    # PNG만 생성 (HTML은 임시 파일로 생성 후 삭제)
    python terminal_screenshot.py "python src/main.py" --png result.png

    # 작업 디렉토리 및 제목 지정
    python terminal_screenshot.py "ollama list" --png shot.png --cwd /path/to/project --title "Ollama 모델 목록"
"""

import argparse
import subprocess
import sys
import os
import tempfile
from pathlib import Path


HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500&display=swap');

  html, body {{
    margin: 0;
    padding: 0;
    background: transparent;
    height: auto;
  }}
  body {{
    padding: 20px;
    display: inline-block;
    width: 100%;
    box-sizing: border-box;
    font-family: 'Noto Sans KR', 'Apple SD Gothic Neo', 'Malgun Gothic',
                 'Menlo', 'Monaco', 'Courier New', monospace;
  }}
  .terminal {{
    width: 860px;
    margin: 0 auto;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    border: 1px solid #d0d0d0;
    background: #ffffff;
  }}
  .titlebar {{
    background: #e0e0e0;
    padding: 10px 16px;
    display: flex;
    align-items: center;
    gap: 8px;
    border-bottom: 1px solid #c8c8c8;
  }}
  .dot {{
    width: 12px;
    height: 12px;
    border-radius: 50%;
  }}
  .dot.red {{ background: #ff5f57; }}
  .dot.yellow {{ background: #ffbd2e; }}
  .dot.green {{ background: #28c940; }}
  .title {{
    color: #555;
    font-size: 12px;
    margin-left: 8px;
    flex: 1;
    text-align: center;
    font-weight: 500;
  }}
  .body {{
    padding: 20px 24px;
  }}
  .prompt {{
    color: #0066cc;
    font-size: 13px;
    margin-bottom: 10px;
    word-break: break-all;
    font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  }}
  .prompt::before {{
    content: '$ ';
    color: #2a9d2a;
    font-weight: bold;
  }}
  .output {{
    color: #222222;
    font-size: 13px;
    line-height: 1.7;
    white-space: pre-wrap;
    word-break: break-all;
    font-family: 'Noto Sans KR', 'Apple SD Gothic Neo', 'Malgun Gothic',
                 'Menlo', 'Monaco', 'Courier New', monospace;
  }}
  .output .err {{ color: #cc0000; font-weight: 500; }}
  .output .ok  {{ color: #2a9d2a; font-weight: 500; }}
</style>
</head>
<body>
<div class="terminal">
  <div class="titlebar">
    <div class="dot red"></div>
    <div class="dot yellow"></div>
    <div class="dot green"></div>
    <div class="title">{title}</div>
  </div>
  <div class="body">
    <div class="prompt">{command}</div>
    <div class="output">{output}</div>
  </div>
</div>
</body>
</html>
"""


def escape_html(text: str) -> str:
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def colorize_output(text: str) -> str:
    """에러/성공 키워드에 색상 클래스 적용"""
    lines = []
    for line in text.split("\n"):
        lower = line.lower()
        if any(k in lower for k in ["error", "traceback", "failed", "exception", "not found"]):
            lines.append(f'<span class="err">{escape_html(line)}</span>')
        elif any(k in lower for k in ["success", "done", "completed", "ok", "pass"]):
            lines.append(f'<span class="ok">{escape_html(line)}</span>')
        else:
            lines.append(escape_html(line))
    return "\n".join(lines)


def run_and_capture(command: str, cwd: str = None, timeout: int = 60) -> tuple[str, int]:
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=cwd,
            timeout=timeout,
        )
        output = result.stdout
        if result.stderr:
            output += "\n[stderr]\n" + result.stderr
        return output.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return f"[타임아웃: {timeout}초 초과]", 1
    except Exception as e:
        return f"[실행 오류: {e}]", 1


def capture_png(html_path: str, png_path: str) -> bool:
    """Playwright로 .terminal 요소만 캡처하여 PNG 저장"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[경고] playwright 미설치. pip install playwright && playwright install chromium")
        return False

    png_out = Path(png_path)
    png_out.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 920, "height": 800})
        page.goto(f"file://{os.path.abspath(html_path)}")
        page.wait_for_load_state("networkidle")
        # .terminal 요소만 캡처 → 여백 없이 딱 맞게
        terminal = page.locator(".terminal")
        terminal.screenshot(path=str(png_out))
        browser.close()

    print(f"PNG 저장: {png_out} ({png_out.stat().st_size // 1024}KB)")
    return True


def build_html(title: str, command: str, output: str) -> str:
    """터미널 스타일 HTML 생성"""
    # 출력이 너무 길면 마지막 100줄만
    lines = output.split("\n")
    if len(lines) > 100:
        output = f"[... 앞 {len(lines)-100}줄 생략 ...]\n" + "\n".join(lines[-100:])

    return HTML_TEMPLATE.format(
        title=title,
        command=escape_html(command),
        output=colorize_output(output),
    )


def main():
    parser = argparse.ArgumentParser(
        description="명령어 실행 결과를 터미널 스타일 스크린샷(PNG)으로 저장"
    )
    parser.add_argument("command", help="실행할 명령어")
    parser.add_argument("--output", default=None, help="출력 HTML 파일 경로")
    parser.add_argument("--png", default=None, help="출력 PNG 파일 경로")
    parser.add_argument("--cwd", default=None, help="작업 디렉토리")
    parser.add_argument("--title", default="Terminal", help="창 제목")
    parser.add_argument("--timeout", type=int, default=60, help="타임아웃(초)")
    parser.add_argument("--display", default=None, help="스크린샷에 표시할 명령어 (실제 실행과 다를 때)")
    args = parser.parse_args()

    if not args.output and not args.png:
        parser.error("--output 또는 --png 중 하나는 지정해야 합니다.")

    cwd = args.cwd or os.getcwd()
    print(f"실행: {args.command}")
    print(f"경로: {cwd}")

    output, exit_code = run_and_capture(args.command, cwd=cwd, timeout=args.timeout)

    if not output:
        output = "(출력 없음)"

    display_cmd = args.display or args.command
    html = build_html(args.title, display_cmd, output)

    # HTML 저장
    html_path = args.output
    temp_html = False
    if not html_path:
        # PNG만 요청된 경우 임시 HTML 생성
        fd, html_path = tempfile.mkstemp(suffix=".html")
        os.close(fd)
        temp_html = True

    Path(html_path).parent.mkdir(parents=True, exist_ok=True)
    Path(html_path).write_text(html, encoding="utf-8")

    if not temp_html:
        print(f"HTML 저장: {html_path}")

    # PNG 캡처
    if args.png:
        capture_png(html_path, args.png)

    # 임시 HTML 정리
    if temp_html:
        os.unlink(html_path)

    print(f"종료 코드: {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
