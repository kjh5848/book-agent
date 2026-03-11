# Chapter Structure Template

## 1. Required 4-Step Structure
<!-- 모든 챕터가 반드시 준수해야 하는 4단계 구조 -->

All chapters must follow the 4-step structure below without exception.

### Step 1: Header and Introduction
<!-- 1단계: 헤더 및 도입부 -->

```markdown
# {Chapter Number}. {Chapter Title}

In this chapter, you will learn {core topic}. {1–2 sentence summary}
```

### Step 2: Concept Explanation
<!-- 2단계: 개념 설명 -->

- Use Mermaid diagrams to explain architecture or principles first.
- Guide readers to form an overall picture in their minds before beginning hands-on practice.

### Step 3: Step-by-Step Practice
<!-- 3단계: 단계별 실습 -->

- Include clear code blocks with line-by-line comments.
- **Code Quoting Rule**: Show only the core logic (10–20 lines) in the book text. Do NOT paste entire files. Add `> 전체 코드: \`src/{filename}.py\`` below each code block to direct readers to the full source. Imports, boilerplate, and error handling belong in examples/, not in the book.
- Place a `#### Code Workflow` section below each code block.

### Step 4: Summary
<!-- 4단계: 마무리 -->

```markdown
## {Last Number}. Summary

- **Key Conclusion 1**: Elaboration
- **Key Conclusion 2**: Elaboration
- **Key Conclusion 3**: Elaboration
```

## 2. Chapter Closing Rules
<!-- 챕터 마무리 규칙 -->

- **Section title**: The last section title of each chapter must always be **"정리하며"** (e.g., `## 5. 정리하며`).
- **Bullet Points**: Do not list in prose; summarize key content in bullet points.
- **Deductive structure**: Present the key conclusion first in each item, then add elaboration afterward.

## 3. Markdown Skeleton Example
<!-- 마크다운 골격 예시 -->

```markdown
# {N}. {Chapter Title}

In this chapter, you will learn about...

## 1. {Concept Section}

{Mermaid diagram}

{Concept explanation}

## 2. {Practice Section}

{Code block}

#### Code Workflow

1. **Input**: ...
2. **Process**: ...
3. **Output**: ...

> **팁: Title**
> Useful information

## 3. {Advanced Section}

{Additional practice or advanced content}

## 4. 정리하며

- **Key Point 1**: Explanation
- **Key Point 2**: Explanation
- **Key Point 3**: Explanation
```

## 4. Quality Checklist
<!-- 집필 완료 전 반드시 체크해야 하는 항목 -->

Before completing writing, verify all items below.

- [ ] **Chapter structure**: Does the order follow Introduction → Concept → Practice → Summary?
- [ ] **Last section**: Is it in the `## {N}. 정리하며` format?
- [ ] **Code Workflow**: Is there an Input/Process/Output section below every code block?
- [ ] **Technical terms**: Are technical terms accurately capitalized?
- [ ] **Bold spacing**: Is there a space before and after bold text (`**`)?
- [ ] **Practice synchronization**: Does the body code match the example project code?
- [ ] **Image paths**: Are actual image paths entered correctly?
- [ ] **No fabricated output**: Are there no fabricated LLM output text blocks? (see `style.md` §8)
- [ ] **Screenshot usage**: Are LLM execution results shown as screenshots, not text blocks?
