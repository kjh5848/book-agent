# Recipe / Cookbook Concept Rules

## Core Characteristics
<!-- 레시피/쿡북 컨셉의 핵심 구조와 특징 -->

- **Structure**: Problem → Requirements → Solution → Verification
- **Tone**: Concise and direct, minimal unnecessary prose
- **TOC composition**: Each chapter is an independent recipe (minimize cross-chapter dependencies)
- **Theory:Practice ratio**: 2:8

## Chapter Introduction Pattern
<!-- 챕터 도입부 패턴 -->

```
## Problem

{One sentence describing the problem this recipe solves}

## Requirements

| Item | Version/Spec |
|------|-------------|
| Python | 3.10+ |
| {package} | {version} |

## Prerequisites

- {Required preparation step 1}
- {Required preparation step 2}
```

## Step Description Pattern
<!-- 번호를 붙인 순서형 목록 단계 서술 패턴 -->

Numbered ordered list. Each step begins with a verb.

```
1. {Verb} {object}: {one-line description}
   ```bash
   {command}
   ```
2. {Verb} {object}: ...
```

## Verification Pattern
<!-- 결과 확인 패턴 -->

```
## Verification

Verify that everything is working correctly with the command below.

```bash
{verification command}
```

Expected output:
```
{expected result}
```
```

## See Also Pattern
<!-- 각 레시피 끝에 관련 레시피 링크 패턴 -->

Link related recipes at the end of each recipe:
```
## See Also

- CH{N}: {related recipe title}
```

## Visual Guide
<!-- 비주얼 가이드 -->

### Image Usage Principles
<!-- 이미지 사용 원칙 -->

- **Requirements list**: A table is sufficient (no image needed)
- **Solution steps**: Per-step screenshot placeholder (code execution result)
- **Verification**: Final output screenshot required

### Gemini Image Style
<!-- Gemini 이미지 스타일 -->

recipe uses a **step-by-step infographic style**.

```
<!-- GEMINI_IMAGE
Prompt: Step-by-step recipe card infographic for "{recipe title}", numbered steps
        1-{N} with icons for each step, minimal flat design, green accent color,
        card-style layout with light gray background, technical cooking metaphor
        (ingredients = dependencies, steps = commands)
Style: recipe-card-infographic
Alt: {recipe title} step-by-step summary
-->
```

### Execution Result Screenshot Pattern
<!-- 각 단계 완료 후 결과를 보여주는 스크린샷 패턴 -->

When showing results after completing each step:

```
<!-- GEMINI_IMAGE
Prompt: Terminal screenshot showing successful output of "{command}", dark terminal
        background, green success text, realistic terminal font, showing the exact
        expected output described in the verification section
Style: terminal-screenshot
Alt: {step} execution result screen
-->
```

### Insertion Location Rules
<!-- 삽입 위치 규칙 -->

1. Recipe introduction — step summary infographic (optional)
2. Each step's code block — result verification screenshot placeholder
3. Verification section — 1 final output screenshot (required)
