# 블루프린트 작성 규칙

기획안을 작성(Phase 1)할 때는 다음 요소를 반드시 포함합니다.
1. **가상의 대상 독자(Persona)**: 독자의 사전 지식 수준, 책을 읽고 난 후의 목표
2. **필수 환경 명세**: OS버전, 필요 라이브러리, 의존성 버전 등
3. **학습 목표 (Learning Objectives)**: 챕터별로 얻어가는 기술적 가치
4. **목차 초안**: 챕터 1~4 수준의 큰 줄기

## 산출물 구조 (Plan Directory Structure)

기획 문서는 단일 `plan.md` 파일이 아닌, 다음 계층 구조로 관리합니다.

```text
anti_v2_book/plan/
├── master_plan.md         # 전체 책의 개요, 분량, 챕터 구성 (Phase 1 산출물)
├── ch01/
│   ├── chapter_plan.md   # 해당 챕터의 세부 집필 플랜 (목차, 다이어그램 계획)
│   └── example_plan.md   # 해당 챕터의 예제 코드 플랜 (IPO 명세, 검증 시나리오)
├── ch02/
│   ├── chapter_plan.md
│   └── example_plan.md
└── ...
```

- `master_plan.md`는 Phase 1에서 사용자 승인을 받습니다.
- 각 챕터의 `chapter_plan.md`와 `example_plan.md`는 Phase 2 코딩 시작 전에 함께 작성하여 사용자 승인을 받습니다.

## 기획 회고 루프 (Planning Retrospective)

블루프린트(`master_plan.md`) 초안이 완성되면 즉시 코딩 단계(Phase 2)로 진입해서는 안 됩니다. 먼저 사용자에게 다음 사항들을 중심으로 **적극적인 리뷰와 피드백**을 요청해야 합니다.

1. **난이도 및 분량 적절성**: 대상 독자 수준에 비해 너무 어렵거나 방대하지 않은가?
2. **기술 스택 검증**: LLM Provider(Ollama, OpenAI 등), 데이터베이스 선택 등이 사용자가 원하는 실습 환경과 동일한가?
3. **학습 방식 일치 여부**: 단순 타이핑인지, Clone & Run 방식인지 등 사용자의 교육 철학과 부합하는가?

사용자의 피드백을 받으면 기획안을 그 즉시 수정(`replace_file_content`)하고 재승인을 요청하여 완벽한 합의(Pass)에 도달할 때까지 이 루프를 반복해야 합니다.
