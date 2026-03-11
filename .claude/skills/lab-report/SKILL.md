---
name: lab-report
description: 학생 입장에서 실습 보고서를 생성하는 스킬. 보고서 템플릿, Playwright/terminal_screenshot.py 캡처 방법, 학생 평가 기준을 포함한다.
---

# 실습 보고서 스킬

## 핵심 규칙

- 학생 관점으로 작성: "실행했습니다", "확인했습니다" (격식체 경어)
- 스크린샷은 반드시 `{project}/assets/CH{N}/`에 PNG로 저장
- 각 단계의 결과를 PASS 또는 FAIL로 표시
- 에러를 숨기지 않고 해결 과정을 포함
- 보고서는 `{project}/review/chapter_review_CH{N}.md`에 저장

## 참조 파일

| 파일 | 로드 시점 |
|------|---------|
| `references/report-template.md` | 보고서 작성 시 (항상) |
| `references/eval-criteria.md` | 종합 평가 작성 시 |
| `references/terminal-screenshot.md` | 터미널 출력을 PNG 스크린샷으로 캡처 시 |
