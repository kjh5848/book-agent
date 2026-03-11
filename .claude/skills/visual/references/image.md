# Image Generation and Management Rules

## 0. Tool Selection by Visual Asset Type
<!-- 시각 자료 유형별 도구 선택 기준 -->

| Visual Asset Type | Tool | When to Create |
|-------------------|------|----------------|
| Flow diagrams, architecture, sequence diagrams | **Mermaid** | Immediately during writing |
| Concept illustration/metaphor images | **Gemini Image** | Batch generation after writing is complete |
| Practice result screenshots (terminal/UI) | **Direct Capture** | After running example code |

During writing, Gemini images and practice captures are not available, so insert the appropriate **placeholder** for each type.
Write captions in advance during writing.

---

## 0.5. Path Convention
<!-- 이미지 경로 규칙 — 모든 플레이스홀더에 적용 -->

모든 이미지(Gemini 생성, 실습 캡처)는 **챕터별 단일 폴더**에 저장한다.

프로젝트 구조:
```
{project}/
├── chapters/CH{N}_{title}.md   ← 챕터 원고
├── assets/
│   ├── CH01/                   ← CH01의 모든 이미지 (Gemini + 캡처)
│   ├── CH02/
│   └── ...CH10/
```

**Two path types are required in every placeholder:**

| 용도 | 경로 기준 | 형식 | 예시 |
|------|----------|------|------|
| `path:` (에이전트/스크립트용) | 프로젝트 루트(`{project}/`) | `assets/CH{N}/{id}.png` | `assets/CH01/01_chapter-opening.png` |
| `![alt](src)` (마크다운 렌더링) | 챕터 파일(`chapters/`) | `../assets/CH{N}/{id}.png` | `../assets/CH01/01_chapter-opening.png` |

- `path:` — 캡처 에이전트, 이미지 생성 스크립트가 저장 위치를 결정할 때 사용
- `![alt](src)` — 마크다운 렌더링 시 챕터 파일 위치에서 상대 경로로 이미지를 불러옴

> **주의**: 챕터 파일이 `chapters/` 폴더 안에 있으므로 `![alt](assets/...)` 는 **오류**. 반드시 `../assets/...` 를 사용한다.

---

## 1. Placeholder Insertion (2 Methods)
<!-- 집필 시점에 삽입하는 2가지 플레이스홀더 방식 -->

### Method A — Concept Image: Gemini Prompt Placeholder
<!-- 방식 A: 아이콘 사전을 참고하여 프롬프트까지 확정하여 삽입 -->

Use when inserting a concept image. The prompt must be finalized by referencing the project icon dictionary (§2).

```markdown
<!-- [GEMINI PROMPT: {NN}_{identifier}]
path: assets/CH{N}/{NN}_{identifier}.png
{Complete prompt combining §3 base style + project icon dictionary}
Style: {style-tag}
-->
![{caption}](../assets/CH{N}/{NN}_{identifier}.png)
*그림 {N}-{order}: {caption}*
```

**Example:**
```markdown
<!-- [GEMINI PROMPT: 03_docker-why]
path: assets/CH03/03_docker-why.png
Minimalist flat-design infographic illustrating Docker isolation. Three container boxes
labeled 'ollama', 'chromadb', 'app' inside a 'docker-compose' boundary. Arrows show
inter-container communication. White background, Korean labels, 16:9 aspect ratio.
Style: architecture-infographic
-->
![Docker 격리 구조](../assets/CH03/03_docker-why.png)
*그림 3-2: Docker Compose가 각 서비스를 격리하여 실행하는 구조*
```

### Method B — Practice Result: Capture Needed Placeholder
<!-- 방식 B: 실제 실행 결과 화면을 캡처해야 할 위치에 삽입 -->

Insert at locations in the practice section where the actual execution result screen must be captured.
Since this is not a Gemini image, specify only **what needs to be captured** without a prompt.

```markdown
<!-- [CAPTURE NEEDED: {NN}_{identifier}
  path: assets/CH{N}/{NN}_{identifier}.png
  desc: {description of screen to capture: which command was run and what state it shows}
] -->
![{caption}](../assets/CH{N}/{NN}_{identifier}.png)
*그림 {N}-{order}: {caption}*
```

**Example:**
```markdown
<!-- [CAPTURE NEEDED: 03_ollama-list
  path: assets/CH03/03_ollama-list.png
  desc: `ollama list` 실행 후 deepseek-r1 모델이 목록에 나타난 터미널 화면
] -->
![ollama list 실행 결과](../assets/CH03/03_ollama-list.png)
*그림 3-3: deepseek-r1 모델 다운로드 완료 확인*
```

---

## 2. Capture Guidelines (Method B)
<!-- 방식 B 실습 캡처 시 준수 기준 -->

Comply with the following criteria when capturing practice screenshots.

| Item | Criteria |
|------|----------|
| Capture range | Full terminal screen (including command input line) |
| Resolution | Retina/HiDPI recommended, minimum 1280px width |
| Terminal theme | Both light and dark backgrounds allowed; consider grayscale conversion for print |
| Error screen | Capture intentional error examples as-is, including red text |
| Sensitive data | Blur actual values (API keys, passwords, etc.) before capturing |

### 스크린샷과 코드 블록 중복 금지

실행 결과를 보여줄 때 **스크린샷과 터미널 출력 코드 블록을 동시에 사용하지 않는다.** 둘 중 하나만 선택한다.

| 상황 | 사용할 형식 |
|------|-----------|
| 스크린샷(`<img>`)이 있는 경우 | 스크린샷만 사용. 코드 블록으로 같은 출력을 반복하지 않는다 |
| 스크린샷이 없는 경우 (플레이스홀더 단계) | 코드 블록으로 예상 출력을 표시한다 |
| 소스 코드(`\`\`\`python`, `\`\`\`bash` 등) | 이것은 **실행 명령**이므로 스크린샷과 무관하게 유지한다 |

> **핵심**: 언어 태그가 없는 코드 블록(` ``` `)으로 터미널 출력을 보여준 뒤 바로 아래에 같은 내용의 스크린샷이 오면 **중복**이다. 스크린샷이 확보된 시점에서 출력 코드 블록을 제거한다.

---

## 3. Gemini Image Base Style
<!-- 모든 개념 이미지의 베이스 프롬프트 -->

All concept images are generated based on the following base prompt.

**Base Prompt:**
```
A minimalist black and white technical diagram with a strict 16:9 aspect ratio
on a solid white background. No shading, no 3D effects, only clean thin line art.
The entire assembly of icons, lines, and text is perfectly centered globally
within the 16:9 frame, leaving generous and equal white space on all sides.
```

### Common Symbol Patterns
<!-- 공통 심볼 패턴 -->

| Target | Prompt Pattern |
|--------|----------------|
| Person/User | `minimalist line-art person icon labeled '{label}'` |
| Server/Computer | `minimalist line-art server rack icon labeled '{label}'` |
| Database | `minimalist line-art cylinder database icon labeled '{label}'` |
| Document/File stack | `minimalist line-art stack of papers icon labeled '{label}'` |
| AI/Model | `minimalist line-art brain icon labeled '{label}'` |
| Cloud | `minimalist line-art cloud icon labeled '{label}'` |

> **Project-specific icons**: Define labels and additional symbols in `outline/image-guide.md`.

---

## 4. Composition and Margin Rules (Gemini Image)
<!-- Gemini 이미지 구도 및 여백 규칙 -->

- **Safety Margin**: The entire diagram occupies approximately 60–70% of the canvas
- **Global Centering**: Place the center of gravity of the entire assembly at the exact center of the 16:9 frame

---

## 5. File Insertion and Caption Rules (After Image is Ready)
<!-- 이미지 준비 완료 후 플레이스홀더를 실제 이미지로 교체하는 형식 -->

When replacing placeholders with actual images, use `<img>` tag with `width` attribute.
Remove the HTML comment block.

### 이미지 사이즈 규칙

모든 이미지는 `<img>` HTML 태그로 삽입하고, **`width="720"`** 을 기본값으로 사용한다.

| 유형 | width | 용도 |
|------|-------|------|
| 전체 화면 캡처 (대시보드, Swagger UI, 웹 UI) | `720` | 기본값 |
| 터미널 출력 | `720` | 기본값 |
| 다이어그램/개념도 | `720` | 기본값 |

> **규칙**: `![alt](src)` Markdown 문법 대신 반드시 `<img src="..." width="720" alt="...">` 를 사용한다.
> 캡션(`*그림 N-M: ...*`)은 `<img>` 태그 다음 빈 줄 뒤에 작성한다.

**Before (placeholder):**
```markdown
<!-- [GEMINI PROMPT: 03_docker-why]
path: assets/CH03/03_docker-why.png
...prompt...
-->
![Docker 격리 구조](../assets/CH03/03_docker-why.png)
*그림 3-2: Docker Compose가 각 서비스를 격리하여 실행하는 구조*
```

**After (image ready):**
```markdown
<img src="../assets/CH03/03_docker-why.png" width="720" alt="Docker 격리 구조">

*그림 3-2: Docker Compose가 각 서비스를 격리하여 실행하는 구조*
```

- **File name format**: Lowercase English letters, underscores, hyphens (e.g., `03_docker-why.png`)
- **Caption**: Use exactly what was written in the placeholder during writing
