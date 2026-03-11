# Page Volume Management Rules

## 1. Absolute Constraints
<!-- 절대 불가침 제약 조건 -->

- **Total pages**: 100 pages or fewer (absolutely non-negotiable)
- **Single chapter**: 20 pages or fewer
- **Exceeding the target is strictly prohibited**

## 2. Page Allocation Matrix
<!-- 파트·챕터별 페이지 배분 매트릭스 -->

```text
[Part 1. Fundamentals] CH01 (Xp) / CH02 (Xp)
[Part 2. Hands-on]     CH03 (Xp) / CH04 (Xp)
[Appendix]             Error Guide (Xp)
Total: 100p or fewer
```

## 3. In-Chapter Composition Ratio
<!-- 챕터 내 구성 요소별 비율 기준 -->

Use the following ratios as a reference within each chapter:

| Component | Ratio | Example (10p chapter) |
|-----------|-------|-----------------------|
| Introduction | 10% | 1p |
| Concept Explanation | 20% | 2p |
| Hands-on Practice | 50% | 5p |
| Advanced / Error Handling | 10% | 1p |
| Summary | 10% | 1p |

## 4. Theory vs. Practice Ratio
<!-- 이론과 실습의 비율 기준 -->

- **Default ratio**: Theory 30%, Practice 70%
- Beginner audience: Theory 40%, Practice 60%
- Advanced audience: Theory 20%, Practice 80%

## 5. Page Estimation Criteria
<!-- 페이지 산정 기준 -->

- Approximately 40 lines of Markdown = 1 page
- Code blocks are counted including code lines
- Mermaid diagram = approximately 0.5 pages
- Image = approximately 0.5–1 page

## 6. TOC Verification Checklist
<!-- 목차 검증 체크리스트 -->

- [ ] Is (number of chapters × average pages) 100 pages or fewer?
- [ ] Does the learning curve flow naturally from introduction to advanced topics?
- [ ] Does each chapter stand alone as a meaningful unit?
- [ ] Can the reader see a working result in the first chapter? (early sense of achievement)
