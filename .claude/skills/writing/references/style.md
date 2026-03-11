# Writing Style and Tone Rules

## 1. Core Writing Strategy
<!-- 집필 핵심 전략 -->

This book must go beyond a simple manual to become a **'practical guide that solves readers' problems'**.

### The Golden Ratio of Theory and Practice
<!-- 이론과 실습의 황금비율 -->

- Each chapter must follow the 3-step structure of **[Concept Understanding] → [Hands-on] → [Principle Analysis]**.

### Reader-Centered Learning Curve
<!-- 독자 중심의 학습 곡선 -->

- **Advanced**: "In production, you need to guard against this." (exception handling, optimization)

## 2. The Art of Explanation
<!-- 설명의 기술 -->

- **Principle**: Every code snippet, command, and diagram **must include an explanation of "Why it was done this way"**.
- **Good Patterns**:
  - "This folder structure was chosen so that it can later be used as metadata."
  - "This option was enabled to prevent memory leaks."
- **Bad Patterns**:
  - (Code block present with no explanation)
  - "Enter the following command." (no explanation of the reason)

## 3. Core Tone
<!-- 핵심 어조 -->

- **Authoritative formal register**: Use polite and restrained language (~합니다, ~입니다) for the credibility of a professional technical book.
- **Confident declarative statements**: Speculative expressions such as "it seems like" or "it appears to be" are prohibited.
- **Friendly mentoring**: Treat readers as colleagues working together to complete a project, and provide practical solutions.

## 4. Style and Editing Rules
<!-- 문체 및 편집 규칙 -->

- **Active voice**: Use active sentences with a clear subject. (e.g., "The system collects data.")
- **English annotation of technical terms**: Technical terms are annotated in `Korean(English)` format only on first appearance. (e.g., 검색 증강 생성(RAG))
- **Step-by-step procedure expression**: For content where order matters, always use a **numbered list (1., 2., 3.)**.
- **No emoji**: Emoji are prohibited in body text for readability and professionalism.
- **Image caption style**: Write captions below images in the format `*Figure X-Y: description*`.

## 5. Bold Text Rules (Strict Spacing)
<!-- 강조 표기 규칙 -->

When using bold text (`**`), **spaces before and after** must be included.

- This prevents rendering issues when a particle is attached to a bold Korean-English annotation (`**term(English)**`).
- Example: `**컨텍스트 주입(Context Injection)** 이라 합니다.` (correct)
- Counter-example: `**컨텍스트 주입(Context Injection)**이라 합니다.` (incorrect)
- Limit bold usage to 1–2 instances per sentence.

## 6. Expressions to Avoid
<!-- 지양해야 할 표현 -->

- **No cliche analogies**: "long journey", "magic-like", "first steps" → use dry and clear words such as "process", "procedure", "start".
- **No subjective interjections**: Avoid negative-nuance words such as "하필" or "하필이면".
- **No time-dependent expressions**: "latest", "trending these days" → use specific version or year.
- **No unnecessary parenthetical explanations**: Exclude parenthetical notes like "(=Look up)". Define technical terms once on first use and then use them as-is.

### 6.1. Prohibited Tone Patterns
<!-- 금지 말투 패턴 — 독자를 가르치려 하지 않는다 -->

독자는 동료이지 학생이 아니다. 아래 패턴은 모두 금지한다.

**① 훈계·깨달음 강요**
- Bad: "단순한 방법의 결과를 본 후에야 더 복잡한 방법의 가치를 이해할 수 있습니다."
- Bad: "이 한계를 몸으로 체감해야만 필요성이 설득력 있게 다가옵니다."
- Bad: "~해야 한계를 안다", "~해봐야 알 수 있다"
- Good: 사실만 서술한다. "Python 파싱은 이미지형 PDF에서 텍스트 손실이 발생한다. Vision LLM은 이 영역을 보완한다."

**② "이것이 바로...이유입니다" 패턴**
- Bad: "이것이 바로 Step 2가 필요한 이유입니다."
- Good: "Step 2는 이런 이미지형 PDF를 처리하기 위한 단계입니다."

**③ "~하는 이유는...때문입니다" 과잉 설명**
- Bad: "CLI로 먼저 검증하는 이유는 웹 UI 개발 전에 문제를 발견하기 위해서입니다."
- Good: 이유를 말해야 한다면 한 문장으로 간결하게. 자명한 이유는 생략한다.

**④ 습관·태도 훈계**
- Bad: "문제를 조기 발견하는 습관이 중요하다."
- Bad: "~를 확인하는 습관을 들이십시오."
- Good: 사실과 기준만 제시한다. "유사도 80% 이상이면 정상이다."

**⑤ 용어는 정의 먼저, 적용 나중에**
- Bad: "Vision LLM은 PDF 각 페이지를 PNG로 변환한 뒤..." (정의 없이 바로 사용법)
- Good: "Vision LLM은 이미지를 입력으로 받을 수 있는 멀티모달 LLM이다." → 그 다음에 PDF 적용 설명

**⑥ 영어 전문용어 그대로 노출 금지**
- Bad: "URL-safe하게 유지합니다", "department 필드를 추가합니다"
- Good: 한국어로 풀어쓰거나, 첫 등장 시 병기한다. "부서(department) 필드", "공백 대신 언더스코어를 사용합니다"

**⑦ 과도한 챕터 간 참조**
- 한 섹션에서 다른 챕터를 2회 이상 언급하지 않는다.
- Bad: "CH06에서 구축한 VectorDB를 CH07에서 연결하고 CH10에서 튜닝합니다."
- Good: 필요한 참조만 최소 1회. "다음 챕터에서 RAG 체인과 연결합니다."

## 7. Reader-Level Adaptive Writing
<!-- 독자 수준별 집필 심도 -->

Adjust the writing depth according to the reader level specified in `outline/draft.md`.

### 7.1. Comparison by Level
<!-- 수준별 비교 -->

| Item | Beginner | Intermediate | Advanced |
|------|----------|--------------|----------|
| Concept explanation style | Everyday analogy + step-by-step principles | Concise principle explanation | Internal behavior/edge cases |
| Why explanation length | 5+ lines per code block | 3 lines per code block | 1 core line |
| Analogy usage | Actively use | Only when needed | Minimize |
| Prior knowledge assumption | None (explain every term on first appearance) | Basic Python/Linux assumed | Experience with the technology assumed |
| Practice guidance | 1 command at a time + result explanation | Grouped flow explanation | Result only |

### 7.2. Beginner Writing Principles (Default for this project)
<!-- 초급 집필 원칙 -->

When writing for beginner readers, the following must be followed.

- **Analogy first**: When introducing a new concept, always explain with an everyday analogy first.
  - Example: "Vector similarity search is like finding 'books on similar topics' in a library."
- **Two-line definition rule**: When a technical term appears for the first time, explain it with a Korean definition (1 line) + analogy (1 line).
- **Why always follows**: After "Do it this way," always attach "because ~".
- **Progressive disclosure**: Do not show all complex parts of the code at once. Simple version first, complete version later.
- **Free use of concept images**: When a concept image would help reader comprehension, actively insert placeholders from `image.md`. Agents have freedom in making this judgment.

### 7.3. Precautions When Writing Analogies
<!-- 비유 작성 시 주의사항 -->

Analogies are helpful, but the following patterns are prohibited.

- **No cliche analogies**: "magic-like", "black box" → replace with concrete operation explanations
- **No misleading analogies**: Analogies must not distort the actual behavior of the technology.
- **No analogy overuse**: No more than 3 analogies per page. Technical explanation must not be buried by analogies.

## 8. Execution Result Writing Rules
<!-- 실행 결과 작성 규칙 -->

LLM responses are non-deterministic. The following rules apply when writing about execution results.

### 8.1. Absolute Prohibition: Fabricated Output
<!-- 절대 금지: 조작된 출력 -->

- **Never fabricate or predict** specific LLM output text in the chapter manuscript.
- LLM responses vary with every execution — specific numbers, sentence structures, and wording all change.
- Do not write text blocks pretending to be LLM output (e.g., "김철수 사원의 남은 연차는 6일입니다" as if the LLM generated it).
- Do not invent specific metric values (e.g., "유사도: 0.943", "매출 합계: 260.5M") that would appear in LLM responses.

### 8.2. Use Screenshots Instead
<!-- 스크린샷으로 대체 -->

- For LLM execution results, always use **screenshot images** captured from actual runs.
- Insert screenshots with `![description](../assets/CH{N}/{NN}_{description}.png)` format.
- If a screenshot is not yet available, insert a placeholder: `<!-- [CAPTURE NEEDED: {description}] -->`.
- One screenshot per execution step — do not duplicate.

### 8.3. Writing Descriptions Around Results
<!-- 결과 주변 서술 방법 -->

- **Before execution**: Describe what the command does and what to observe, not what the output will say.
  - Good: "실행하면 LLM이 사내 정보 없이 답변을 생성합니다. 어떤 답변이 나오는지 확인하십시오."
  - Bad: "실행하면 다음과 같은 답변이 출력됩니다: ..."
- **After screenshot**: Describe the **pattern** to observe, not the specific content.
  - Good: "LLM이 그럴듯하지만 실제와 다른 정보를 생성했습니다. 이것이 환각입니다."
  - Bad: "LLM이 '남은 연차는 10일입니다'라고 답변했습니다."
- **Variability notice**: When LLM output is shown, add a note that responses differ per run.
  - Example: `> **참고:** LLM 응답은 실행할 때마다 달라집니다. 화면과 다른 결과가 나와도 정상입니다.`

### 8.4. Non-LLM Execution Results
<!-- LLM이 아닌 실행 결과 -->

- Deterministic outputs (DB queries, file listings, version checks) CAN be written as text blocks.
- But keep them short — only the essential lines. Use `...` to truncate long outputs.
- If a deterministic output includes computed values from LLM-dependent data, treat it as LLM output (non-deterministic).
