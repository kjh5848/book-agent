# 회고 보고서: AI 업무 비서 구축 — RAG + MCP 실전 가이드

## 생성일: 2026-02-26

> 분석 범위: Phase 1(기획) ~ Phase 7(챕터 리뷰) ~ Phase 8(실습 보고서)
> 분석 대상: plan.md, chapter_spec_CH01~CH10, TOC.md, 챕터 원고 CH01~CH10, 예제 코드 CH01~CH10, verify_* 보고서, chapter_review_CH01~CH10, lab_report_CH02~CH10

---

## 1. Phase별 소요 및 재시도 분석

| Phase | 판정 | 재시도 횟수 | 주요 이슈 |
|-------|------|-----------|---------|
| Phase 1 (기획) | PASS | 0 | plan.md 5항목 전부 PASS. storytelling 컨셉, 이서연 페르소나 완벽 정의 |
| Phase 2 (코드) | CONDITIONAL_PASS | 0 | plan.md 코드 모듈 매핑과 실제 파일명 일부 상이(기능 동일). 전체적으로 높은 품질 |
| Phase 3 (목차) | PASS | 0 | TOC.md 4항목 전부 PASS. 100p 분량 정확 달성, 4단계 구조 완벽 준수 |
| Phase 4 (집필) | CONDITIONAL_PASS (10챕터 모두) | 0 | bash 코드 블록 IPO 워크플로우 부재(반복 경고). 코드-원고 발췌 정확도 전 챕터 PASS |
| Phase 7 (챕터 리뷰) | 완료 | N/A | CH01~CH10 전 챕터 리뷰. 평균 점수 27.3/30 |
| Phase 8 (실습 보고서) | 완료 | N/A | CH02~CH10 실습 보고서. 평균 점수 16.9/20 |

### Phase별 소요 분석 요약

Phase 1~4는 재시도 없이 1회 통과하는 높은 완성도를 보였습니다. CONDITIONAL_PASS가 유일한 감점 요인이며, 모두 동일한 bash 코드 블록 IPO 워크플로우 부재 패턴이었습니다. 이는 Phase 2에서 발생한 설계 결정이 Phase 4까지 이어진 구조적 패턴입니다.

---

## 2. 반복 오류 패턴 분석

### 패턴 1: bash 코드 블록에 IPO 워크플로우 미적용 (전 챕터 반복)

- **발생 위치**: CH01~CH10 전 챕터 (verify_chapter 보고서 5-2 항목 CONDITIONAL 반복)
- **근본 원인**: `code` 스킬의 "코드 블록 아래 반드시 IPO 워크플로우 배치" 규칙이 Python 코드 블록과 bash 실행 명령어 코드 블록을 구분하지 않음. writing-agent가 bash 블록을 Python 로직 코드와 동일하게 취급하여 매번 CONDITIONAL 처리.
- **영향**: 낮음 (의미상 문제 없음. 모든 챕터 CONDITIONAL_PASS로 처리됨)
- **권장 조치**: `code` 스킬에 "bash 실행 명령어 블록은 IPO 워크플로우 적용 제외" 규칙 명시

### 패턴 2: git clone URL 플레이스홀더 전 챕터 공통 문제

- **발생 위치**: CH01~CH10 모든 README.md (chapter_review에서 공통 지적)
- **현상**: `git clone https://github.com/{repo}/CH{N}_...` — 실제 GitHub URL 없이 `{repo}` 플레이스홀더 사용
- **근본 원인**: Phase 2(코드) 생성 단계에서 실제 저장소 URL이 미확정. planning-agent가 URL을 plan.md에 포함하지 않았고, code-agent가 플레이스홀더로 처리.
- **영향**: 중간 (독자가 실제 URL을 알 수 없어 저장소 클론 불가)
- **권장 조치**: plan.md에 `repo_url` 필드 추가 필수화. code-agent에 README 생성 시 실제 URL 또는 TBD 명시 안내 추가.

### 패턴 3: Docker 의존 챕터의 Mock 대안 부재 (CH03, CH04, CH08)

- **발생 위치**: CH03 개발환경, CH04 베이스시스템, CH08 통합에이전트
- **현상**: Docker/PostgreSQL 없으면 실습의 50~100%가 SKIP. SQLite 기반 Mock DB 대안 없음.
- **근본 원인**: planning-agent가 Docker를 필수 전제로 설계. code-agent가 Mock DB 폴백 로직을 구현하지 않음.
- **영향**: 높음 (macOS PEP 668 환경, Docker 미설치 학습자에게 치명적)
- **권장 조치**: code-agent에 "Docker 의존 챕터에는 SQLite/in-memory 폴백 필수" 규칙 추가.

### 패턴 4: 첫 실행 시 모델 다운로드 시간 미안내

- **발생 위치**: CH02(ChromaDB+sentence-transformers), CH06(sentence-transformers 470MB), CH10(CrossEncoder 90MB)
- **현상**: 첫 실행 시 수 분 소요되지만 챕터/README에 안내 없어 독자가 멈춘 것으로 오해.
- **근본 원인**: writing-agent가 기술적 구현 설명에 집중하고 사용자 경험(UX) 측면의 대기 시간 안내를 놓침.
- **영향**: 중간 (입문자 이탈 유발 가능)
- **권장 조치**: writing-agent에 "외부 모델/패키지 다운로드가 있는 경우 예상 소요 시간 안내 필수" 규칙 추가.

### 패턴 5: 챕터 간 선행 의존성 표기 불충분

- **발생 위치**: CH07(CH06 필요), CH08(CH06, CH07 필요), CH09(CH06, CH07, CH08 필요)
- **현상**: 선행 챕터 없이 실행 시 오류 발생. README에 "CH06 사전 실행 권장" 정도만 안내.
- **근본 원인**: 챕터 간 데이터 흐름이 긴밀하지만(CH06 ChromaDB → CH07 → CH08 → CH09) 독립 실행 경로가 Mock 모드로만 처리.
- **영향**: 중간 (실습 순서대로 진행하면 문제 없으나 챕터를 건너뛰거나 재시작 시 혼란)
- **권장 조치**: README에 "선행 챕터 체크리스트" 섹션 추가. 또는 샘플 ChromaDB/데이터를 각 챕터에 내장.

---

## 3. 스킬 개선 제안

| 스킬 | 개선 대상 파일 | 제안 내용 | 우선순위 |
|------|-------------|---------|---------|
| `code` | references/conventions.md | "bash 실행 명령어 코드 블록은 IPO 워크플로우 적용 제외" 명시 | 높음 |
| `code` | references/conventions.md | "Docker 의존 예제에는 SQLite/in-memory Mock DB 폴백 필수" 규칙 추가 | 높음 |
| `writing` | references/style.md | "외부 모델/패키지 다운로드 포함 단계에는 예상 소요 시간(분) 안내 필수" 추가 | 높음 |
| `writing` | references/chapter-structure.md | "챕터 선행 의존성 체크리스트 섹션 README에 포함" 규칙 추가 | 중간 |
| `planning` | references/plan-template.md | `repo_url` 필드를 plan.md 필수 항목으로 추가 | 중간 |
| `verification` | references/checklist.md | bash 코드 블록 IPO 워크플로우 예외 조건 명시 → CONDITIONAL 반복 제거 | 중간 |
| `lab-report` | references/eval-criteria.md | 실행 가능 환경 제약 시 "환경 제한" 점수 기준 추가 (Docker SKIP 처리 방법) | 낮음 |

---

## 4. 에이전트 프롬프트 개선 제안

| 에이전트 | 개선 대상 | 제안 내용 |
|---------|---------|---------|
| v1-planning-agent | plan.md 생성 규칙 | `repo_url` 필드 필수 포함. Docker 의존 챕터 목록에 "Mock DB 대안 필요" 플래그 명시 |
| v1-code-agent | README 생성 지침 | git clone URL에 실제 URL 또는 `{repo_url}` 변수 사용. "첫 실행 시 다운로드 항목과 예상 소요 시간 README에 명시" 지시 추가 |
| v1-code-agent | 예제 코드 생성 규칙 | Docker 의존 챕터: SQLite/in-memory Mock DB 폴백 필수. 각 챕터 data/ 디렉토리에 독립 실행 가능한 샘플 데이터 포함 |
| v1-writing-agent | 실습 섹션 작성 지침 | 첫 pip install 시 다운로드 발생 패키지(sentence-transformers, chromadb, CrossEncoder 등)에 소요 시간 안내 필수 |
| v1-writing-agent | 선행 의존성 안내 | 챕터 도입부에 "이전 챕터에서 생성한 파일이 필요한 경우" 체크리스트 박스 추가 지시 |
| v1-writing-verifier | 검증 체크리스트 | bash 블록 IPO 워크플로우 예외 조건 명시하여 불필요한 CONDITIONAL 제거 |
| v1-chapter-reviewer | 리뷰 기준 | Docker 미설치 환경을 기준 환경으로 명시. "실행 재현성" 평가 시 Docker 없는 경우도 포함 |
| v1-lab-reporter | 실습 프로세스 | Docker 미설치 시 자동으로 Mock 모드로 전환하는 선처리 단계 추가 |

---

## 5. 프로세스 개선 (Lessons Learned)

### 5.1. 스토리텔링 기법의 탁월한 효과

이서연 → 박민준 → 김도현의 3인 캐릭터 구조가 기술 설명을 자연스러운 대화로 변환하는 데 매우 효과적이었습니다. "세상에, 진짜 찾아오네요!"(CH06), "감으로 고치지 말고, 테스트 케이스를 만들자"(CH10) 같은 대화가 독자의 학습 동기를 지속시켰습니다. 이 패턴은 다음 프로젝트에서도 반드시 유지해야 합니다.

**교훈**: story_persona에 배경 상황과 성격을 구체적으로 정의할수록 집필 품질이 높아집니다. 캐릭터 간 역할 분담(이서연=실습 주체, 박민준=기술 멘토, 김도현=비즈니스 관점)이 챕터마다 일관적으로 유지된 것이 효과적이었습니다.

### 5.2. Mock 모드 설계의 중요성

Docker/Ollama 없이도 실습 가능한 Mock 모드가 있는 챕터(CH01, CH02, CH05, CH09)는 실습 보고서 점수가 평균 19/20점인 반면, Docker 의존적인 챕터(CH03, CH04, CH08)는 평균 14/20점이었습니다. **Mock 모드 설계는 입문자 친화성의 핵심 지표**입니다.

**교훈**: 모든 챕터는 Docker/외부 API 없이도 기본 흐름을 체험할 수 있는 Mock 모드를 기본 제공해야 합니다. 특히 실제 DB 조회(MCP 도구)는 SQLite in-memory 폴백이 필수입니다.

### 5.3. 코드-원고 발췌 정확도는 이 시스템의 강점

Phase 2(코드 생성) 이후 Phase 4(집필)에서 예제 코드와 챕터 원고의 발췌 일치율이 10챕터 모두에서 100%에 가까웠습니다. code-agent가 먼저 완전한 코드를 생성하고, writing-agent가 그 코드를 발췌하는 구조가 효과적으로 작동했습니다.

**교훈**: "코드 먼저, 집필 나중"의 Phase 2→4 순서는 코드-원고 동기화 품질을 보장하는 핵심 요소입니다. 이 순서를 절대 역전시키지 마십시오.

### 5.4. 단방향 의존성 DAG 설계의 가치

CH01 → CH02 → CH03 → ... → CH10의 단방향 의존성 구조가 순환 없이 명확했습니다. 단, CH06→CH07→CH08→CH09의 데이터 의존성(ChromaDB, PostgreSQL)이 강해 독자가 챕터를 건너뛸 수 없었습니다.

**교훈**: 다음 프로젝트에서는 각 챕터에 독립 실행 가능한 샘플 데이터를 포함하여, 챕터를 어느 것부터 시작해도 기본 흐름을 확인할 수 있는 구조를 설계해야 합니다.

### 5.5. 자동 모드의 장단점 평가

**장점**: Phase 1~4가 재시도 없이 완성된 고품질 산출물을 생성. 10개 챕터를 일관된 품질로 작성. 검증 보고서가 자동 생성되어 품질 추적 가능.

**단점**: 플레이스홀더(git clone URL) 처리가 시스템 전체에 퍼짐. Docker 없는 환경에서의 Mock 대안 설계가 자동으로 이루어지지 않음. 독자 UX(다운로드 시간 안내) 같은 "인간적 세부사항"이 자동 에이전트에서 간과됨.

**권장**: 자동 모드에 "독자 관점 체크리스트(Reader UX Checklist)" Phase를 추가. 집필 완료 후 자동으로 chapter_reviewer가 실행되어 독자 관점 품질을 검증하는 구조가 효과적.

### 5.6. v1-chapter-reviewer와 v1-lab-reporter의 가치

이번 Phase 7~8에서 수행한 독자 리뷰와 실습 보고서가 Phase 1~4 검증에서 놓친 문제들(Docker 의존성, 다운로드 시간, URL 플레이스홀더)을 명확히 식별했습니다. **독자 관점 검증은 기술적 검증과 분리하여 별도 Phase로 운영하는 것이 필수**입니다.

---

## 6. 챕터별 품질 요약

### 챕터 리뷰 점수 (Phase 7)

| 챕터 | 제목 | 점수 | 등급 | 주요 이슈 |
|------|------|------|------|---------|
| CH01 | 목표와 미리보기 | 27/30 | 우수 | venv 안내 없이 pip 직접, git clone URL |
| CH02 | 기초 RAG | 28/30 | 우수 | ChromaDB 설치 시간 미안내, Step 4 출력 예시 없음 |
| CH03 | 개발 환경 구축 | 29/30 | 탁월 | Python 3.12+ 호환성 미안내 |
| CH04 | 베이스 시스템 | 26/30 | 양호 | Docker 없으면 전체 막힘, MCP 설명 빠름 |
| CH05 | 사내 문서 표준화 | 29/30 | 탁월 | Word 처리 코드 미완성 |
| CH06 | 벡터 DB 구축 | 29/30 | 탁월 | sentence-transformers 다운로드 시간 미안내 |
| CH07 | RAG Q&A 엔진 | 28/30 | 우수 | CH06 선행 의존성, LangChain 버전 주의 없음 |
| CH08 | 통합 에이전트 | 25/30 | 양호 | Docker 의존성 강함, ReAct 출력 예시 없음 |
| CH09 | LangChain 연결 | 29/30 | 탁월 | log 경로 auto-create 미안내 |
| CH10 | RAG 튜닝 | 28/30 | 우수 | CrossEncoder 다운로드 시간, 재색인 안내 부족 |
| **평균** | | **27.3/30** | **우수** | |

### 실습 보고서 점수 (Phase 8)

| 챕터 | 제목 | 점수 | 등급 | 실행 성공률 |
|------|------|------|------|---------|
| CH02 | 기초 RAG | 19/20 | EXCELLENT | 100% (Mock) |
| CH03 | 개발 환경 | 15/20 | GOOD | 75% (Docker SKIP) |
| CH04 | 베이스 시스템 | 12/20 | FAIR | 0% (Docker SKIP) |
| CH05 | 사내 문서 표준화 | 19/20 | EXCELLENT | 100% |
| CH06 | 벡터 DB 구축 | 20/20 | EXCELLENT | 100% |
| CH07 | RAG Q&A 엔진 | 17/20 | GOOD | 80% (CH06 의존) |
| CH08 | 통합 에이전트 | 14/20 | GOOD | 50% (Docker SKIP) |
| CH09 | LangChain 연결 | 19/20 | EXCELLENT | 100% (Mock) |
| CH10 | RAG 튜닝 | 17/20 | GOOD | 80% |
| **평균** | | **16.9/20** | **GOOD** | |

---

## 7. 다음 프로젝트를 위한 핵심 권장사항

1. **plan.md에 `repo_url` 필드와 `docker_free_option` 플래그 필수 추가** — URL 플레이스홀더 문제와 Docker 의존성 문제를 기획 단계에서 해결.

2. **모든 챕터에 독립 실행 샘플 데이터 내장** — `data/sample/` 폴더에 해당 챕터만으로 실행 가능한 최소 데이터 포함. 선행 챕터 완료 없이도 기본 실습 가능.

3. **자동 파이프라인에 "독자 UX 체크리스트" 스텝 추가** — 집필 완료 직후, 외부 패키지 다운로드 시간 안내, Mock 모드 완전성, 선행 의존성 표기를 자동으로 검사하는 스텝.

4. **bash 코드 블록 IPO 워크플로우 예외 규칙 스킬에 명시** — 10챕터에 걸친 반복 CONDITIONAL 패턴 제거.

5. **Phase 7(독자 리뷰)를 Phase 4 직후 자동 실행으로 통합** — 독자 관점 피드백을 더 빠르게 반영하여 집필 품질을 실시간으로 개선.
