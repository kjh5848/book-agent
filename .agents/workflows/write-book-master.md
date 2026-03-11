---
description: 안티그래비티 도서 집필 파이프라인 마스터 워크플로우 (단일 스크립트 기반)
---
# 안티그래비티 마스터 집필 파이프라인

이 워크플로우는 `anti_v2_book/outline/` 폴더에 위치한 기획안 초안을 바탕으로 전체 집필 과정을 4단계(Phase)로 나누어 수행합니다. 각 단계별로 사용자에게 승인을 요청하며(BlockedOnUser), 모듈화된 레고 블록식 스킬 폴더(`.agents/skills/`)들을 능동적으로 참조(view_file)하여 작업합니다.

사전 준비:
- `anti_v2_book/outline/` 디렉토리에 대상 도서의 핵심 키워드/목차 초상 명세가 있는지 확인.
- 없다면 사용자에게 초안(Markdown 형식) 작성을 요청(`notify_user`)하고 대기.

---

## Phase 1: 전체 기획 및 구조화 (Planning)
이 단계에서는 초반 목차와 집필의 방향성 뼈대를 도출합니다.
- [ ] 현재 워크스페이스 내에 존재하는 모든 **book_** 접두어로 시작하는 스킬 디렉토리(`.agents/skills/`)를 탐색합니다.
- [ ] **가장 먼저 `book_writing/references/persona-tech-writer.md` 파일을 찾아 읽고(`view_file`), 실리콘밸리 10년차 수석 테크 라이터 페르소나에 100% 빙의하십시오.**
- [ ] 이어서 `book_planning/` 디렉토리와 `book_writing/` 디렉토리 아래의 규칙 문서 파일들을 모두 찾아 읽으십시오. 
- [ ] `anti_v2_book/outline/` 에 위치한 문서를 바탕으로 대상 독자의 수준 및 집필 목표를 분석합니다.
- [ ] 파악된 규칙에 의거하여 책 전체 개요, 분량 배분, 챕터 구성이 담긴 **`anti_v2_book/plan/master_plan.md`** 파일을 생성합니다.
- [ ] 생성한 `master_plan.md`를 바탕으로 **기획 검증 체크리스트(`book_planning/references/plan-validation.md`)를 필수적으로 실행**하고 점검합니다. 미달 시 스스로 보완합니다.
- [ ] **[기획 고도화]** 체크리스트 6항을 가동하여, 누락된 최신 트렌드/실무 케이스를 능동적으로 추론하여 사용자에게 제안합니다.
- [ ] 사용자에게 `master_plan.md` 승인을 요청(`notify_user`, `BlockedOnUser: true`)합니다. **승인 전까지 절대 다음 단계(Phase 2)로 넘어가지 마십시오.**

---

## Phase 2: 실습 예제 코드 생성 및 물리적 검증 (Execution & Verification)
이 단계에서는 본문에 삽입될 코드들의 실제 구동 여부를 가상환경에서 먼저 검증합니다.
- [ ] `book_code_python/` 디렉토리 아래의 스킬 규칙 문서들을 전부 찾아 읽으십시오.
- [ ] Phase 1에서 승인된 `master_plan.md`를 참고하여, `anti_v2_book/examples/` 하위에 각 챕터별 폴더를 준비합니다.
- [ ] 실제 파이썬 코드를 작성하기 **전에**, 반드시 다음 순서를 따르십시오.
  - **1단계**: 해당 챕터의 `anti_v2_book/plan/chXX/chapter_plan.md`(집필 플랜)를 먼저 작성하십시오. (세부 목차, 다이어그램 계획 포함)
  - **2단계**: 해당 챕터의 `anti_v2_book/plan/chXX/example_plan.md`(예제 코드 플랜)를 작성하십시오. (파일 구성도, IPO 명세, 검증 시나리오 포함)
  - **3단계**: `chapter_plan.md`와 `example_plan.md`를 **반드시 함께** 사용자에게 승인 요청(`notify_user`, `BlockedOnUser: true`)합니다. 승인 전까지 코딩을 시작하지 마십시오.
- [ ] 승인된 `example_plan.md`를 설계도로 삼아 `examples/chXX/` 내의 파이썬 코드를 작성합니다.
- [ ] 각 예제 디렉토리마다 **초보자 친화적인 상세한 `README.md`**를 반드시 포함하여 작성합니다.
- [ ] 🚨 **가장 중요한 규칙**: 사용자 가상환경(터미널)에 접근해 코드를 직접 실행하여 **물리적으로 검증**(`run_command`)합니다. 에러 발생 시 스스로 패치하고 다시 검증합니다.
- [ ] 실습 코딩을 끝마쳤다면, `book_visual/references/image-guide.md` 스킬 문서의 **Type C (성공 결과화면 캡처)** 규칙에 따라 성공 화면을 `anti_v2_book/assets/`에 저장하십시오.
- [ ] 작성/검증된 코드가 담긴 디렉토리 목록과 에셋(`assets/`)을 요약해 사용자에게 검토를 요청(`notify_user`, `BlockedOnUser: true`)하고 승인을 대기합니다.

---

## Phase 3: 최종 목차(TOC) 확정 (Table Of Contents)
이 단계에서는 검증된 코드를 기반으로 책의 뼈대를 최종적으로 고정합니다.
- [ ] 승인된 `plan.md` 와 `examples/` 코드를 조합하여, 각 장(Chapter)별로 집필될 세부 마크다운 파일들의 목록과 개요가 담긴 최종 `anti_v2_book/plan/TOC.md` 를 작성합니다.
- [ ] 사용자에게 `TOC.md` 의 검토를 요청(`notify_user`, `BlockedOnUser: true`)하고 승인을 대기합니다.

---

## Phase 4: 전체 본문 집필 및 자동 조판 (Writing)
이 단계에서는 각 챕터별로 실제 마크다운 문서를 집필합니다.
- [ ] `book_visual/references/image-guide.md` 를 다시 한 번 상기하십시오. (특히 **원칙 B: 개념 이해 보조용 시각적 비유 프롬프트 선주입** 숙지)
- [ ] `TOC.md` 를 순회하며 본문 마크다운 파일들을 생성합니다.
  - **[필수 자동화]** 빈 파일을 수동으로 만들지 말고, 각 챕터를 시작할 때 반드시 아래 스크립트를 먼저 실행하여 아웃라인 뼈대를 구성하세요.
  - `python3 .agents/skills/book_writing/scripts/init_chapter_md.py --chapter "01" --title "RAG 기초" --out "anti_v2_book/chapters"`
- [ ] 각 장비 집필 시 **Type A (아키텍처/흐름 Mermaid 다이어그램)** 을 개념 설명부나 실습 중간중간 필요할 때마다 자유롭게 삽입합니다.
- [ ] 초보자가 단번에 이해하기 어려운 추상적 개념, 복잡한 로직, 혹은 단계적 변화를 설명해야 하는 분기점마다 **Type B (Gemini 이미지 생성 프롬프트)** 를 마크다운 주석 형태(`<!-- [Gemini 이미지 프롬프트]: "..." -->`)로 **문맥에 맞게 실시간으로 직접 주입**하면서 글을 이어갑니다. 
- [ ] 실습 챕터에는 이전 Phase 2에서 만들어 둔 **Type C (결과 에셋 링크)** 및 캡처 사진 삽입 위치를 적절한 캡션과 함께 배치합니다.
- [ ] 챕터를 모두 작성한 후, `book_verification/` 디렉토리 아래의 검증 룰(오탈자, 어투 유지 등)을 읽고 자체적으로 전체 마크다운 파일들을 순회 검수합니다.
- [ ] 본문 집필이 모두 끝나면 사용자에게 완료를 알리고 승인을 대기합니다(`notify_user`, `BlockedOnUser: true`).

---

## Phase 5: 프로젝트 회고 및 시스템 개선 (Retrospective)
이 단계에서는 산출물 완성 후, AI 시스템 자체의 능력을 레벨업하기 위해 사용자 피드백을 수집하고 워크플로우/스킬을 업데이트합니다.
- [ ] Phase 4가 끝나면, **반드시 사용자에게 다음 질문을 던지십시오(`notify_user`, `BlockedOnUser: true`).**
  > "책 집필이 완료되었습니다! 이번 작업 과정에서 제가 부족했던 부분이나, 워크플로우 및 스킬 문서에 추가/개선했으면 하는 내용이 있으신가요?"
- [ ] 사용자의 피드백(답변)을 수령하면, 해당 내용을 심도 깊게 분석합니다.
- [ ] 분석 결과를 바탕으로 `.agents/workflows/` (마스터 워크플로우 등) 또는 `.agents/skills/` (관련 지식 프롬프트)의 **실제 마크다운 파일들을 찾아 능동적으로 수정 및 업데이트(`replace_file_content`)** 합니다. (예: "다음엔 다이어그램 이렇게 그려줘" -> `book_visual` 스킬 수정)
- [ ] 시스템 업데이트사항과 프로젝트 종합 리뷰를 담은 최종 `anti_v2_book/review/retrospective.md` 리포트를 작성하여 저장합니다.
- [ ] 모든 회고 시스템 업데이트가 완료되면 최종적으로 사용자에게 보고하고 파이프라인을 종료합니다.
