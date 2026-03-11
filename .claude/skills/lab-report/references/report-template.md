# Lab Report Template

<!-- 아래 구조로 `수동/review/lab_report_CH{N}.md`를 작성한다. {N}은 두 자리 숫자 (예: 08). -->

Write `수동/review/lab_report_CH{N}.md` using the structure below.
{N} is a two-digit number (e.g., 08).

---

# CH{N} {Chapter Title} — Lab Report

> Date: {YYYY-MM-DD} | Environment: {OS} | Python {version} | Reviewer: Student perspective

---

## 1. Lab Overview
<!-- 실습 개요 -->

| Item | Details |
|------|---------|
| Chapter | CH{N} {title} |
| Core Technologies | (e.g., FastMCP, LangChain ReAct, PostgreSQL) |
| Lab Objectives | (extracted from README) |
| Estimated Time | (based on README) |
| Actual Time | {measured value} |

---

## 2. Environment Setup
<!-- 환경 설정 -->

### 2-1. Prerequisites Check
<!-- 필수 조건 확인 -->

| Item | Requirement | Actual Version/Status | Result |
|------|-------------|-----------------------|--------|
| Python | 3.10+ | {actual} | PASS/FAIL |
| Docker | Running | {status} | PASS/FAIL |
| Ollama | Running | {status} | PASS/FAIL |
| Free RAM | 8GB+ | {actual} | PASS/FAIL |

### 2-2. Dependency Installation
<!-- 의존성 설치 -->

**Command:**
```bash
pip install -r requirements.txt
```

**Result:**
```
{Installation log (last 10 lines)}
```

> Installed packages: {count} | Time: {seconds}s | Result: PASS/FAIL

---

## 3. Step-by-Step Lab
<!-- 단계별 실습 -->

Each STEP follows the execution scenarios in the README in order.

### STEP {number}: {Step Name}
<!-- 각 단계별 실습 -->

**Command:**
```bash
{command executed}
```

**Execution Result:**
```
{terminal output}
```

**Screen Capture:**
![{step description}](../assets/CH{N}/{NN}_{description}.png)
*(Omit if capture is not possible)*

**Result:** PASS / FAIL / SKIP
> {one-line comment}

---

(Repeat STEP)

---

## 4. Feature Verification
<!-- 기능 검증 -->

### API Endpoint Testing
<!-- API 엔드포인트 테스트 -->

| Endpoint | Request | Response Code | Result |
|----------|---------|---------------|--------|
| POST /admin/qa/query | {"query": "..."} | 200 | PASS |
| ... | | | |

### Core Feature Scenarios
<!-- 핵심 기능 시나리오 -->

| Scenario | Input | Expected Output | Actual Output | Result |
|----------|-------|-----------------|---------------|--------|
| RAG question | "Leave policy..." | Document-based answer | {actual} | PASS |
| ... | | | | |

---

## 5. Error Resolution Log
<!-- 오류 해결 내역 -->

If no errors occurred, write "No errors".

| # | Error | Cause | Resolution | Result |
|---|-------|-------|------------|--------|
| 1 | {error message} | {cause} | {resolution} | Resolved/Unresolved |

---

## 6. Overall Evaluation
<!-- 종합 평가 -->

### Score Table
<!-- 점수표 -->

| Evaluation Item | Score (out of 5) | Basis |
|-----------------|------------------|-------|
| Setup difficulty | {score} | {basis} |
| Execution success rate | {score} | {basis} |
| Code comprehensibility | {score} | {basis} |
| Documentation quality | {score} | {basis} |
| **Total** | **{sum}/20** | |

### Student Comments
<!-- 학생 의견 -->

> {Write 2–4 sentences about the overall impression after the lab, difficulties encountered, and improvement suggestions}

### Improvement Suggestions
<!-- 개선 제안 -->

- {Specific improvement item 1}
- {Specific improvement item 2}
