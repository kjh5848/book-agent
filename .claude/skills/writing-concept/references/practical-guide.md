# Practical Guide Concept Rules

<!-- 현재 시스템 기본값. writing 스킬의 style.md, chapter-structure.md 규칙을 그대로 따른다. -->

Current system default. Follows the rules in writing skill's style.md and chapter-structure.md as-is.

## Core Characteristics
<!-- 실무 지침서 컨셉의 핵심 구조와 특징 -->

- **Structure**: [Concept Understanding] → [Hands-on] → [Principle Analysis] 3-step structure
- **Tone**: Formal register (하십시오체), authoritative mentor tone
- **Why obligation**: Explanation of reasons is required for all code and commands
- **Theory:Practice ratio**: 4:6

## Chapter Introduction Pattern
<!-- 챕터 도입부 패턴 -->

```
In this chapter, you will learn {core topic}.
{1–2 sentence summary — what and why you are learning this}
```

## Section Transition Pattern
<!-- 개념 설명에서 실습으로 넘어가는 전환 패턴 -->

When transitioning from concept explanation to hands-on practice:
```
Now that we understand the concept, let us implement it directly.
```

## Code Explanation Pattern
<!-- 코드 블록 아래 코드 워크플로우 배치 패턴 -->

Below every code block, include:
```
#### Code Workflow

1. **Input**: ...
2. **Process**: ...
3. **Output**: ...
```

## Visual Guide
<!-- 비주얼 가이드 -->

### Image Usage Principles
<!-- 이미지 사용 원칙 -->

- **Concept explanation**: System architecture diagram showing relationships between components takes priority
- **Practice flow**: Step-by-step flowchart (Mermaid flowchart)
- **Result verification**: Terminal output screenshot placeholder

### Gemini Image Style
<!-- Gemini 이미지 스타일 -->

practical-guide uses a **clean technical document style**.

```
<!-- GEMINI_IMAGE
Prompt: Clean technical diagram showing {concept}, flat design with blue and gray tones,
        professional developer documentation style, no decorative elements,
        labeled arrows indicating data flow, white background
Style: technical-flat
Alt: {concept} architecture diagram
-->
```

### Priority Use Cases for Mermaid
<!-- Mermaid 우선 사용 케이스 -->

| Situation | Recommended Visual |
|-----------|-------------------|
| Relationships between concepts | Mermaid graph LR |
| Execution steps | Mermaid flowchart TD |
| Overall system structure | Gemini image placeholder |
| Code execution result | Code block (bash output) |

### Insertion Location Rules
<!-- 삽입 위치 규칙 -->

1. Chapter introduction — 1 at-a-glance overview diagram (required)
2. After concept explanation — Mermaid or image to visualize the concept (choose)
3. After practice completion — result screen placeholder (optional)
