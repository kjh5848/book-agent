# plan.md Template

## plan.md Required 4 Sections
<!-- plan.md에 반드시 포함되어야 하는 4개 섹션 -->

### Section 1: Design Document
<!-- 독자 페르소나, 학습 목표, 기술 스택, 집필 컨셉 명세 -->

- **Reader Persona**: Target audience, prerequisite knowledge level, required environment
- **Per-chapter Learning Objectives**: Learning Objectives and final achievement criteria
- **Technology Stack**: Clear version specification (e.g., Python 3.11, LangChain 0.3)
- **Pre-practice Checklist**: Guide for preparation tasks before starting
- **Writing Concept (writing_concept)**: Choose one of the following
  - `practical-guide` — Practical guide (default): 3-step structure of concept → hands-on → principles, Why explanation required
  - `storytelling` — Storytelling: narrative structure in which a fictional character solves a problem
  - `recipe` — Recipe/Cookbook: independent recipes per problem, ingredients → instructions → result verification
  - `project-buildup` — Project Build-up: single project where features are added chapter by chapter
  - `comparison` — Comparison/Contrast: provides criteria for technology selection, trade-offs explicitly stated
  - `workbook` — Workbook: concept summary → example → exercise → solution structure
- **Code Workflow Style (code_workflow_style)**: Choose one of the following
  - `narrative` — 서술형 (default): 입력·처리·출력을 자연어 한 문단으로 서술 (`> **동작 요약:** ...`)
  - `flow` — 화살표 흐름: 입력→처리→출력을 화살표로 한 줄 표현 (`> **흐름:** ... → ... → ...`)

### Section 2: Architecture and Diagrams
<!-- 시스템 구성도, 개념-코드 매핑, 의존성 그래프, 실행 흐름도 -->

- **Overall System Diagram**: Mermaid format
- **Per-chapter Key Concept ↔ Code Module Mapping Table**
- **System/Module Dependency Graph**
- **Execution Flow Diagram per Scenario**

### Section 3: Environment Specification
<!-- 환경 변수, 외부 API, 지원 OS, 실패 시나리오 명세 -->

- **Required Environment Variable (.env) List** and how to obtain them
- **External API/Service List**: free/paid status
- **Supported OS Scope** and OS-specific notes
- **Major Failure Scenarios and Mitigation Strategies**

### Section 4: Volume and Composition Plan
<!-- 챕터별 페이지 배분 및 이론:실습 비율 -->

- **Per-chapter Page Allocation**: total 100p or fewer
- **Theory vs. Practice Ratio**

---

## chapter_spec.md Template
<!-- 각 챕터별 집필 명세 파일 형식 -->

Format for per-chapter writing specification file:

```markdown
# CH{number} Writing Specification

## 1. Chapter Section Structure
- ## 1. {Section Name}: {Content Summary}
- ## N. Summary

## 2. Code-Section Mapping
| Section | File | Code Range |
|---------|------|------------|

## 3. Concept Explanation Hints (Why)
- Reason for using {function/class}: ...

## 4. Key Terms
- {Term (English)}: Definition

## 5. Mermaid Diagram Draft

## 6. Chapter Connections
- Concepts carried over from the previous chapter:
- Concepts passed on to the next chapter:
```

---

## Planning Verification Checklist
<!-- 기획 검증 체크리스트 -->

- [ ] Total volume is 100p or fewer
- [ ] No version compatibility conflicts in the technology stack
- [ ] No circular dependencies between chapters
- [ ] No sudden difficulty spikes relative to the reader's level
- [ ] All external APIs are free or have alternatives
- [ ] LLM Provider is designed to be switchable via `.env`
