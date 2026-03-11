# Project Build-up Concept Rules

## Core Characteristics
<!-- 프로젝트 빌드업 컨셉의 핵심 구조와 특징 -->

- **Structure**: The entire book follows a flow of building one service from start to finish
- **Tone**: Formal register (하십시오체), emphasis on sharing progress
- **Chapter connection**: Each chapter adds features on top of the previous chapter's output
- **Theory:Practice ratio**: 3:7

## Progress Display Pattern
<!-- 각 챕터 도입부 전체 프로젝트 대비 현재 위치 표시 패턴 -->

Display the current position relative to the overall project at the beginning of each chapter.

```
Features completed so far:
- [x] CH02: Development environment setup
- [x] CH03: LLM integration
- [ ] **CH04: Base system construction** ← Current chapter
- [ ] CH05–CH10: ...
```

## Chapter Introduction Pattern
<!-- 챕터 도입부 패턴 -->

```
We have completed {previous chapter output} so far.
In this chapter, we will add {this chapter's feature} to it.
Once complete, {what the user will be able to do} will be possible.
```

## Code Extension Display Pattern
<!-- 이전 챕터 코드에서 변경·추가되는 부분 표시 패턴 -->

Clearly mark the parts changed or added from the previous chapter's code.

```python
# Code written in CH03 (no changes)
def existing_function():
    ...

# Newly added in CH04 ↓
def new_function():
    ...
```

## Chapter Closing Pattern
<!-- 챕터 마무리 패턴 -->

```
## N. Summary

{This chapter's feature} has now been added to {service name}.
In the next chapter, we will implement {next chapter's feature}.
```

## Visual Guide
<!-- 비주얼 가이드 -->

### Image Usage Principles
<!-- 이미지 사용 원칙 -->

- **Chapter introduction**: Cumulative architecture growth diagram (updated each chapter)
- **When adding features**: Comparison diagram showing new components added to previous structure
- **Chapter closing**: Full system structure diagram of everything completed so far

### Gemini Image Style
<!-- Gemini 이미지 스타일 -->

project-buildup uses a **layered architecture growth style**.

```
<!-- GEMINI_IMAGE
Prompt: Layered architecture diagram showing cumulative project growth up to CH{N},
        previously completed layers in gray/muted tones, current chapter's new
        component highlighted in bright blue, stack building upward style,
        clean technical diagram, white background, labeled layers
Style: layered-architecture-growth
Alt: {service name} architecture completed up to CH{N}
-->
```

### Progress Bar Pattern
<!-- 챕터 도입부 진행 상황 표시에 시각 효과를 추가하는 패턴 -->

When adding visual effect to the chapter introduction progress display:

```
<!-- GEMINI_IMAGE
Prompt: Horizontal progress bar showing project completion: {N}/{total_chapters} chapters done,
        filled portion in green, current chapter highlighted with a marker,
        chapter names below each segment, clean flat infographic style
Style: progress-bar-infographic
Alt: Overall project progress ({N}/{total_chapters} chapters completed)
-->
```

### Insertion Location Rules
<!-- 삽입 위치 규칙 -->

1. Chapter introduction — 1 cumulative architecture diagram (required, Mermaid or image)
2. When explaining code extension — Mermaid diagram highlighting added components
3. Chapter closing — 1 system structure diagram of everything completed so far (required)
