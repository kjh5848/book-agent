# Workbook Concept Rules

## Core Characteristics
<!-- 워크북 컨셉의 핵심 구조와 특징 -->

- **Structure**: Concept summary → Example → Exercise → Solution
- **Tone**: Formal register (하십시오체), encouraging learner tone
- **Checklist**: Learning completion checklist at the end of each chapter
- **Theory:Practice ratio**: 3:7

## Concept Summary Box Pattern
<!-- 각 개념을 박스로 압축 요약하는 패턴 -->

Compress and summarize each concept in a box.

```
> **Core Concept: {concept name}**
> {Definition in one sentence}
> Example: {concrete example}
```

## Example Pattern
<!-- 완성된 예제 먼저, 설명 나중 패턴 -->

Show the completed example first, explanation second.

```
**Example {number}: {title}**

{Completed code}

Let us examine the key parts of the above code.
- Line {N}: {explanation}
- Line {M}: {explanation}
```

## Exercise Pattern
<!-- 각 챕터 끝 난이도별 3가지 연습문제 패턴 -->

Present 3 exercises by difficulty level at the end of each chapter.

```
## Exercises

**★ Basic**: {basic level problem}

**★★ Applied**: {applied level problem}

**★★★ Advanced**: {advanced level problem}

> See `exercises/CH{N}_solutions.md` for solutions.
```

## Learning Checklist Pattern
<!-- 챕터 마지막 학습 체크리스트 패턴 -->

Place at the end of the chapter.

```
## Learning Checklist

After completing this chapter, verify the following items on your own.

- [ ] I can explain {learning objective 1}.
- [ ] I can implement {learning objective 2} directly.
- [ ] I can compare the pros and cons of {learning objective 3}.
```

## Prohibited Items
<!-- 금지 사항 -->

- Omitting exercises is prohibited
- Exercises without solutions are prohibited (the path to the solution file must always be specified)
- If the checklist has fewer than 3 items, add more

## Visual Guide
<!-- 비주얼 가이드 -->

### Image Usage Principles
<!-- 이미지 사용 원칙 -->

- **Concept summary box**: Visual memory card image (optional)
- **Example execution process**: Per-step screenshot placeholder
- **Learning checklist**: Text markdown is sufficient (no image needed)

### Gemini Image Style
<!-- Gemini 이미지 스타일 -->

workbook uses an **educational study card style**.

```
<!-- GEMINI_IMAGE
Prompt: Study flashcard design for concept "{concept name}", card has a clean white front
        with concept title in large bold font, key definition in a colored box
        (light yellow), one visual example icon on the right, subtle drop shadow,
        educational workbook style, A6 card proportions
Style: study-flashcard
Alt: {concept name} core concept card
-->
```

### Exercise Difficulty Display Pattern
<!-- 난이도를 시각적으로 구분하는 패턴 -->

When visually distinguishing difficulty levels:

```
<!-- GEMINI_IMAGE
Prompt: Three exercise difficulty level badges in a row: "★ 기본" (green, easy),
        "★★ 응용" (yellow, medium), "★★★ 심화" (red, hard), badge style with
        rounded corners, clear star icons, educational workbook aesthetic
Style: difficulty-badge
Alt: Exercise difficulty levels (Basic / Applied / Advanced)
-->
```

### Insertion Location Rules
<!-- 삽입 위치 규칙 -->

1. Next to concept summary box — study card image (optional, 1–2 per chapter)
2. After example code execution — result screenshot placeholder
3. Before exercise section — 1 difficulty badge image (optional)
