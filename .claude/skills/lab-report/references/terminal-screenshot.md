# terminal_screenshot.py
<!-- 명령어 실행 결과를 화이트 배경 터미널 스타일 PNG로 저장하는 스크립트 -->

Runs a shell command, captures stdout+stderr, renders as a white-background terminal-style HTML, then Playwright screenshots it to PNG.

## Prerequisites
<!-- 사전 환경 설정 -->

### 1. Python — no extra packages required
<!-- Python 표준 라이브러리만 사용 (별도 설치 불필요) -->

`terminal_screenshot.py` uses only the Python standard library. No `pip install` needed.

```bash
python3 --version   # 3.8 or higher required
```

### 2. Playwright MCP — for HTML → PNG capture
<!-- HTML을 PNG로 찍으려면 Playwright MCP가 실행 중이어야 함 -->

The MCP server must be configured in `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

Chromium browser must be installed:

```bash
cd /tmp && npm install @playwright/test && npx playwright install chromium
# Installed browsers location: ~/Library/Caches/ms-playwright/
```

Verify installation:

```bash
ls ~/Library/Caches/ms-playwright/   # should show chromium-XXXX
```

### 3. Google Fonts (Korean rendering)
<!-- 한글 렌더링: Playwright가 인터넷 연결 상태에서 HTML 열 때 자동 로드 -->

The HTML template imports `Noto Sans KR` from Google Fonts automatically when Playwright opens the file. **Internet connection required** during screenshot capture for correct Korean rendering.

Offline fallback fonts: `Apple SD Gothic Neo` (macOS), `Malgun Gothic` (Windows).

## Usage
<!-- 기본 사용법 -->

```bash
python3 {project_root}/.claude/skills/lab-report/scripts/terminal_screenshot.py \
  "실행할 명령어" \
  --output /tmp/step01.html \
  --cwd {예제_경로} \
  --title "CH08 STEP01 - 설명"
```

## Parameters
<!-- 파라미터 -->

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `command` | ✅ | — | Shell command to execute |
| `--output` | ✅ | — | Output HTML file path |
| `--cwd` | — | current dir | Working directory for the command |
| `--title` | — | `Terminal` | Window title shown in titlebar |
| `--timeout` | — | `60` | Timeout in seconds |

## Full Workflow with Playwright
<!-- Playwright와 함께 사용하는 전체 워크플로우 -->

```bash
# Step 1: Generate HTML
python3 {project_root}/.claude/skills/lab-report/scripts/terminal_screenshot.py \
  "python src/main.py" \
  --output /tmp/ch08/step03.html \
  --cwd /path/to/examples/CH08_통합에이전트 \
  --title "CH08 STEP03 - main.py 실행"
```

```
# Step 2: Playwright screenshot
mcp__playwright__browser_navigate("file:///tmp/ch08/step03.html")
mcp__playwright__browser_screenshot(name="/path/to/assets/screenshots/CH08/step03_main_run.png")
```

## Design
<!-- 스크린샷 스타일 특징 -->

- **Background**: White (`#ffffff`) — suitable for book insertion
- **Font**: Noto Sans KR + Apple SD Gothic Neo — Korean characters render correctly
- **Colors**: Blue prompt, green `$` prefix, red errors, green success
- **Window chrome**: macOS-style (red/yellow/green dots)
- **Footer**: Execution time, exit code, working directory
- **Long output**: Truncated to last 100 lines automatically

## Notes
<!-- 주의사항 -->

- Always use `file:///` prefix (3 slashes) when passing HTML path to `browser_navigate`
- Create output directory with `mkdir -p` before running
- The HTML file is temporary — only the final PNG needs to be kept
