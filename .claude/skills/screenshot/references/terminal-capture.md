# Terminal Screenshot Capture Workflow

## Script Location

```
{project_root}/.claude/skills/lab-report/scripts/terminal_screenshot.py
```

## One-Command PNG Generation

`--png` 옵션으로 HTML 생성 + Playwright 캡처를 한 번에 수행한다.

```bash
python3 {SCRIPT} "{ACTUAL_COMMAND}" \
  --png {OUTPUT_PNG} \
  --display "{DISPLAY_COMMAND}" \
  --cwd {WORKING_DIR} \
  --title "{TITLE}" \
  --timeout 120
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `command` | Y | 실제 실행할 명령어 (venv 경로 포함 가능) |
| `--png` | Y | 출력 PNG 파일 경로 |
| `--display` | Y | 스크린샷에 표시할 깨끗한 명령어 |
| `--cwd` | Y | 명령어 실행 디렉토리 |
| `--title` | Y | 터미널 창 타이틀바에 표시할 제목 |
| `--timeout` | - | 타임아웃 초 (기본 60, 임베딩 등은 120 권장) |
| `--output` | - | HTML도 보존하려면 경로 지정 |

## Example

```bash
SCRIPT="/path/to/.claude/skills/lab-report/scripts/terminal_screenshot.py"
CH06="/path/to/examples/CH06_VectorDB_구축"

python3 "$SCRIPT" \
  "$CH06/.venv/bin/python src/main.py" \
  --png "$CH06/../../assets/CH06/06_main-pipeline.png" \
  --display "python src/main.py" \
  --cwd "$CH06" \
  --title "전체 파이프라인 실행" \
  --timeout 120
```

## Display Command Rules

`--display`에는 독자가 따라할 수 있는 깨끗한 명령어를 지정한다:

| Bad (절대경로) | Good (--display) |
|---|---|
| `/Users/me/.venv/bin/python src/main.py` | `python src/main.py` |
| `/opt/homebrew/bin/python3 src/cli_search.py --query '연차'` | `python src/cli_search.py --query '연차'` |
| `docker exec -it container bash -c "python test.py"` | `python test.py` |

## File Naming Convention

```
{CH번호}_{설명}.png

06_extract-pdf.png        # 개별 스크립트 실행
06_main-pipeline.png      # 전체 파이프라인
06_cli-search.png         # CLI 검색 결과
07_server-start.png       # 서버 시작
07_chat-api.png           # API 호출 결과
```

## Save Location

```
{project}/assets/CH{N}/{CH번호}_{설명}.png
```

## Verification Checklist

캡처 후 반드시 확인:

1. **파일 존재**: PNG 파일이 생성되었는가
2. **파일 크기**: 5KB 이상인가 (빈 이미지 방지)
3. **내용 확인**: Read 도구로 이미지를 열어 다음을 확인
   - 하단이 잘리지 않았는가 (마지막 출력 라인이 보이는가)
   - prompt에 절대경로가 노출되지 않았는가
   - 이모지/특수문자가 정상 렌더링되었는가

## Troubleshooting

### Playwright 미설치

```bash
pip install playwright && playwright install chromium
```

### 한글 깨짐

- 인터넷 연결 필요 (Google Fonts Noto Sans KR 로드)
- 오프라인: macOS `Apple SD Gothic Neo`, Windows `Malgun Gothic` 폴백

### 이미지 잘림

`terminal_screenshot.py`는 `.locator(".terminal").screenshot()`를 사용하여 요소 전체를 캡처한다.
잘림이 발생하면 `--output`으로 HTML을 보존하고 브라우저에서 직접 확인한다.

### 타임아웃

임베딩 모델 로드가 포함된 명령어는 `--timeout 120` 이상을 사용한다.
