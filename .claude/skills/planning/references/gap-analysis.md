# Gap Analysis Criteria

<!-- 기획 에이전트가 초안 분석 후 plan.md 작성 전에 수행하는 갭 분석 기준 -->

The planning agent performs a gap analysis after reviewing the draft and before writing plan.md.

## Priority Classification
<!-- 갭 항목의 우선순위 분류 기준 -->

| Grade | Definition |
|-------|------------|
| **Essential** | Without this, readers cannot apply to real work |
| **Recommended** | Differentiates the book when included |
| **Optional** | Advanced content for experienced readers |

## Gap Analysis Procedure
<!-- 갭 분석 절차 -->

1. **Derive domain standard curriculum**: Use WebSearch to research official documentation, practical guides, and course curricula for the technology, and list the core chapters/concepts typically included.
2. **Compare with draft**: Identify concepts or chapters missing relative to the standard.
3. **Prioritize**: Consider reader level, page limit, and relevance to the technology stack.

## Common Gap Check Items for Technical Books
<!-- 기술서 공통 갭 체크 항목 -->

- **Basic concepts**: Is there an introductory chapter?
- **Comparative analysis**: Does the book provide criteria for choosing among similar technologies/libraries?
- **Troubleshooting**: Are common errors and solutions covered?
- **Practical patterns**: Are there best practices beyond tutorials?
- **Evaluation/Validation**: Is there guidance on measuring implementation results?

## User Suggestion Message Format
<!-- 사용자 제안 메시지 형식 -->

```
## 📋 Planning Gap Analysis Results

### [Essential] Content readers need to apply immediately in real work
- {item}: {reason}

### [Recommended] Content that differentiates the book
- {item}: {reason}

### [Optional] Content useful for advanced readers
- {item}: {reason}

---
Please let me know which items to include so I can reflect them in the plan.
If you'd like to proceed with the current draft, say "Proceed as-is."
```

**Do not begin writing plan.md until this message has been output.**
