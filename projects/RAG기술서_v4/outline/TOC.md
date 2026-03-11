# 사내 문서 기반 AI 업무 비서 (RAG + MCP) — 목차

> 집필 컨셉: storytelling | 주인공: 메타코딩 (1인 개발자, 중소기업 AI 도입 담당)
> 프로젝트: "커넥트HR AI 비서"

---

## 전체 구성

- 총 챕터 수: 10개
- 예상 총 분량: 95p
- 이론 / 실습 비율: 약 25% / 75%
- 집필 구조: 문제 상황 → 기술 소개 → 해결 과정 → before/after 결과 정리

---

## 파트 구성 개요

```
PART 0.   시작하기         CH01 (5p)  + CH02 (7p)
기초                       CH03 (8p)
PART 1.   기반 구축        CH04 (10p) + CH05 (7p)
PART 2.   핵심 구현        CH06 (12p) + CH07 (12p)
PART 3.   통합             CH08 (12p) + CH09 (10p)
PART 4.   고도화           CH10 (12p)
합계                       95p
```

---

## PART 0. 시작하기

---

### CH01. 이 책의 목표와 최종 완성본 미리보기 (5p)

> 스토리: 메타코딩은 대표에게 "AI로 사내 문서 문제를 해결하라"는 요청을 받는다.
> 하루 30분씩 문서를 뒤지는 직원들, 인사팀에 쏟아지는 반복 질문 20건/일.
> 메타코딩은 RAG + MCP 조합이 중소기업에 최적임을 확인하고 프로젝트를 시작한다.

#### 1.1 이 책이 다루는 범위 (1p)

- 이 책이 해결하는 문제: 사내 문서 3,000건, 직원 1인당 문서 검색 30분/일
- RAG(검색 증강 생성) vs Fine-tuning 비교표: 비용, 데이터 요구량, 업데이트 주기, 적합 상황
- MCP(Model Context Protocol)가 필요한 이유: 정형 DB와 비정형 문서를 하나의 에이전트에서 통합 처리
- 이 책의 최종 산출물: "커넥트HR AI 비서" (정형 + 비정형 + 복합 질문 처리)
- [표] Fine-tuning vs RAG 비교 (비용·데이터·응답 속도·업데이트 주기)

#### 1.2 최종 결과물 데모 시나리오 (1p)

- 정형 질문 예시: "김철수 사원의 남은 연차는?" → DB 조회 → 즉시 응답
- 비정형 질문 예시: "신입사원 온보딩 절차를 알려줘" → 문서 검색 → 출처 포함 응답
- 복합 질문 예시: "올해 매출 상위 부서의 복지 정책을 비교해줘" → DB + 문서 조합
- [다이어그램] 질문 유형별 처리 흐름 개요

#### 1.3 아키텍처 한 장 요약 (1p)

- 전체 시스템 Mermaid 다이어그램: 사용자 → FastAPI → QueryRouter → MCP Tools / RAG Chain / ReAct Agent
- 각 구성 요소 역할 1줄 설명 (FastAPI, QueryRouter, ChromaDB, PostgreSQL, LangChain Agent)
- [다이어그램] 커넥트HR AI 비서 전체 아키텍처

#### 1.4 사용 기술 스택 (1p)

- 기술별 역할 및 메모리 요구사항 표 (Ollama + DeepSeek R1, ChromaDB, PostgreSQL, LangChain, MCP 등)
- 최소 하드웨어 스펙: RAM 16GB, 저장공간 20GB
- 권장 환경: macOS / Ubuntu 22.04+ (Apple Silicon 또는 NVIDIA GPU)
- LLM Provider 선택지: Ollama(로컬 무료) / OpenAI(클라우드 유료) / vLLM(자체 호스팅)

#### 1.5 이 책을 마치면 할 수 있는 것 (1p)

- 3가지 핵심 역량: RAG 파이프라인 구축, MCP 통합 에이전트 설계, 실전 RAG 튜닝
- 챕터별 빌드업 로드맵 요약 (CH01→CH02→...→CH10 의존성 흐름)
- [다이어그램] 챕터 의존성 그래프 (CH01부터 CH10까지 순방향 연결)
- before/after: 직원 1인 문서 검색 30분 → 30초, 인사팀 반복 질의 20건/일 → 0건

---

### CH02. 개발 환경 설정 (7p)

> 스토리: 메타코딩은 클라우드 API 비용과 사내 보안 정책 때문에 로컬 LLM을 선택한다.
> Ollama를 발견하고, 나중에 Provider를 바꿀 수 있도록 처음부터 전환 구조를 설계한다.

#### 2.1 필수 요구사항 확인 (0.5p)

- Python 3.10+, RAM 16GB+, 저장공간 20GB+, Docker, Git 설치 확인
- OS별 주의사항 표 (macOS Apple Silicon / Intel, Ubuntu 22.04+, Windows WSL2)
- 사전 실습 체크리스트 (6개 항목)

#### 2.2 Ollama + DeepSeek R1 설치 및 테스트 (1.5p)

- Ollama 설치 (OS별 가이드: macOS brew, Linux curl, Windows WSL2)
- DeepSeek R1 모델 다운로드: `ollama pull deepseek-r1:8b`
- 간단한 대화 테스트: `ollama run deepseek-r1:8b`
- 메모리 부족 시 대안: `deepseek-r1:1.5b` 경량 모델
- [코드 워크플로우] Input: 질문 문자열 / Process: Ollama API 호출 / Output: 텍스트 응답

#### 2.3 Python 가상환경 및 의존성 (0.5p)

- venv 생성 및 활성화 (OS별 명령어)
- requirements.txt 주요 패키지 설명 (FastAPI, LangChain, ChromaDB, sentence-transformers 등)
- pip install 실행

#### 2.4 PostgreSQL 설치 (1p)

- Docker Compose 기반 설치 (권장): docker-compose.yml 구조 설명
- 네이티브 설치 대안 (macOS homebrew, Ubuntu apt)
- 초기 DB 생성: `connect_hr` 데이터베이스

#### 2.5 프로젝트 클론 및 초기 설정 (0.5p)

- git clone 및 폴더 구조 설명
- .env 파일 생성 및 필수 환경변수 설정

#### 2.6 주요 의존성 목록 (0.5p)

- requirements.txt 항목별 용도 설명 표
- 버전 호환성 주의사항 (LangChain 0.3+, ChromaDB 0.5+, Python 3.10+)

#### 2.7 LLM Provider 전환 구조 (1.5p)

- .env 기반 Provider 전환 설계: `LLM_PROVIDER=ollama|openai|vllm`
- `src/llm_provider.py` 팩토리 패턴 설명 (핵심 코드 10~15줄)
- Provider별 테스트 방법: ollama(로컬), openai(API 키), vllm(자체 호스팅)
- [코드 워크플로우] Input: LLM_PROVIDER 환경변수 / Process: 팩토리 패턴 분기 / Output: LLM 인스턴스
- 전체 코드: `src/llm_provider.py`

#### 2.8 환경 검증 (1p)

- `src/verify_env.py` 실행: Ollama, Python, Docker, PostgreSQL 전항목 PASS 확인
- 각 검증 항목 설명 (연결 확인, 버전 확인, 응답 테스트)
- [코드 워크플로우] Input: 없음 / Process: 4개 서비스 연결 순차 확인 / Output: PASS/FAIL 항목 표
- 전체 코드: `src/verify_env.py`
- before/after: LLM 실행 환경 없음 → Ollama 로컬 / 월 비용 $50+ → $0 / .env 한 줄로 Provider 전환

---

## 기초

---

### CH03. LLM의 한계와 RAG의 필요성 (8p)

> 스토리: 메타코딩은 바로 DeepSeek R1에 사내 질문을 던져본다.
> "김철수 사원의 남은 연차가 며칠입니까?" — LLM은 자신 있게 틀린 답을 내놓는다.
> 환각을 직접 체험하고, RAG 아이디어를 스스로 떠올린다.

#### 3.1 [실패] LLM 단독 질의 (1.5p)

- DeepSeek R1에 사내 정보 질문: "김철수 사원의 남은 연차는?"
- 환각 체험: 실제 7일인데 "12일"이라고 자신 있게 답변
- `src/01_llm_only.py` 실행 및 결과 분석
- [코드 워크플로우] Input: 사내 정보 질문 / Process: LLM 단독 호출 / Output: 환각 포함 응답
- 전체 코드: `src/01_llm_only.py`

#### 3.2 왜 LLM은 환각을 일으키는가 (1p)

- 학습 데이터 컷오프 문제: 사내 비공개 정보는 학습에 포함되지 않음
- 파라메트릭 지식(학습 데이터) vs 컨텍스트 지식(프롬프트 주입) 구분
- [다이어그램] LLM 지식의 한계 — 사내 정보가 없는 이유

#### 3.3 [임시 해결] Context Injection 맛보기 (1.5p)

- 프롬프트에 문서 직접 붙여넣기: 정확도는 올라가지만 토큰 한계 체감
- 문서 3개만 넣어도 컨텍스트 초과 발생
- `src/02_context_injection.py` 실행
- [코드 워크플로우] Input: 질문 + 문서 전체 / Process: 프롬프트 직접 삽입 / Output: 정확도 개선 + 토큰 오류
- 전체 코드: `src/02_context_injection.py`

#### 3.4 [성공] RAG 미리보기 (2p)

- 인메모리 ChromaDB로 검색 + 답변 파이프라인 구성
- 청킹 유무 비교: 전체 문서 첨부 vs 500자 청크 검색
- `src/03_rag_preview.py` 실행: 연차 7일 정확 응답 확인
- [다이어그램] RAG 파이프라인: 질문 → 검색 → 컨텍스트 주입 → 답변
- [코드 워크플로우] Input: 질문 / Process: 청크 검색 + 프롬프트 주입 / Output: 출처 포함 정확한 답변
- 전체 코드: `src/03_rag_preview.py`

#### 3.5 [심화] DeepSeek R1 추론 능력 확인 (1p)

- RAG + 계산/추론 질문: "올해 1분기 매출 합계는?"
- `src/04_rag_reasoning.py` 실행
- [코드 워크플로우] Input: 수치 계산 질문 / Process: RAG 검색 + 추론 / Output: 계산 결과 포함 답변
- 전체 코드: `src/04_rag_reasoning.py`

#### 3.6 정리하며 (1p)

- 4단계 결과 비교표: 정확도 / 출처 포함 여부 / 토큰 효율 / 한계
- before/after: 사내 질의 정확도 0%(환각) → 85%+(출처 기반) / 토큰 사용량: 전체 문서 첨부 시 초과 → 관련 청크 500~1000토큰
- 다음 챕터 예고: "이제 제대로 된 사내 시스템부터 만들어보겠습니다"

---

## PART 1. 기반 구축

---

### CH04. FastAPI로 초간단 사내 시스템 만들기 (10p)

> 스토리: 메타코딩은 RAG 가능성을 확인하였지만, AI가 답변할 "사내 데이터"가 없다.
> 직원 정보는 Excel, 휴가 현황은 수동 집계, 매출은 부서별 파일.
> "AI 비서보다 기본 시스템이 먼저다"라는 것을 깨닫는다.

#### 4.1 프로젝트 구성 (1p)

- 폴더 구조 설명: `app/`, `templates/`, `data/`, `static/`
- .env 설정: POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB 등
- 실행 방법: `uvicorn app.main:app --reload`
- FastAPI를 선택하는 이유: async 지원, 자동 API 문서(Swagger), Pydantic 통합
- 전체 코드: `app/main.py`

#### 4.2 데이터 모델 설계 (2p)

- 3테이블 구조: `employee`, `leave_balance`, `sales`
- [다이어그램] ERD: 테이블 간 관계 (employee ↔ leave_balance, employee ↔ sales)
- `data/schema.sql` + 시드 데이터 설명
- Pydantic 스키마와 SQLAlchemy 모델의 역할 분리
- PostgreSQL을 선택하는 이유: MCP를 통한 SQL 질의 대상, 실무 표준 RDBMS
- 전체 코드: `app/models.py`, `data/schema.sql`

#### 4.3 CRUD API 구현 (3p)

- 직원 CRUD: `GET/POST/PUT/DELETE /api/employees`
- 휴가 잔여 조회 및 변경: `GET/PUT /api/leaves`
- 매출 CRUD: `GET/POST/PUT/DELETE /api/sales`
- Pydantic 요청/응답 스키마 설계
- 3테이블 구조인 이유: CH08 MCP 통합 시 현실적인 정형 데이터 시나리오 제공
- [코드 워크플로우] Input: HTTP 요청 + Pydantic 검증 / Process: SQLAlchemy ORM / Output: JSON 응답
- 전체 코드: `app/crud.py`, `app/schemas.py`

#### 4.4 관리자 Admin UI (4p)

- base.html 베이스 레이아웃: 좌측 사이드바(240px) + 메인 콘텐츠 — CH07/CH08에서 계승
- Jinja2 템플릿 기반 웹 UI 구조 설명
- 직원 목록/등록/수정 화면 (`templates/employees.html`)
- 휴가 현황 조회 화면 (`templates/leaves.html`)
- 매출 현황 대시보드 (`templates/dashboard.html`)
- Jinja2를 선택하는 이유: Python만으로 UI 구현, 별도 프론트엔드 불필요
- [다이어그램] Admin UI → FastAPI → PostgreSQL 요청 흐름
- 전체 코드: `templates/*.html`, `app/views.py`
- before/after: 직원 정보 Excel → PostgreSQL + 웹 Admin UI / 휴가 집계 30분 → 즉시 조회

---

### CH05. 사내 문서 수집 전략과 문서 표준 만들기 (7p)

> 스토리: 메타코딩은 커넥트 인사팀 서버를 열어보고 당황한다.
> "취업규칙_최종_진짜최종.pdf"와 "취업규칙_최종_v2.pdf"가 공존하고,
> 100개 넘는 파일이 하나의 폴더에 뒤섞여 있다. "Garbage In, Garbage Out"을 실감한다.

#### 5.1 어떤 문서를 넣을 것인가 (1p)

- 교재용 문서 세트 소개: HR 취업규칙, 보안 규정, 운영 전략, 예산 기안, 매출 현황
- 문서 유형별 특성: 규정류 PDF(고정 양식), 보안 DOCX(표 구조), XLSX(수치 데이터)
- 실무 문서 선정 기준: 자주 질문받는 문서, 정기 갱신 문서 우선

#### 5.2 문서 형식 지원 범위 (1p)

- PDF, DOCX, XLSX 각 형식의 특성과 파싱 난이도 비교표
- 이미지 PDF vs 텍스트 PDF 구분 (이미지 PDF 처리는 CH06 LLM 파싱, CH10 튜닝에서 심화)
- 형식별 파싱 라이브러리: pypdf, python-docx, openpyxl

#### 5.3 문서 표준 규칙 (2p)

- 파일명 규칙: `{부서}_{문서종류}_v{버전}.{확장자}` (예: `HR_취업규칙_v1.0.pdf`)
- 폴더 구조: `data/docs/{부서}/` (hr, security, ops, finance)
- [다이어그램] 표준화 전/후 폴더 구조 비교
- 메타데이터 필수 항목: doc_id, title, department, version, date, format (7개 항목)
- 파일명 규칙을 정하는 이유: 버전 관리, 부서별 분류, 출처 추적 — CH10 Self-Query Retriever에서 필수

#### 5.4 문서 수집 파이프라인 (3p)

- docs/ 폴더 구조 설계 및 실제 문서 배치 (PDF 4개, DOCX 1개, XLSX 2개)
- `src/validator.py`: 파일명 규칙 검증 + 파일 형식 확인 + 메타데이터 자동 추출
- 검증 스크립트 실행: 모든 문서 PASS 확인
- [다이어그램] 원본 문서 → 폴더 배치 → validator.py → metadata.json → CH06으로 전달
- [코드 워크플로우] Input: data/docs/ 폴더 전체 / Process: 파일명 패턴 검증 + 메타데이터 추출 / Output: 검증 결과 + metadata.json
- 전체 코드: `src/validator.py`
- before/after: 파일명 규칙 없음 → `{부서}_{종류}_v{버전}.{확장자}` 통일 / 단일 폴더 100+ 파일 → 부서별 4개 폴더 / 메타데이터 없음 → 7개 항목 자동 추출

---

## PART 2. 핵심 구현

---

### CH06. VectorDB 구축 — 문서를 검색 가능한 지식으로 바꾸기 (12p)

> 스토리: 메타코딩은 CH05에서 문서를 깔끔하게 정리하였다.
> 이제 이 문서를 AI가 검색할 수 있게 변환해야 한다.
> 그런데 취업규칙에는 표가 가득하고, 매출 현황에는 차트가 있다.
> "단순 텍스트 추출만으로는 정보가 날아간다"는 것을 깨닫는다.

#### 6.1 [Step 1] Python 파싱 테스트 (2p)

- `src/extractor.py`: 형식별 통합 텍스트 추출기
- PDF(pypdf), DOCX(python-docx), XLSX(openpyxl) 순차 실행
- 추출 결과 비교: 형식별 품질 차이 직접 확인 (깨진 문자, 표 손실, 이미지 누락)
- 한계 체감: 표/이미지/복잡한 레이아웃은 Python 파싱으로 처리 불가
- [코드 워크플로우] Input: PDF/DOCX/XLSX 파일 / Process: 형식별 파서 분기 / Output: 텍스트 + 손실 목록
- 전체 코드: `src/extractor.py`

#### 6.2 [Step 2] LLM 파싱 — Vision LLM으로 문서 이해 (2.5p)

- Vision LLM(LLaVA): PDF 페이지를 이미지로 변환 후 분석
- LLM이 추출하는 것: 텍스트 + 메타데이터(제목, 부서, 버전) + 이미지 캡션
- `src/vision_extractor.py`: PDF → 페이지 이미지 → LLM 분석 → 구조화된 결과
- [표] Python 파싱 vs LLM 파싱 비교 (품질, 속도, 비용)
- Vision LLM을 사용하는 이유: 표/이미지/복잡한 레이아웃을 이해, 메타데이터 자동 추출
- [코드 워크플로우] Input: PDF 파일 / Process: 페이지 이미지 변환 + LLaVA 분석 / Output: 구조화된 텍스트 + 메타데이터
- 전체 코드: `src/vision_extractor.py`

#### 6.3 Chunk 설계 (2p)

- Fixed-size 청킹: 500~1000자 + overlap 10~20%
- 메타데이터 부착: doc_id, title, section, department, page, source_path
- 이미지 청크: 캡처본 경로 + LLM 캡션을 텍스트 청크로 변환
- Fixed-size 청킹을 기본으로 쓰는 이유: 구현이 단순하고 예측 가능, Semantic 청킹은 CH10에서 개선
- [다이어그램] 문서 → 청크 분할 → 메타데이터 부착 구조
- 전체 코드: `src/chunker.py`

#### 6.4 임베딩 & VectorDB 저장 (2.5p)

- 임베딩 모델: `ko-sroberta-multitask` (로컬, 무료, 한국어 최적화)
- ChromaDB Collection 생성 및 문서 추가
- 텍스트 청크 + 이미지 캡션 청크를 함께 저장하는 이유: 실무 문서는 텍스트만으로 정보가 완전하지 않음
- `src/store.py`: 임베딩 + ChromaDB 저장 파이프라인
- [코드 워크플로우] Input: 청크 리스트 + 메타데이터 / Process: ko-sroberta 임베딩 + ChromaDB upsert / Output: ChromaDB 인덱스
- 전체 코드: `src/store.py`

#### 6.5 [Step 3] CLI 검증 — 쿼리로 근거 확인 (2p)

- `src/cli_search.py`: 터미널에서 쿼리 입력 → 관련 청크 + 출처 + 캡처본 경로 출력
- 텍스트 근거: 관련 문구 하이라이트
- 이미지 근거: 해당 페이지 캡처본 경로 표시
- 검색 품질 확인: k값, 유사도 점수
- CLI로 먼저 검증하는 이유: 웹 UI 없이 VectorDB 품질을 빠르게 확인, CH07에서 웹 UI 연결
- [코드 워크플로우] Input: 자연어 쿼리 / Process: 임베딩 → ChromaDB 검색 / Output: 관련 청크 + 출처 + 캡처본 경로
- 전체 코드: `src/cli_search.py`, `src/main.py`
- 전체 파이프라인 코드: `src/main.py`

#### 6.6 정리하며 (1p)

- before/after: 파일명 수동 검색 → 의미 기반 벡터 검색 / 검색 소요 시간 10~30분 → 1초 미만 / 표·차트 정보 손실 → Vision LLM 캡션으로 보존 / 검색 정확도 top-5 기준 0% → 80%+
- 다음 챕터 예고: CLI 검색을 웹 채팅 UI로 연결하는 작업

---

### CH07. RAG로 Q&A 엔진 만들기 (12p)

> 스토리: CLI 검색은 개발자인 메타코딩만 쓸 수 있다.
> 직원 30명이 브라우저에서 자연어로 질문하고, 이전 대화를 이어서 물어볼 수 있어야 한다.
> "아까 물어본 건데, 그것 말고 다른 부서 규정은?" — 멀티턴 대화가 필요하다.

#### 7.1 RAG 최소 동작 구현 (2.5p)

- 질문 → Retriever → Prompt → LLM → 답변 파이프라인
- LCEL(LangChain Expression Language) 기반 RAG 체인: `retriever | prompt | llm | parser`
- LCEL을 사용하는 이유: 파이프 연산자(|)로 가독성 높은 체인 조립, LangChain 최신 방식
- `src/rag_chain.py` 핵심 코드 (15줄)
- [코드 워크플로우] Input: 자연어 질문 / Process: ChromaDB 검색 → 프롬프트 조립 → LLM 호출 / Output: 답변 텍스트
- 전체 코드: `src/rag_chain.py`

#### 7.2 RAG 프롬프트 기본 템플릿 (1p)

- 출처 강제 규칙: "반드시 제공된 문서에서만 답변하시오"
- 모르면 "확인되지 않음" 응답 규칙: 환각 방지
- 프롬프트 템플릿 설계 패턴 (시스템 역할 + 컨텍스트 블록 + 질문)

#### 7.3 출처 표시 응답 포맷 (1.5p)

- answer + sources JSON 구조 설계
- 출처 필드: 문서명, 페이지, 관련도 점수
- 출처를 강제하는 이유: 환각 여부를 사용자가 검증 가능, 실무 신뢰도의 핵심
- `src/response_parser.py`: 응답 파서 구현
- 전체 코드: `src/response_parser.py`

#### 7.4 채팅 웹 UI (3p)

- CH04의 base.html 계승: 동일 사이드바 + 메인 콘텐츠 레이아웃 확장
- FastAPI `/api/chat` 엔드포인트 구현 (Fetch 기반)
- Jinja2 + JavaScript 채팅 UI: `templates/chat.html extends base.html`
- Fetch 방식을 사용하는 이유: 구현이 단순하고 초급 독자에게 적합
- 근거 아코디언 UI: 답변 아래 "근거: HR_취업규칙_v1.0.pdf, 15페이지" 표시
- [다이어그램] 사용자 질문 → Fetch POST → FastAPI → ChromaDB → LLM → 채팅 UI
- 전체 코드: `app/chat_api.py`, `templates/chat.html`

#### 7.5 멀티턴 대화 관리 (3p)

- 대화 히스토리 저장: 세션 기반
- `ConversationBufferWindowMemory`: 최근 N턴 대화 유지
- 이전 대화 맥락을 프롬프트에 포함하는 구조
- 세션 관리: 세션 ID 기반, 만료 정책
- 멀티턴을 추가하는 이유: 실무에서 단일 질의만으로 문제가 해결되는 경우는 드묾
- [코드 워크플로우] Input: 질문 + 세션 ID / Process: 히스토리 조회 + RAG 체인 + 히스토리 업데이트 / Output: 답변 + 업데이트된 세션
- 전체 코드: `src/conversation.py`, `app/session.py`

#### 7.6 정리하며 (1p)

- before/after: 사용 가능한 사람 개발자 1명 → 전 직원 30명 / 터미널 명령어 → 브라우저 채팅 / 텍스트 출력 → 근거 아코디언 UI / 멀티턴 불가 → 멀티턴 대화 지원 / 질의 건수 5건/일 → 50건/일 (예상)
- 다음 챕터 예고: 문서 검색 외에 DB 조회가 필요한 질문 처리

---

## PART 3. 통합

---

### CH08. 정형 MCP + 비정형 RAG 통합 에이전트 (12p)

> 스토리: RAG 채팅 UI를 직원들이 쓰기 시작했다.
> 그런데 예상치 못한 질문이 들어온다.
> "김철수 사원의 남은 연차는?" — DB에 있는 정형 데이터다.
> "매출 상위 부서의 복지 정책은?" — DB + 문서를 조합해야 한다.
> RAG만으로는 절반밖에 처리할 수 없다.

#### 8.1 정형/비정형 분리 원칙 (1.5p)

- 정형 데이터(DB): MCP + SQL 질의 경로
- 비정형 데이터(문서): VectorDB + RAG 경로
- 복합 질문: 두 경로를 순차/병렬로 조합
- [표] 질문 유형별 처리 경로 분류 기준
- [다이어그램] 사용자 질문 → QueryRouter → 정형/비정형/복합 분기

#### 8.2 질문 라우팅 전략 (2.5p)

- 1단계: 규칙 기반 라우팅 (키워드 매칭)
- 2단계: 스키마 기반 라우팅 (DB 컬럼명 매칭)
- 3단계: LLM 판단 라우팅 (LLM이 질문 분석 후 경로 결정)
- 3단계로 나누는 이유: 단순한 것에서 시작하여 왜 LLM 판단이 필요한지 점진적으로 이해
- `src/router.py` 핵심 코드 (15줄)
- [코드 워크플로우] Input: 자연어 질문 / Process: 3단계 라우팅 순서 판단 / Output: 경로 결정(정형/비정형/복합)
- 전체 코드: `src/router.py`

#### 8.3 통합 응답 전략 (3p)

- 질문 분석 → 데이터 수집 → 통합 컨텍스트 구성 → 답변 생성
- `src/agent.py`: ReAct Agent 구현 (Reasoning + Acting 반복)
- `src/mcp_tools.py`: MCP 도구 연결
- ReAct Agent를 사용하는 이유: 복합 질문을 "먼저 DB 조회, 그 다음 문서 검색" 식으로 단계적으로 해결
- MCP를 사용하는 이유: LLM이 직접 DB를 조회하는 표준화된 프로토콜, 도구 추가가 선언적
- [코드 워크플로우] Input: 복합 질문 / Process: ReAct 추론 → MCP 호출 → RAG 호출 → 통합 / Output: 정형 + 비정형 통합 답변
- 전체 코드: `src/agent.py`, `src/mcp_tools.py`

#### 8.4 대표 질문 시나리오 10개 (3p)

- 정형 4개: 연차 잔여 / 매출 합계 / 직원 목록 / 부서별 통계
- 비정형 4개: 온보딩 절차 / 보안 정책 / 복지 안내 / 출장 규정
- 복합 2개: 매출 상위 부서의 복지 정책 / 특정 직원의 휴가 규정
- 각 시나리오별 기대 응답 및 검증 기준
- 10개 시나리오를 정하는 이유: CH10 평가의 기준선, 정형/비정형/복합 패턴 커버
- 전체 코드: `tests/test_scenarios.py`

#### 8.5 통합 에이전트 웹 UI (1p)

- CH07 채팅 UI 확장: 동일 base.html + 질문 유형 표시(정형/비정형/복합) 추가
- 통합 응답 포맷: 출처 + DB 결과 병합 표시

#### 8.6 정리하며 (1p)

- before/after: 처리 가능한 질문 유형 비정형만 → 정형 + 비정형 + 복합 / 10개 시나리오 정답률 4/10 → 10/10 / 연차 조회 불가 → DB에서 즉시 조회 / 복합 질문 불가 → DB + 문서 자동 조합
- 다음 챕터 예고: 운영 환경에서 안정적으로 동작하게 하는 LangChain 표준 구성

---

### CH09. LangChain으로 연결 전략 세팅 (10p)

> 스토리: AI 비서가 인기를 끌면서 하루 질의가 100건을 넘겼다.
> LLM 호출 30초 타임아웃, 같은 질문 반복으로 불필요한 비용, 에러 로그 없음.
> "되는 것"과 "운영할 수 있는 것"은 다르다.

#### 9.1 기본 구성 3종 세트 (2p)

- Router/Agent: 질문 라우팅 + 실행 조율
- RAG Chain: 문서 검색 + 답변 생성
- MCP Tools: 외부 도구 연결
- 3종 세트가 결합되는 방식: 아키텍처 설명
- CH08과 별도 챕터로 분리하는 이유: CH08은 통합 원리, CH09는 LangChain 표준 구성과 운영에 집중
- [다이어그램] LangChain Agent → Router → 4 MCP Tools / RAG Chain / 모니터링

#### 9.2 Router 전략 (2p)

- 문서 검색 판단 로직
- DB 조회 판단 로직
- 실행 순서 결정: 직렬 vs 병렬
- 최종 응답 조합
- `src/agent_config.py` 핵심 코드
- 전체 코드: `src/agent_config.py`

#### 9.3 MCP Tool 설계 (3p)

- @tool 데코레이터 기반 4개 도구 정의
- `leave_balance`: 휴가 잔여 조회 (`src/tools/leave_balance.py`)
- `sales_sum`: 매출 합계 조회 (`src/tools/sales_sum.py`)
- `list_employees`: 직원 목록 조회 (`src/tools/list_employees.py`)
- `search_documents`: 문서 검색 (`src/tools/search_documents.py`)
- 도구 스키마 정의 및 LLM에 전달하는 구조
- 4개 도구로 한정하는 이유: 가장 빈번한 패턴 커버, 이후 @tool 추가로 확장 가능
- [코드 워크플로우] Input: LLM 도구 호출 요청 / Process: 스키마 검증 + DB/문서 조회 / Output: 구조화된 도구 응답
- 전체 코드: `src/tools/*.py`

#### 9.4 운영 설정 (2p)

- Timeout/Retry 설정: 타임아웃 발생률 15% → 2%
- 로깅: 구조화된 로그 포맷 (JSON 기반)
- 캐싱: 응답 캐시, 임베딩 캐시 — 동일 질문 응답 시간 5초 → 0.3초
- 비용 관리: 토큰 사용량 추적
- Langfuse 간략 소개: LLM 모니터링 도구 (월별 비용 예측 가능)
- 전체 코드: `src/monitoring.py`, `src/cache.py`

#### 9.5 정리하며 (1p)

- before/after: 타임아웃 발생률 15% → 2% / 동일 질문 응답 시간 5초 → 0.3초 / 에러 추적 불가 → 구조화된 로그 + Langfuse / @tool 1개 추가 소요 시간: 코드 전체 수정 → 10분
- 다음 챕터 예고: RAG 품질을 측정 가능하게 개선하는 튜닝 작업

---

## PART 4. 고도화

---

### CH10. RAG 튜닝 — 되는 수준에서 쓸만한 수준으로 (12p)

> 스토리: 2주간 운영하며 직원 피드백이 쌓인다.
> "보안 정책 물어봤는데 출장 규정이 나왔다" / "연봉 테이블을 모른다고 한다 (PDF 이미지에 있는데)"
> "증상에 맞는 처방"이 있다는 것을 알게 되고, 체계적인 튜닝을 시작한다.

#### 10.1 증상으로 시작하는 튜닝 (1p)

- [표] 문제 → 처방 매핑: "답변 부정확" → Chunk 튜닝/ReRanker / "관련 없는 문서" → Hybrid Search/메타데이터 필터링 / "질문 의도 파악 못함" → Query Rewrite
- 증상 기반으로 시작하는 이유: 실무에서는 "이론을 알아서"가 아니라 "문제가 생겨서" 튜닝을 시작

#### 10.2 Chunk 튜닝 (1p)

- Fixed-size → Semantic 청킹 비교
- overlap 비율 조정 실험: 10%, 20%, 30%
- 청크 크기 실험: 300, 500, 1000자
- [코드 워크플로우] Input: 문서 + 파라미터 / Process: 청킹 실험 → 검색 정확도 측정 / Output: 파라미터별 Precision@5 비교표
- 전체 코드: `tuning/chunk_experiment.py`

#### 10.3 Retriever 튜닝 (1p)

- k값 실험: k=3, 5, 10
- similarity threshold 적용
- metadata filtering: 부서별, 버전별 필터링
- 전체 코드: `tuning/retriever_experiment.py`

#### 10.4 ReRanker (1.5p)

- Cross-Encoder 기반 리랭킹 원리
- top_k=20으로 넓게 검색 → ReRanker → top_k=5로 정제
- 리랭킹 전후 정확도 비교: top-5 정확도 72% → 89%
- [코드 워크플로우] Input: 넓은 검색 결과(k=20) / Process: Cross-Encoder 재점수 계산 / Output: 정제된 결과(k=5)
- 전체 코드: `tuning/reranker.py`

#### 10.5 Hybrid Search (1p)

- BM25(키워드) + Vector(의미) 결합 원리
- Ensemble Retriever 구현
- 가중치 조정: alpha 파라미터
- 전체 코드: `tuning/hybrid_search.py`

#### 10.6 고급 Retriever (1p)

- Parent Document Retriever: 검색은 작은 청크, 반환은 큰 청크
- Self-Query Retriever: 메타데이터 자동 필터링 (CH05에서 설계한 메타데이터 활용)
- Contextual Compression: 반환 청크에서 관련 부분만 압축 추출
- 전체 코드: `tuning/advanced_retriever.py`

#### 10.7 Query Rewrite / Multi-Query (1p)

- HyDE(Hypothetical Document Embeddings): 가상 문서를 생성하여 검색 품질 향상
- 약어/동의어 처리
- Multi-Query: 하나의 질문을 여러 관점으로 변환
- 전체 코드: `tuning/query_rewrite.py`

#### 10.8 프롬프트 튜닝 (0.5p)

- 근거 우선 응답 구조
- "모르면 모른다" 규칙 강화: 환각률 15% → 5% (비용 0원)
- 포맷 고정: JSON/표 형식 응답

#### 10.9 PDF 이미지 처리 (1p)

- 이미지가 포함된 PDF 문제: 텍스트 추출 시 빈 결과
- LLaVA를 활용한 이미지 캡션 생성
- EasyOCR을 활용한 텍스트 추출
- 하이브리드 접근: Vision + OCR 조합
- 전체 코드: `tuning/vision_extractor.py`

#### 10.10 평가 체계 (1.5p)

- 테스트 질문 30개+ (부록 B 연동): 정형 10 + 비정형 10 + 복합 10
- Retrieval 정확도: Precision@k, Recall@k
- Answer 정확도: RAGAS (Faithfulness, Answer Relevancy)
- Hallucination Rate 측정
- before/after 비교 프레임워크
- RAGAS를 사용하는 이유: LLM 기반 자동 평가, 수작업 라벨링 없이 품질 측정
- [코드 워크플로우] Input: 테스트 질문 30개 + 기대 답변 / Process: RAG 실행 + RAGAS 채점 / Output: 지표별 before/after 비교표
- 전체 코드: `src/eval_framework.py`, `data/test_questions.json`

#### 10.11 튜닝 우선순위 가이드 + 다음 단계 (0.5p)

- 1순위: 프롬프트 튜닝 (비용 0원, 즉시 적용)
- 2순위: Chunk 크기/overlap 조정
- 3순위: ReRanker 추가
- 4순위: Hybrid Search
- 5순위: Query Rewrite
- 6순위: 고급 Retriever
- GraphRAG 소개 (다음 단계 — 한 문단): 지식 그래프 기반 RAG 확장 기법
- GraphRAG를 "다음 단계"로만 소개하는 이유: 100p 분량 제약, 초중급 독자 수준 고려

#### 10.12 정리하며 (0.5p)

- before/after: Retrieval Precision@5 72% → 89% / Answer Faithfulness(RAGAS) 0.65 → 0.88 / Hallucination Rate 15% → 3% / 이미지 PDF 처리 불가 → Vision + OCR 하이브리드 / 직원 만족도 "가끔 엉뚱한 답변" → "꽤 쓸만합니다"
- 커넥트HR AI 비서 완성: 정형 + 비정형 + 복합 질문, 멀티턴 대화, 운영 최적화, 튜닝까지 완료

---

## 부록

### 부록 A. 예제 문서 세트

- HR_취업규칙_v1.0.pdf, HR_정보보안서약서.pdf
- SEC_보안규정_v1.0.docx
- OPS_신규서비스_런칭전략.pdf
- FIN_부서별_예산기안서.xlsx, FIN_2025_상반기_매출현황.xlsx
- 사용 방법: `data/docs/{부서}/` 구조로 배치 후 CH06 인덱싱 실행

### 부록 B. 테스트 질문 30선

- 정형 10개: 연차 잔여, 매출 합계, 직원 목록, 부서별 통계 등
- 비정형 10개: 온보딩 절차, 보안 정책, 복지 안내, 출장 규정 등
- 복합 10개: 매출 상위 부서 + 복지 정책 비교, 특정 직원 + 휴가 규정 등
- CH10 평가 체계의 기준 데이터셋으로 활용: `data/test_questions.json`

### 부록 C. 코드 전체 구조

- CH02~CH10 예제 폴더 구조 일람
- 챕터별 핵심 파일 목록 및 역할 표
- 챕터 간 파일 계승 관계 (CH05 → CH06 → CH07 → CH08 흐름)

### 부록 D. 참고 자료

- LangChain 공식 문서: https://python.langchain.com
- ChromaDB 공식 문서: https://docs.trychroma.com
- Ollama 공식 문서: https://ollama.com/docs
- RAGAS 공식 문서: https://docs.ragas.io
- MCP(Model Context Protocol) 사양: https://modelcontextprotocol.io

---

## 검증 체크리스트

- [x] 총 분량이 100p 이하인가? (95p, PASS)
- [x] 모든 예제 파일이 TOC에 매핑되어 있는가? (CH02~CH10 예제 전체 매핑 완료)
- [x] 챕터 간 전환이 자연스러운가? (메타코딩 스토리 서사 흐름으로 연결)
- [x] chapter_spec의 모든 섹션이 TOC에 반영되었는가? (CH01~CH10 전 섹션 반영)
- [x] 각 챕터 첫 섹션이 메타코딩의 문제 상황으로 시작하는가? (스토리텔링 구조 적용)
- [x] 각 챕터 마지막 섹션에 before/after 결과 정리가 포함되는가? (전 챕터 반영)
- [x] 단일 챕터가 20p 이하인가? (최대 12p, PASS)
