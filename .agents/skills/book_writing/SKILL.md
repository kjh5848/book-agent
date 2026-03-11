---
name: book-writing
description: 테크 라이터 페르소나와 문체, 1개 챕터당 3단계 구성 구조 지침 모음. Use when: 실제 마크다운 본문을 작성할 때 라이터 페르소나, 문체, 챕터 구성 규칙을 확인해야 할 때 사용합니다.
---

# 문서 작성 (Writing) 스킬 셋

이 스킬은 마크다운 본문을 쓸 때 필요한 언어적 규칙과 챕터 뼈대 규칙, 자동 생성 스크립트를 제공합니다. 
마스터 워크플로우 구동 시 **가장 먼저 `persona-tech-writer.md`를 읽어 라이터 페르소나에 빙의**하는 것이 중요합니다.

## 실행 스크립트 (Scripts)
에이전트가 각 챕터 본문을 집필할 때 매번 `# 서론, # 본론` 구조를 타이핑하지 마십시오. **아래 스크립트를 실행하여 완벽한 아웃라인을 가진 빈 마크다운 파일을 생성한 후 내용을 채워넣으세요.**
- `scripts/init_chapter_md.py --chapter "01" --title "RAG 기초" --out "anti_v2_book/chapters"` -> 표준 서론/본론/결론과 다이어그램 프롬프트 플레이스홀더가 삽입된 `CH01_RAG_기초.md` 파일을 자동 생성해줍니다.

## 보조 참조 문서 (References)
- [persona-tech-writer.md](references/persona-tech-writer.md): 실리콘밸리 10년차 수석 라이터 페르소나 지시서
- [tone-and-style.md](references/tone-and-style.md): 어투, 경어체, 띄어쓰기 등 문체 규정
- [chapter-structure.md](references/chapter-structure.md): 각 책장(CH01, CH02...)의 내부 서론/본론/결론 작성 포맷
