# Storytelling Concept Rules

## Core Characteristics
<!-- 스토리텔링 컨셉의 핵심 구조와 특징 -->

- **Structure**: Present problem situation → Introduce technology → Resolution process → Result
- **Tone**: Maintain formal register (하십시오체), add narrative flow
- **Protagonist**: The same fictional character/team appears throughout the entire book
- **Theory:Practice ratio**: 3:7

## Protagonist Setup Principles
<!-- 주인공 설정 원칙 -->

- Use the character specified in the `story_persona` field of plan.md.
- If not specified, default to: "Startup development team (5 members)"
- Begin each chapter introduction with the problem situation the protagonist faces.

## Chapter Introduction Pattern
<!-- 챕터 도입부 패턴 -->

```
{Protagonist} was struggling with {problem situation}.
{Concrete description of the pain — numbers, time, repetitive tasks, etc.}
In this chapter, we will explore how to solve this problem using {technology}.
```

Example:
```
Developer Kim spent 2 hours every Monday searching for employment regulations
among 3,000 internal documents. In this chapter, we will solve this problem using RAG.
```

## Section Transition Pattern
<!-- 섹션 전환 패턴 -->

```
The solution {protagonist} chose was {technology}. Let us examine how it was implemented.
```

## Result Presentation Pattern
<!-- 챕터 말미 결과 제시 패턴 -->

Present the protagonist's problem resolution result in numbers at the end of the chapter:
```
Kim can now complete the same task in 30 seconds instead of 2 hours.
```

## Code Explanation Principles
<!-- 코드 설명 원칙 — 스토리텔링에서는 개념과 이해가 중심이다 -->

### Core Principle
- **코드가 중요한 것이 아니라, 개념과 이해가 중요하다.**
- 코드 로직을 줄줄이 설명하지 않는다. 독자가 "왜 이것을 하는지, 어떤 흐름인지"를 이해하면 충분하다.
- **코드 블록 자체를 최소화한다.** 챕터 전체의 핵심 로직 1~2개만 코드 블록으로 보여주고, 나머지는 실행 명령 + 결과 화면으로 대체한다.

### Execution + Result Only (기본 패턴)
- **대부분의 파일은 이 패턴을 따른다.** 코드 블록을 보여주지 않고, 실행 명령 → 동작 요약 → 결과 화면 순서로 구성한다.
- 테스트, 검증, 설정, 유틸리티 스크립트는 **반드시** 이 패턴을 적용한다.

#### Bad Example (금지)
```
python src/01_llm_only.py

def ask_llm(question: str) -> str:
    prompt = build_prompt(question)  # ①
    if LLM_PROVIDER == "ollama":
        return call_ollama(prompt)  # ②
    ...

> ① .env의 LLM_PROVIDER 값을 읽어 적절한 프롬프트를 구성합니다.
> ② LLM_PROVIDER=ollama인 경우 Ollama 엔드포인트를 호출합니다.
```

#### Good Example (권장)
```
python src/01_llm_only.py

이 스크립트는 사내 질문을 LLM에 직접 전달하고 응답을 출력합니다.

{Mermaid 흐름도: 질문 → 프롬프트 구성 → LLM 호출 → 응답 출력}

{실행 결과 화면 (스크린샷 또는 터미널 출력)}

> 전체 코드: src/01_llm_only.py
```

### Code Block Decision Rule
- **핵심 코드**: 챕터의 중심 개념을 이해하는 데 **반드시** 코드를 봐야 하는 경우에만 코드 블록을 사용한다. (예: RAG 체인 조립, 에이전트 라우팅 로직)
- **보조 코드**: 위에 해당하지 않는 모든 코드. 코드 블록 대신 **실행 명령 + Mermaid/동작 요약 + 결과 화면** 패턴을 사용한다.
- **판단 기준**: "이 코드를 안 보여줘도 독자가 개념을 이해할 수 있는가?" → Yes면 코드 블록 삭제.

### Visual Flow over Text Explanation
- 코드 동작 설명은 **Mermaid 흐름도** 또는 **이미지 생성 플레이스홀더**로 대체한다.
- 텍스트 설명이 필요하면 1~2문장 동작 요약만 추가한다.
- **Code Workflow (Input→Process→Output) 패턴을 사용하지 않는다.** (practical-guide 전용)
- **번호 주석(①②③) + 주석 설명 블록도 사용하지 않는다.** 코드 내부 설명 대신 Mermaid 또는 동작 요약으로 대체한다.

### Protagonist Interspersion
- 주인공(메타코딩 등)이 중간중간 등장하여 스토리를 연결한다.
- 기술 섹션 사이에 주인공의 생각, 판단, 반응을 1~2문장 삽입한다.
- Example: "메타코딩은 4개 항목 모두 PASS를 확인하고 다음 단계로 넘어갔습니다."

### Core Code Only
- 핵심 코드(프로젝트의 중심 로직)만 코드 블록으로 보여준다.
- 보조 코드(설정, 테스트, 유틸리티)는 실행 결과만 보여주거나 파일 경로만 안내한다.
- **코드 블록을 보여줄 때도 10~15줄 이내로 핵심만 발췌한다.** 전체 함수를 복붙하지 않는다.

## Prohibited Items
<!-- 금지 사항 -->

- Exaggerated emotional expressions are prohibited ("like a miracle", "finally liberated")
- The protagonist's narrative must not dominate technical explanation by more than 3 lines
- Apply the same analogy rules as in writing/style.md
- **Code Workflow (Input→Process→Output) section is prohibited** — use Mermaid + summary instead

## Visual Guide
<!-- 비주얼 가이드 -->

### Image Usage Principles
<!-- 이미지 사용 원칙 -->

- **Chapter introduction**: An illustration depicting the problem situation the protagonist faces
- **Technology introduction**: A before/after image showing the problem → solution flow
- **Result presentation**: A before/after comparison diagram visualizing numerical improvement

### Gemini Image Style
<!-- Gemini 이미지 스타일 -->

storytelling uses a **warm office illustration style**.

```
<!-- GEMINI_IMAGE
Prompt: Warm office illustration of {protagonist situation description}, soft color palette (warm beige,
        light blue), friendly cartoon style, showing the problem/challenge clearly,
        no text overlay, clean background with subtle workplace elements
Style: office-illustration-warm
Alt: {protagonist} facing the {problem} situation
-->
```

### Before/After Comparison Diagram Pattern
<!-- Before/After 비교 다이어그램 패턴 -->

When visualizing the protagonist's problem resolution effect with numbers:

```
<!-- GEMINI_IMAGE
Prompt: Simple before/after comparison infographic: LEFT side shows "{problem situation}"
        with red indicator and large number "{original number}", RIGHT side shows
        "{resolved situation}" with green indicator and "{improved number}", arrow in the middle,
        clean flat design, white background
Style: before-after-infographic
Alt: Result improved from {original number} to {improved number}
-->
```

### Insertion Location Rules
<!-- 삽입 위치 규칙 -->

1. Chapter introduction — 1 protagonist problem situation illustration (required)
2. Technology introduction section — Mermaid for technical structure explanation (separate from protagonist narrative)
3. Chapter closing — 1 Before/After comparison image (recommended)
