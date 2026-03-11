# Browser Screenshot Capture Workflow (Playwright MCP)

## 사용 시점

챕터에 웹 UI, Swagger, 채팅 화면 등 **브라우저에서 동작하는 화면**을 캡처해야 할 때 사용한다.
터미널 출력 캡처는 `terminal-capture.md`를 참조한다.

## 필수 MCP 도구

| 도구 | 용도 |
|------|------|
| `mcp__playwright__browser_navigate` | URL로 이동 |
| `mcp__playwright__browser_screenshot` | 현재 화면 캡처 |
| `mcp__playwright__browser_click` | 요소 클릭 (버튼, 링크 등) |
| `mcp__playwright__browser_type` | 입력 필드에 텍스트 입력 |
| `mcp__playwright__browser_close` | 브라우저 종료 |

## 캡처 워크플로우

### 1. 서버 실행

캡처 전 대상 서버를 백그라운드로 실행한다.

```bash
cd {example_path}
source .venv/bin/activate
python app/main.py &
sleep 3  # 서버 초기화 대기
```

### 2. 브라우저 캡처

```
Step 1: browser_navigate → http://localhost:{port}/{path}
Step 2: (필요 시) browser_click / browser_type → 인터랙션
Step 3: browser_screenshot → {project}/assets/CH{N}/{NN}_{description}.png
```

### 3. 인터랙션 캡처 (채팅 UI 예시)

채팅 UI처럼 입력 → 응답 → 재입력 시나리오:

```
1. browser_navigate → http://localhost:8000/chat
2. browser_screenshot → 07_chat-ui-running.png (초기 화면)
3. browser_click → 입력창 클릭
4. browser_type → "병가 신청 시 증빙 서류가 필요한가요?"
5. browser_click → 전송 버튼 클릭
6. (응답 대기 — 30초 이상 걸릴 수 있음)
7. browser_screenshot → 07_first-question.png
8. browser_type → "그럼 장기 병가는 최대 며칠까지 가능한가요?"
9. browser_click → 전송 버튼
10. (응답 대기)
11. browser_screenshot → 07_multiturn-result.png
```

### 4. Swagger UI 캡처 (FastAPI 예시)

```
1. browser_navigate → http://localhost:8000/docs
2. browser_screenshot → {NN}_swagger-ui.png
3. browser_click → POST /api/chat 엔드포인트 클릭
4. browser_click → "Try it out" 버튼
5. browser_type → 예제 JSON 입력
6. browser_click → "Execute" 버튼
7. browser_screenshot → {NN}_api-response.png
```

### 5. 정리

```bash
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "python app/main" 2>/dev/null || true
browser_close
```

## 캡처 규칙

### 파일 저장

- **저장 경로**: `{project}/assets/CH{N}/{NN}_{kebab-case}.png`
- **[CAPTURE NEEDED] 매칭**: 챕터 원고의 `<!-- [CAPTURE NEEDED: {id}` 주석에 지정된 `path:`에 저장
- **중복 금지**: 하나의 캡처에 하나의 파일만 생성

### 응답 대기

- LLM 응답은 30초 이상 걸릴 수 있다 (Ollama 첫 로딩)
- `browser_screenshot` 전에 응답 완료를 확인한다
- 로딩 스피너가 사라지고 AI 답변 말풍선이 나타난 후 캡처한다

### 검증

캡처 후 확인:

1. **파일 존재**: PNG 생성 여부
2. **파일 크기**: 5KB 이상 (빈 이미지 방지)
3. **내용 확인**: Read 도구로 이미지를 열어 화면이 정상인지 확인
   - UI 요소가 모두 렌더링되었는가
   - 텍스트가 깨지지 않았는가
   - 답변 내용이 기대와 일치하는가

## 터미널 + 브라우저 혼합 캡처

한 챕터에 터미널과 브라우저 캡처가 모두 필요한 경우:

```
1. 터미널 캡처 (서버 시작 로그 등) → terminal_screenshot.py
2. 서버 백그라운드 실행
3. 브라우저 캡처 (웹 UI) → Playwright MCP
4. 서버 종료 + 브라우저 종료
```

## Troubleshooting

### 서버 연결 실패

```
browser_navigate → "localhost refused to connect"
```

→ 서버가 아직 시작되지 않았다. `sleep` 시간을 늘리거나 health check 후 진행한다.

### 페이지 빈 화면

→ JavaScript 로딩 시간 필요. `browser_navigate` 후 2-3초 대기 후 `browser_screenshot`.

### LLM 응답 타임아웃

→ Ollama 첫 로딩 시 1-2분 걸릴 수 있다. 응답 대기 시간을 충분히 확보한다.
