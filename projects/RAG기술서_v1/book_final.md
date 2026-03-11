# AI 업무 비서 구축 — RAG + MCP 실전 가이드

> 생성일시: 2026-02-26 06:51

---

## 목차

# AI 업무 비서 구축 — RAG + MCP 실전 가이드

## 상세 목차

---

### 전체 구성

- 총 챕터 수: 10개
- 예상 총 분량: 100페이지
- 이론/실습 비율: 27% / 73%
- 대상 독자: Python 기초는 알지만 LLM/RAG는 처음인 초급 개발자

---

### CH01. 이 책의 목표와 최종 완성본 미리보기 (6p)

**이 챕터에서 답하는 질문:** "이 책은 무엇을 만들고, 왜 그 방식인가?"

#### 1.1 이 책이 만드는 것 (1p)

**키워드:** RAG(Retrieval-Augmented Generation), 로컬 LLM

- Fine-tuning이 아닌 RAG 파이프라인을 선택하는 이유
- 외부 클라우드 API 없이 로컬 LLM만으로 구성하는 원칙
- 최종 완성본의 데모 화면 미리보기 (RAG Q&A + MCP Agent)

#### 1.2 시나리오로 보는 AI 업무 비서 (2p)

**키워드:** 질문 라우터(Question Router), MCP Tool

- 복합 질의 예시: "김철수 씨의 남은 연차는 며칠이고, 연차 사용 기준은 어떻게 되나요?"
- 단계별 처리 흐름 추적 (질문 입력 → 라우팅 → DB 조회/문서 검색 → 응답 합성)
- 최종 답변 예시 (출처 포함)

| 단계 | 동작 | 구성 요소 |
|------|------|---------|
| ① 질문 라우팅 | "연차 잔여일" → 정형, "연차 사용 기준" → 비정형 분류 | 질문 라우터 |
| ② MCP Tool 호출 | PostgreSQL에서 잔여 연차 조회 | MCP Tool + PostgreSQL |
| ③ RAG Chain 호출 | 사내 규정 문서 벡터 검색 | ChromaDB + 임베딩 |
| ④ 응답 합성 | DB 결과 + 문서 청크로 자연어 답변 생성 | Ollama (DeepSeek R1) |

#### 1.3 전체 아키텍처 한 장 요약 (1p)

**키워드:** ChromaDB, PostgreSQL

- Mermaid 다이어그램: 사용자 → 라우터 → MCP Tool / RAG Chain → LLM → 최종 답변
- 각 구성 요소의 역할 한 줄 설명

#### 1.4 사용 기술 스택 상세 (1p)

**키워드:** Ollama, LangChain 0.3 (LCEL)

- 기술 선택 이유와 버전 정리 표 (Python 3.11, Ollama + DeepSeek R1, LangChain 0.3, ChromaDB 0.5, PostgreSQL 16, FastAPI 0.110)
- 모든 서비스가 무료·로컬 구성임을 강조

#### 1.5 이 책을 마치면 할 수 있는 것 (0.5p)

- 독자가 달성할 역량 목록 (5가지)
- 확장 가능성: Graph RAG, 멀티에이전트 등

#### 1.6 정리하며 (0.5p)

- 핵심 요약: RAG 선택 이유, 로컬 LLM 선택 이유, MCP 도입 이유
- CH02 예고: "이 시스템을 직접 구축하기 위해, 2장에서 Ollama, PostgreSQL, Python 가상환경을 세팅합니다"

> 예제 코드: 없음 (아키텍처 설명 중심)

---

### CH02. 개발 환경 구축 (8p)

**이 챕터에서 답하는 질문:** "이 책의 모든 실습을 실행할 수 있는 환경을 갖추었는가?"

#### 2.1 Ollama 설치 및 DeepSeek R1 모델 다운로드 (2p)

**키워드:** Ollama, DeepSeek R1

- OS별 Ollama 설치 방법 (macOS / Ubuntu / Windows WSL2)
- 모델 다운로드: `ollama pull deepseek-r1`, `ollama pull nomic-embed-text`
- 동작 확인: `ollama run deepseek-r1` 으로 간단한 응답 테스트

#### 2.2 PostgreSQL 설치 및 초기 설정 (2p)

**키워드:** Docker Compose, PostgreSQL 16

- Docker Compose로 PostgreSQL 컨테이너 구동
- `docker-compose.yml` 구조 설명
- 접속 확인: psql 또는 curl로 헬스체크
- Docker Compose를 쓰는 이유: 환경 격리, 재현성, 초기화 용이

#### 2.3 Python 3.11 가상환경 및 패키지 설치 (2p)

**키워드:** venv, requirements.txt

- Python 3.11 버전 확인 및 가상환경 생성 (`python -m venv venv`)
- `requirements.txt` 기반 패키지 설치 (`langchain==0.3.x`, `chromadb>=1.0.9`, `psycopg2-binary` 등)
- 설치 확인: 주요 패키지 임포트 테스트

#### 2.4 환경 변수(.env) 구성 및 LLM Provider 스위칭 설계 (1.5p)

**키워드:** python-dotenv, LLM_PROVIDER

- `.env.example` 파일 복사 및 항목별 설명
- `config.py`로 환경 변수 로딩 패턴 (LLM_PROVIDER 기반 전환 구조)
- .env 파일로 설정을 분리하는 이유: 비밀번호 하드코딩 방지, 환경별 전환

#### 2.5 환경 전체 동작 확인 (0.5p)

**키워드:** verify_env.py

- `src/verify_env.py` 실행으로 6가지 항목 일괄 점검 (Python 버전, .env 파일, 환경 변수, 패키지, Ollama, PostgreSQL)
- PASS / FAIL 결과 해석 및 자주 발생하는 오류 대응

#### 2.6 정리하며 (0.5p)

- 핵심 요약: Ollama + DeepSeek R1, Docker + PostgreSQL, venv + requirements.txt, .env 설정 완료
- CH03 예고: "환경이 완성되었습니다. 3장에서는 LLM의 한계를 직접 체험합니다"

> 예제 코드: `src/verify_env.py`, `.env.example`, `docker-compose.yml`, `requirements.txt`, `src/config.py`

---

### CH03. DeepSeek R1으로 체험하는 LLM의 한계와 RAG의 필요성 (8p)

**이 챕터에서 답하는 질문:** "LLM이 왜 실패하고, RAG는 어떻게 그것을 해결하는가?"

#### 3.1 [실패] LLM 단독 질의의 한계 (2p)

**키워드:** 환각(Hallucination), 학습 데이터 컷오프

- `01_llm_only.py` 실행: DeepSeek R1에 사내 정보를 질문하여 환각 응답 직접 체감
- 환각이 발생하는 이유: 학습 데이터 컷오프, 사내 비공개 정보 부재, 확률적 토큰 예측의 본질
- 실제 환각 응답 예시 (박스 처리)

#### 3.2 왜 LLM은 환각을 일으키는가 (1p)

**키워드:** 트레이닝 컷오프, 확률적 언어 모델

- 학습 데이터 컷오프의 의미와 사내 비공개 데이터 부재 문제
- "확신 있는 거짓말"이 발생하는 메커니즘 (다음 토큰 예측 원리)

#### 3.3 [임시 해결] Context Injection 맛보기 (1.5p)

**키워드:** Context Injection, 토큰 윈도우

- `02_context_injection.py` 실행: 문서를 프롬프트에 직접 붙여넣어 응답 개선 체험
- 응답은 개선되지만 한계 체감: 토큰 윈도우 초과, 문서가 많아지면 느려지고 확장 불가

#### 3.4 [성공] RAG 미리보기 + 청킹 비교 (2p)

**키워드:** RAG, 청킹(Chunking), 인메모리 벡터스토어

- `03_rag_preview.py` 실행 (인메모리 ChromaDB, 영속화 없음 — 개념 체험용)
- Part A (청킹 없음) vs Part B (청킹 있음) 검색 정밀도 나란히 비교
- 청킹의 필요성을 수치로 직접 확인

#### 3.5 [심화] DeepSeek R1 추론 능력 확인 (1p)

**키워드:** 추론(Reasoning), RAG + LLM 조합

- `04_rag_reasoning.py` 실행: RAG로 검색한 문서를 기반으로 계산·추론 질문에 답하는 체험
- DeepSeek R1의 `<think>` 태그를 통한 추론 과정 확인

#### 3.6 정리하며 (0.5p)

- 핵심 요약: LLM 단독 → Context Injection → RAG 미리보기 → RAG + 추론의 4단계 비교
- CH04 예고: "RAG가 왜 필요한지 확인했습니다. 4장에서 시스템 인프라를 확보합니다"

> 예제 코드: `01_llm_only.py`, `02_context_injection.py`, `03_rag_preview.py`, `04_rag_reasoning.py`, `requirements.txt`

---

### CH04. 베이스 시스템 확보 (8p)

**이 챕터에서 답하는 질문:** "사내 시스템(DB + API)을 어떻게 확보하고 이해하는가?"

#### 4.1 사내 시스템 git clone으로 확보 (2p)

**키워드:** Docker Compose, FastAPI

- `git clone`으로 인프라 레포 확보 — 독자가 인프라 구축에 시간을 쏟지 않는 이유
- `docker-compose up -d`로 PostgreSQL + FastAPI 한 번에 구동
- `docker-compose ps`로 컨테이너 상태 확인

#### 4.2 데이터베이스 스키마 분석 (2p)

**키워드:** ER 다이어그램, 스키마(Schema)

- `init/01_schema_and_data.sql` 구조: employees, leaves, sales 테이블 DDL
- ER 다이어그램으로 테이블 간 관계 시각화
- 샘플 데이터 내용: 직원 5명, 연차 신청 10건, 매출 기록 20건

#### 4.3 CRUD API 구조 이해 (2p)

**키워드:** FastAPI, Swagger UI, 엔드포인트(Endpoint)

- `app/main.py`, `app/routers/` 구조 설명
- 엔드포인트 목록: `/employees`, `/leaves`, `/sales/summary` 등 10개
- Swagger UI(`localhost:8000/docs`)에서 직접 API 테스트
- curl / PowerShell 명령어로 API 동작 확인

#### 4.4 MCP 개념 소개 (1.5p)

**키워드:** MCP(Model Context Protocol), LangChain Tool

- MCP의 정의: LLM이 외부 도구(DB, API)를 표준 프로토콜로 호출하는 방법
- LangChain Tool과 MCP의 차이 (LangChain Tool은 Python 코드에 종속, MCP는 프로토콜로 분리)
- 이 인프라가 8장 MCP 구현의 대상이 되는 흐름 예고

#### 4.5 정리하며 (0.5p)

- 핵심 요약: Docker Compose로 인프라 구동, 스키마 파악, CRUD API 확인, MCP 개념 기초
- CH05 예고: "인프라가 준비되었습니다. 5장에서 RAG에 입력할 문서를 표준화합니다"

> 예제 코드: `docker-compose.yml`, `init/01_schema_and_data.sql`, `app/main.py`, `app/routers/employees.py`, `app/routers/leaves.py`, `app/routers/sales.py`, `app/models.py`, `app/schemas.py`

---

### CH05. 사내 문서 표준화 (8p)

**이 챕터에서 답하는 질문:** "RAG 품질을 결정하는 문서 기준은 무엇인가?"

#### 5.1 RAG 검색 품질을 결정하는 문서 기준 (1p)

**키워드:** GIGO(Garbage In, Garbage Out), 전처리(Preprocessing)

- "쓰레기가 들어가면 쓰레기가 나온다" — 문서 품질이 RAG 성능을 좌우하는 원리
- 문서 표준화를 별도 챕터로 분리하는 이유

#### 5.2 PDF, Word, Markdown, HWP 수집 전략 (2p)

**키워드:** pdfplumber, python-docx, Vision LLM

- `guides/collection_strategy.md` 기반 문서 유형별 수집 우선순위 매트릭스
- 규칙 기반(pdfplumber, python-docx) vs AI 기반(Vision LLM) 선택 기준
- HWP 처리 방법 (LibreOffice → PDF 변환 후 PDF 파이프라인 위임)

#### 5.3 문서 전처리 및 정규화 가이드라인 (2p)

**키워드:** 정규화(Normalization), Markdown 통일

- `guides/preprocessing_rules.md` 기반 정규화 규칙 표
- 헤더/푸터 제거, 인코딩 통일, 불필요 공백 정리, 표/이미지 처리 방침
- 전처리 전(`data/sample_raw/`) vs 후(`data/sample_clean/`) 비교 예시
- 최종 출력을 Markdown으로 통일하는 이유: 토큰 효율, 구조 보존, LLM 이해도

#### 5.4 사내 문서 네이밍(Naming) 표준 규칙 (1.5p)

**키워드:** 네이밍 표준(Naming Convention), 메타데이터 자동 추출

- `guides/naming_convention.md` 기반: `{부서}_{문서명}_{버전}.확장자` 포맷 강제
- 부서별 폴더(`hr/`, `finance/`, `ops/`) 분리 규칙
- 잘못된 사례(`2025년본.pdf`, `최종수정(진짜최종).xlsx`) vs 올바른 사례 비교
- 네이밍 규칙 → 메타데이터 자동 추출 연결 예고 (6장 `parse_filename_metadata()`)

#### 5.5 메타데이터 스키마 설계 (1p)

**키워드:** 메타데이터(Metadata), ChromaDB 필터

- `data/metadata_schema.json` 기반 스키마 필드 정의 (doc_id, source, department, version, date 등)
- ChromaDB 필터링에 사용할 필드와 그 이유
- 네이밍 규칙 → 메타데이터 자동 파싱 연결 (파일명만으로 `department`, `version` 추출)

#### 5.6 정리하며 (0.5p)

- 표준화 완료 체크리스트 (7가지 항목)
- CH06 예고: "표준화된 문서를 6장에서 벡터 DB에 저장합니다"

> 예제 코드: `guides/collection_strategy.md`, `guides/preprocessing_rules.md`, `guides/naming_convention.md`, `data/metadata_schema.json`, `data/sample_raw/`, `data/sample_clean/`

---

### CH06. 벡터 DB 구축 (14p)

**이 챕터에서 답하는 질문:** "PDF에서 ChromaDB까지 전체 파이프라인을 어떻게 구축하는가?"

#### 6.1 [실습 준비] 데이터 파일 확인 (1p)

**키워드:** 네이밍 규칙, 사내 문서 샘플

- `data/docs/` 폴더 구조 확인: `HR_취업규칙_v1.0.pdf`, `HR_정보보안서약서.pdf`, `OPS_신규서비스_런칭전략.pdf`
- 5장 네이밍 규칙(`{부서}_{문서명}_{버전}.pdf`)이 실제 파일에 적용된 것 재확인
- 전체 파이프라인 흐름 미리보기 (5단계)

#### 6.2 [규칙 기반] PDF 파싱 (2.5p)

**키워드:** pdfplumber, is_complex_layout(), parse_filename_metadata()

- `src/extractor.py` — `extract_text_pdfplumber()` 함수 코드 워크플로우 (IPO)
  - Input: PDF 파일 경로
  - Process: pdfplumber로 페이지별 텍스트·표 추출
  - Output: 페이지 딕셔너리 리스트 (text, has_table, source, page 포함)
- `is_complex_layout()`: 복합 레이아웃 감지 로직 설명
- `parse_filename_metadata()`: 파일명에서 `department`, `doc_name`, `version` 자동 파싱 (5장 → 6장 연결)
- "규칙이 실패할 때" 직접 체감: 다단/복합 레이아웃에서 pdfplumber가 깨지는 순간

#### 6.3 [AI 기반] Vision LLM으로 Markdown 변환 (2.5p)

**키워드:** Vision LLM(LLaVA), pdf_page_to_image(), extract_pdf_to_markdown()

- `src/vision_extractor.py` — `pdf_page_to_image()`, `call_vision_llm()`, `extract_pdf_to_markdown()` 코드 워크플로우
  - Input: PDF 파일 경로, 페이지 번호
  - Process: 페이지 이미지 캡처 → Vision LLM(llava) → Markdown 출력
  - Output: `outputs/markdown/{파일명}.md`
- 규칙 기반 실패 케이스를 AI로 해결하는 흐름
- Vision LLM을 최후 수단으로 사용하는 이유: 비용/속도 ROI 전략

#### 6.4 청킹 전략 (2p)

**키워드:** 청킹(Chunking), Markdown 청킹, Fixed-size 청킹

- `src/chunker.py` — `markdown_chunk()`, `fixed_size_chunk()`, `compare_strategies()` 코드 워크플로우
- Markdown 헤더(`#`) 기준 의미 단위 청킹 vs Fixed-size 청킹 나란히 비교
- 비교 출력: 청크 수, 평균 길이, 섹션 보존 여부
- 청킹 전략 선택 기준 (문서 유형별 권장)

#### 6.5 임베딩 + ChromaDB 저장 (3.5p)

**키워드:** 임베딩(Embedding), nomic-embed-text, PersistentClient

- `src/embedder.py` — `get_embedding_model()`, `embed_texts()`, `embed_single()` 코드 워크플로우
  - Input: 텍스트 리스트, 모델명
  - Process: Ollama REST API로 nomic-embed-text 임베딩 생성
  - Output: 벡터 리스트 (768차원)
- `src/store.py` — `get_client()`, `create_collection()`, `add_documents()`, `search()` 코드 워크플로우
  - PersistentClient: `CHROMA_PERSIST_DIR`에 영속 저장
  - 부서 메타데이터 필터 검색 테스트 (`filter_dept` 파라미터)
- `src/main.py` — `run_pipeline(use_vision=False/True)` 전체 흐름 (`--vision` 플래그)

#### 6.6 정리하며 (2.5p)

- 핵심 요약: PDF → pdfplumber/Vision LLM → 청킹 → nomic-embed-text → ChromaDB PersistentClient
- 구축된 벡터 DB 확인 (컬렉션 통계, 부서별 분포)
- 자주 발생하는 오류와 해결법 (Ollama 미실행, ChromaDB 권한 오류 등)
- CH07 예고: "벡터 DB가 완성되었습니다. 7장에서 RAG Q&A 엔진을 구현합니다"

> 예제 코드: `src/extractor.py`, `src/vision_extractor.py`, `src/chunker.py`, `src/embedder.py`, `src/store.py`, `src/main.py`, `data/docs/`, `.env.example`, `requirements.txt`

---

### CH07. RAG Q&A 엔진 구현 (14p)

**이 챕터에서 답하는 질문:** "RAG Q&A 엔진을 FastAPI 서비스로 어떻게 제공하는가?"

#### 7.1 FastAPI로 RAG 서비스 제공하기 (2p)

**키워드:** FastAPI, uvicorn, 비동기 처리

- `app/main.py` — FastAPI 앱 생성, 라우터 등록, StaticFiles 마운트, 루트 리다이렉트
- `app/routers/ui.py` — 대시보드, Q&A 페이지 HTML 라우터
- FastAPI를 선택하는 이유: 비동기 처리, Swagger UI 자동 제공, uvicorn 기반 실무 표준
- 실행 방법: `uvicorn app.main:app --reload` 및 브라우저 접속

#### 7.2 LLM 서비스 계층 구성 (2.5p)

**키워드:** LLMService, Jinja2 프롬프트 템플릿

- `app/services/llm_service.py` — `LLMService` 클래스 코드 워크플로우
  - Input: 프롬프트 템플릿명, 컨텍스트 변수
  - Process: Jinja2로 `.j2` 파일 렌더링 → ChatOllama / ChatOpenAI 호출
  - Output: LLM 응답 문자열
- `app/prompts/router_prompt.j2` — 인텐트 분류 프롬프트 구조 설명
- `app/prompts/answer_prompt.j2` — 답변 생성 프롬프트 구조 설명
- DeepSeek R1 `<think>` 태그 제거 처리 이유
- LLMService 계층 분리 이유: ollama/openai 전환이 환경변수 1개 변경으로 가능

#### 7.3 벡터 검색 서비스 연결 (2p)

**키워드:** VectorService, similarity_search_with_score()

- `app/services/vector_service.py` — `VectorService` 클래스 코드 워크플로우
  - Input: 검색 쿼리, k값, 부서 필터
  - Process: OllamaEmbeddings(nomic-embed-text)로 쿼리 임베딩 → ChromaDB 유사도 검색
  - Output: 문서 청크 + 유사도 점수 리스트
- CH06 ChromaDB를 그대로 사용하는 이유: 동일 임베딩 모델로 재임베딩 비용 없음
- 싱글톤 패턴으로 서비스 객체 공유하는 이유

#### 7.4 인텐트 라우팅과 RAG Q&A 오케스트레이션 (3p)

**키워드:** 인텐트 라우팅(Intent Routing), QAService

- `app/services/qa_service.py` — `QAService` 클래스 코드 워크플로우
  - Input: 사용자 질문
  - Process: `router_prompt.j2`로 인텐트 분류(unstructured/hybrid) → 검색 전략 선택 → `answer_prompt.j2`로 LLM 답변 생성
  - Output: 답변 텍스트 + 출처(source, score) 리스트
- `app/routers/qa.py` — `POST /admin/qa/query` 엔드포인트 코드 워크플로우
- `hybrid_search()`와 `get_ai_answer()` 연계 흐름

#### 7.5 웹 채팅 인터페이스 구현 (3p)

**키워드:** Jinja2 HTML 템플릿, AJAX, 출처 카드

- `app/templates/` — `base.html`, `dashboard.html`, `qa.html` 구조 설명
- `app/static/js/qa.js` — `sendQuery()` 비동기 AJAX 전송, 출처 카드 렌더링 (source, score)
- `scripts/ingest.py` — PDF → ChromaDB 인제스트 스크립트 실행 방법
- 브라우저에서 `http://127.0.0.1:8000/admin/qa` 접속 후 RAG 동작 확인

#### 7.6 정리하며 (1.5p)

- 핵심 요약: FastAPI 서비스 구조, LLMService + VectorService + QAService 계층, 인텐트 라우팅, Jinja2 프롬프트 템플릿
- 자주 발생하는 오류와 해결법 (모델 미설치, ChromaDB 경로 불일치 등)
- CH08 예고: "7장의 RAG Q&A에 MCP Agent(정형 DB 조회)를 추가합니다"

> 예제 코드: `app/main.py`, `app/routers/ui.py`, `app/routers/qa.py`, `app/services/llm_service.py`, `app/services/vector_service.py`, `app/services/qa_service.py`, `app/prompts/router_prompt.j2`, `app/prompts/answer_prompt.j2`, `app/templates/`, `app/static/js/qa.js`, `scripts/ingest.py`

---

### CH08. 통합 에이전트 설계 (MCP + RAG) (12p)

**이 챕터에서 답하는 질문:** "PostgreSQL DB 조회를 MCP 프로토콜로 노출하고 ReAct 에이전트로 자율 실행하는 방법은?"

#### 8.1 MCP란 무엇인가 (1.5p)

**키워드:** MCP(Model Context Protocol), FastMCP

- MCP의 정의와 등장 배경 (Anthropic 제안 오픈 프로토콜)
- LangChain Tool vs MCP의 차이: Tool은 Python 종속, MCP는 프로토콜로 분리하여 재사용 가능
- FastMCP로 MCP 서버를 빠르게 구현하는 구조 개요

#### 8.2 PostgreSQL 연결과 DB 초기화 (2p)

**키워드:** PostgresConnectionWrapper, SQLAlchemy, init_db.py

- `docker-compose.yml` — PostgreSQL 컨테이너 설정
- `app/database/connection.py` — `PostgresConnectionWrapper` 패턴: psycopg2 연결에 DictCursor와 편의 메서드 추가
- `app/database/init_db.py` — `init_db()` 코드 워크플로우
  - Input: DATABASE_URL 환경 변수
  - Process: 테이블 생성(employees, leaves, sales) + 샘플 데이터 삽입
  - Output: 직원 5명, 연차 신청 10건, 매출 기록 20건
- `app/database/crud.py` — `list_employees()`, `get_leave_by_employee()`, `get_sales_by_dept()` 등 주요 함수

#### 8.3 MCP 서버 구현 (FastMCP) (2.5p)

**키워드:** @mcp.tool() 데코레이터, stdio 모드

- `mcp/mcp_server.py` — FastMCP 서버 전체 구조
- `@mcp.tool()` 데코레이터 패턴: JSON Schema 자동 생성 원리
- 9개 도구 등록 (직원 5개, 휴가 3개, 매출 4개) 코드 워크플로우
  - Input: 자연어 파라미터 (직원명, 부서명, 날짜 범위 등)
  - Process: crud.py 함수 호출
  - Output: 딕셔너리 형태의 조회 결과
- stdio 모드로 실행되는 이유: 서버-클라이언트 격리, 크래시 시 영향 없음

#### 8.4 MCP 에이전트 서비스 구현 (2.5p)

**키워드:** MCPToolWrapper, ReAct 에이전트, AgentExecutor

- `app/services/mcp_agent_service.py` — `MCPAgentService.run_agent()` 코드 워크플로우
  - Input: 사용자 질문 문자열
  - Process: StdioServerParameters로 MCP 서버 서브프로세스 실행 → list_tools로 도구 목록 수집 → MCPToolWrapper(async→sync 변환) → create_react_agent + AgentExecutor ReAct 루프
  - Output: 최종 답변 + 도구 사용 기록(steps)
- MCPToolWrapper가 필요한 이유: MCP는 async 기반, LangChain Tool은 sync 기대 → asyncio.run()으로 브릿지
- ReAct 에이전트를 사용하는 이유: 복수 도구 호출 순서를 LLM이 자율 결정

#### 8.5 FastAPI에 MCP Agent 통합 (2.5p)

**키워드:** POST /admin/qa/agent, agent.html, 아코디언 UI

- `app/routers/qa.py` — `POST /admin/qa/agent` 엔드포인트 추가 (CH07 구조에 탭 추가)
- `app/templates/agent.html` — Agent 채팅 UI 구조
- `app/static/js/agent.js` — `sendAgentQuery()`, 도구 사용 기록(steps) 아코디언 렌더링
- 브라우저에서 `http://127.0.0.1:8000/admin/agent` 접속 후 자연어로 DB 조회 확인

#### 8.6 정리하며 (1p)

- 핵심 요약: FastMCP 서버 + MCPToolWrapper + ReAct Agent + FastAPI 통합
- 대표 질문 10개 시나리오와 올바른 응답 경로
- CH09 예고: "9장에서 모든 구성 요소를 LangChain LCEL로 통합하고 운영 설정을 추가합니다"

> 예제 코드: `mcp/mcp_server.py`, `app/database/connection.py`, `app/database/init_db.py`, `app/database/crud.py`, `app/services/mcp_agent_service.py`, `app/routers/qa.py`, `app/templates/agent.html`, `app/static/js/agent.js`, `docker-compose.yml`

---

### CH09. LangChain 최종 연결 (10p)

**이 챕터에서 답하는 질문:** "모든 구성 요소를 하나의 파이프라인으로 통합하고 운영 가능한 수준으로 만드는 방법은?"

#### 9.1 Router / Agent / RAG Chain / MCP Tool 통합 구성 (2.5p)

**키워드:** LangChain LCEL, AgentExecutor, ReAct 패턴

- `src/agent.py` — AgentExecutor 구성 코드 워크플로우
  - Input: 사용자 질문
  - Process: LCEL 체인(`|` 연산자)으로 Router → Tool 선택 → 실행 → 응답 합성
  - Output: 최종 답변 + 도구 호출 로그
- CH07 ChromaDB RAG Tool + CH08 MCP Tools를 하나의 Agent에 통합하는 구조
- `src/rag_tool.py` — ChromaDB 검색을 LangChain Tool로 래핑

#### 9.2 MCP Tool 설계 (2p)

**키워드:** LangChain Tool, get_leave_balance(), get_sales_sum()

- `src/mcp_tools.py` — `get_leave_balance()`, `get_sales_sum()`, `get_employee_info()` 코드 워크플로우
  - Input: 자연어 파라미터 (직원명, 부서명)
  - Process: CH04 FastAPI REST API 호출 (httpx)
  - Output: 조회 결과 문자열
- LangChain Tool 규격으로 구현하는 이유: Agent가 자동으로 적절한 Tool을 선택하고 호출 가능

#### 9.3 운영 설정 (Timeout, Retry, 로깅, 캐싱) (2.5p)

**키워드:** SQLiteCache, LangChain Cache, 타임아웃

- `src/config.py` — timeout, retry, logging, cache 설정 코드 워크플로우
  - SQLiteCache 초기화: `langchain_cache.db`에 동일 입력 결과 저장
  - Retry: 로컬 LLM 응답 시간 가변성 대응
  - logging: 도구 호출 기록, 응답 시간 측정
- Timeout/Retry가 필요한 이유: 로컬 LLM 응답 시간 가변, DB 연결 일시 실패 가능

#### 9.4 비용 관리 및 토큰 모니터링 (2p)

**키워드:** MetricsCollector, 캐시 히트율

- `src/monitor.py` — `MetricsCollector` 코드 워크플로우
  - 응답 시간 측정, 도구 호출 횟수 집계, 캐시 히트율 계산
  - 세션 종료 시 통계 요약 출력
- `src/main.py` — 대화 루프 진입점: 질문 입력 → AgentExecutor 실행 → 메트릭 출력 → 다음 질문
- 로컬 LLM에서도 토큰 모니터링이 필요한 이유: GPU 메모리와 처리 시간은 유한

#### 9.5 정리하며 (1p)

- 핵심 요약: LCEL 통합, LangChain Tool 표준화, SQLiteCache, MetricsCollector
- 전체 파이프라인 완성 확인 (단일 CLI 인터페이스에서 RAG + MCP 통합 동작)
- CH10 예고: "파이프라인이 완성되었습니다. 10장에서 성능을 측정하고 튜닝합니다"

> 예제 코드: `src/main.py`, `src/agent.py`, `src/rag_tool.py`, `src/mcp_tools.py`, `src/config.py`, `src/monitor.py`, `.env.example`, `requirements.txt`

---

### CH10. RAG 시스템 튜닝 (12p)

**이 챕터에서 답하는 질문:** "RAG 시스템의 성능 문제를 어떻게 진단하고 개선하는가?"

#### 10.1 증상별 튜닝 가이드 (2p)

**키워드:** 증상별 진단, Retrieval Accuracy, Hallucination Rate

- 증상-원인-해결 매트릭스 (환각, 근거 부족, 엉뚱한 문서 반환, 응답 느림 등)
- "RAG 성능이 안 좋다"는 막연한 진단이 아니라 구체적 증상에서 출발하는 방법
- 각 증상별 체크 포인트와 빠른 대응 방법

#### 10.2 Chunk / Retriever 튜닝 (2.5p)

**키워드:** Semantic Chunk, k값 조정, Metadata Filtering

- `src/tuning/chunker_tuning.py` 코드 워크플로우
  - Input: 문서 텍스트, 청크 크기 / k값 범위
  - Process: 조합별 검색 정확도 측정
  - Output: 청크 크기 / k값별 정확도 비교 표
- Semantic Chunk 구현: 의미 경계 기반 동적 분할
- k값 조정과 Metadata Filtering(부서별, 날짜별) 적용

#### 10.3 고급 기술 (ReRanker, Hybrid Search) (2.5p)

**키워드:** ReRanker, Hybrid Search(BM25 + 벡터), Parent Document Retriever

- `src/tuning/reranker.py` — CrossEncoder ReRanker 코드 워크플로우
  - Input: 1차 검색 결과 (k=10)
  - Process: CrossEncoder로 재순위화
  - Output: 재순위 top-3 반환
- Hybrid Search: 키워드 검색(BM25)과 벡터 유사도 결합 방법 및 약점 보완 효과
- Parent Document Retriever: 작은 청크로 검색하되 반환 시 상위 문서 포함하는 전략

#### 10.4 프롬프트 튜닝 (1.5p)

**키워드:** 근거 우선 응답, "모르면 모른다" 전략

- `src/tuning/prompts.py` — 시스템 프롬프트 변형 3가지 비교 코드 워크플로우
- 근거 우선 응답 전략, "모르면 모른다" 전략, 시스템 프롬프트 최적화 포인트
- 프롬프트 변형이 Hallucination Rate에 미치는 영향 수치 비교

#### 10.5 PDF 이미지 처리 (LLaVA + EasyOCR 하이브리드) (2p)

**키워드:** EasyOCR, LLaVA, 하이브리드 OCR

- `src/ocr_hybrid.py` — 하이브리드 OCR 코드 워크플로우
  - Input: 스캔 PDF 파일 경로
  - Process: 이미지 내 텍스트는 EasyOCR, 이미지 내용 설명은 LLaVA(Vision LLM)로 분담
  - Output: 추출된 텍스트 + 이미지 설명 통합 결과
- LLaVA + EasyOCR 하이브리드의 이유: 텍스트 추출과 이미지 이해의 역할 분담

#### 10.6 평가 체계 구축 (1.5p)

**키워드:** 테스트셋, Retrieval Accuracy, Hallucination Rate

- `src/evaluator.py` — `data/testset.json` 기반 30개 테스트 케이스 평가 코드 워크플로우
  - Input: 테스트 질문 + 정답 쌍 30개
  - Process: RAG 파이프라인 실행 → 검색 문서 일치율 계산 → 응답 정확도 판정
  - Output: Retrieval Accuracy, Answer Accuracy, Hallucination Rate 리포트
- `src/main.py` — `--mode tune / eval / ocr` 플래그별 실행 방법

#### 10.7 정리하며 (0.5p)

- 핵심 요약: 증상별 튜닝 매트릭스, ReRanker + Hybrid Search, 프롬프트 튜닝, LLaVA + EasyOCR, 정량 평가 체계
- 전체 프로젝트 회고: CH01의 최종 시나리오를 CH10에서 완성하기까지의 여정
- 향후 확장 방향: Graph RAG, 멀티에이전트 오케스트레이션, 클라우드 배포, 실시간 문서 동기화

> 예제 코드: `src/main.py`, `src/tuning/chunker_tuning.py`, `src/tuning/reranker.py`, `src/tuning/prompts.py`, `src/ocr_hybrid.py`, `src/evaluator.py`, `data/testset.json`

---

## 챕터 간 의존성 요약

```
CH01 (아키텍처 이해)
  ↓
CH02 (개발 환경: Ollama + PostgreSQL + venv + .env)
  ↓
CH03 (LLM 한계 체험: 01~04_*.py — 인메모리 ChromaDB)
  ↓
CH04 (베이스 시스템: Docker Compose + FastAPI CRUD)
  ↓
CH05 (문서 표준화: 가이드라인 + 메타데이터 스키마)
  ↓
CH06 (벡터 DB: extractor → chunker → embedder → store)
  ↓
CH07 (RAG Q&A: FastAPI + LLMService + VectorService + QAService)
  ↓                ↖ CH04 MCP 개념
CH08 (통합 에이전트: FastMCP + MCPToolWrapper + ReAct Agent)
  ↓
CH09 (LangChain 통합: AgentExecutor + LCEL + SQLiteCache + MetricsCollector)
  ↓
CH10 (튜닝: ReRanker + Hybrid Search + 프롬프트 최적화 + 정량 평가)
```

## 예제 파일 매핑 전체 요약

| CH | 주요 파일 | 실행 명령 |
|----|---------|---------|
| CH02 | `src/verify_env.py` | `python src/verify_env.py` |
| CH03 | `01_llm_only.py`, `02_context_injection.py`, `03_rag_preview.py`, `04_rag_reasoning.py` | `python 01_llm_only.py` 등 |
| CH04 | `docker-compose.yml`, `app/main.py`, `init/01_schema_and_data.sql` | `docker-compose up -d` |
| CH05 | `guides/*.md`, `data/metadata_schema.json` | (가이드 문서 참조) |
| CH06 | `src/main.py` | `python src/main.py` / `python src/main.py --vision` |
| CH07 | `app/main.py`, `scripts/ingest.py` | `uvicorn app.main:app --reload` |
| CH08 | `mcp/mcp_server.py`, `app/main.py` | `python -m app.main` |
| CH09 | `src/main.py` | `PYTHONPATH=. python src/main.py` |
| CH10 | `src/main.py` | `python src/main.py --mode eval` 등 |

---

# 1. 이 책의 목표와 최종 완성본 미리보기

이 장에서는 이 책이 만드는 결과물과 그 설계 원칙을 학습합니다. 어떤 시스템을 구축하는지, 왜 그 방식을 선택했는지를 먼저 확인하여 이후 실습의 방향을 잡습니다.

<!-- [IMAGE PLACEHOLDER: 01_system-overview — AI 업무 비서 시스템의 전체 구성요소와 데이터 흐름을 한눈에 보여주는 개요도] -->
*그림 1-1: AI 업무 비서 시스템 전체 구성 개요*

---

## 1. 이 책이 만드는 것

이 책은 **AI 업무 비서(AI Work Assistant)** 를 로컬 환경에서 처음부터 끝까지 구축하는 과정을 안내합니다. 사내 문서(PDF)와 정형 데이터베이스(PostgreSQL)를 LLM과 연결하여, 자연어 질문에 출처가 포함된 답변을 반환하는 시스템입니다.

### Fine-tuning이 아닌 RAG를 선택하는 이유

LLM에 사내 지식을 주입하는 방법은 크게 두 가지입니다. **파인튜닝(Fine-tuning)** 은 모델 가중치를 직접 학습시키는 방법이고, **검색 증강 생성(RAG, Retrieval-Augmented Generation)** 은 기존 모델에 외부 지식을 실시간으로 주입하는 방법입니다.

파인튜닝은 강력하지만 비용과 복잡도가 높습니다. 사내 규정이 업데이트될 때마다 모델을 다시 학습시켜야 하고, 학습 데이터 준비부터 GPU 자원 확보까지 진입 장벽이 높습니다. 반면 RAG는 문서를 벡터 데이터베이스에 저장해 두고 질문이 들어올 때마다 관련 문서를 검색하여 LLM에 전달합니다. 문서가 바뀌면 벡터 DB를 업데이트하면 되므로, 유지 보수 비용이 훨씬 낮습니다.

> **참고: 이 책의 대상 시나리오**
> 이 책은 "사내 문서(PDF)와 DB에 LLM을 연결하고 싶지만, 모델 재학습까지는 하지 않겠다"는 실무 요구에 최적화된 접근 방식을 다룹니다.

### 외부 클라우드 API 없이 로컬 LLM으로 구성하는 이유

이 책의 모든 실습은 **Ollama + DeepSeek R1** 조합으로 동작합니다. OpenAI API나 Anthropic API 키가 전혀 필요하지 않습니다.

로컬 LLM을 선택하는 이유는 세 가지입니다.

1. **사내 데이터 보안**: 인사 규정, 매출 데이터 등 민감한 정보가 외부 서버로 전송되지 않습니다.
2. **API 비용 제거**: 질의 횟수에 관계없이 추가 비용이 발생하지 않습니다.
3. **네트워크 독립성**: 인터넷 연결이 불안정한 환경에서도 동작합니다.

> **주의: 하드웨어 요구사항**
> DeepSeek R1(7B 파라미터) 기준으로 최소 16GB RAM이 필요합니다. RAM이 부족한 경우 더 작은 모델(예: deepseek-r1:1.5b)로 실습할 수 있으나 응답 품질이 낮아집니다.

---

## 2. 시나리오로 보는 AI 업무 비서

완성된 시스템이 어떻게 동작하는지 구체적인 사용 시나리오로 먼저 확인합니다.

### 복합 질의 시나리오

인사팀 직원이 다음 질문을 AI 업무 비서에 입력합니다.

> "김철수 씨의 남은 연차가 며칠이고, 연차 사용 기준은 어떻게 되나요?"

이 질문에는 두 가지 성격이 서로 다른 정보 요구가 섞여 있습니다.

- **"남은 연차가 며칠인가"** → 데이터베이스에서 조회해야 하는 **정형(Structured)** 데이터
- **"연차 사용 기준은 어떻게 되나"** → 사내 규정 문서에서 검색해야 하는 **비정형(Unstructured)** 데이터

이 두 가지를 하나의 시스템이 처리하여 단일 답변으로 합성합니다.

### 단계별 처리 흐름

| 단계 | 동작 | 구성 요소 |
|------|------|---------|
| ① 질문 입력 | 사용자가 복합 질문을 입력 | CLI / Web UI |
| ② 질문 라우팅 | "연차 잔여일" → 정형(DB), "연차 사용 기준" → 비정형(문서)으로 분류 | 질문 라우터 |
| ③-A MCP Tool 호출 | PostgreSQL에서 김철수의 잔여 연차를 조회 | MCP Tool + PostgreSQL |
| ③-B RAG Chain 호출 | "연차 사용 기준"으로 사내 규정 문서를 벡터 검색 | ChromaDB + 임베딩 모델 |
| ④ LLM 응답 합성 | DB 결과 + 문서 청크를 컨텍스트로 DeepSeek R1이 자연어 답변 생성 | Ollama (DeepSeek R1) |
| ⑤ 최종 답변 출력 | 출처 문서명이 포함된 답변을 반환 | FastAPI 응답 |

단계 ③-A와 ③-B는 병렬로 실행됩니다. **질문 라우터(Question Router)** 가 질문을 분석하여 정형·비정형 두 경로로 동시에 요청을 보내고, 두 결과가 모이면 LLM이 최종 답변을 합성합니다.

### 최종 답변 예시

```
김철수 씨의 남은 연차는 5일입니다.

연차 사용 기준 (사내 취업규칙 v1.0, 3조 2항):
- 연차는 최소 1일 단위로 사용 가능합니다.
- 3일 이상 연속 사용 시 팀장 사전 승인이 필요합니다.
- 미사용 연차는 다음 해 3월 31일까지 이월됩니다.

[출처: HR_취업규칙_v1.0.pdf, 3페이지]
```

출처가 명시되기 때문에 담당자가 원문을 직접 확인할 수 있습니다. 이것이 RAG 방식의 핵심 장점입니다. LLM이 생성한 내용이 어느 문서 어느 페이지에 근거하는지 추적이 가능합니다.

---

## 3. 전체 아키텍처 한 장 요약

아래 다이어그램은 이 책에서 구축하는 전체 시스템의 구성도입니다. 10개 챕터를 거쳐 완성할 시스템의 최종 모습을 미리 확인하십시오.

```mermaid
flowchart TB
    U(["사용자 질문"])
    U -- "1. 입력" --> R["질문 라우터 (LangChain)"]

    R -- "정형: 연차 잔여일" --> M["MCP Tool"]
    R -- "비정형: 연차 사용 기준" --> V["RAG Chain"]

    M -- "SQL 조회" --> PG[("PostgreSQL\n연차 DB")]
    V -- "유사도 검색" --> CR[("ChromaDB\n사내 문서")]

    PG -- "DB 결과" --> S["LLM 응답 합성 (DeepSeek R1)"]
    CR -- "문서 청크" --> S

    S -- "최종 답변 + 출처" --> U
```

*그림 1-2: AI 업무 비서 전체 아키텍처 다이어그램*

각 구성 요소의 역할을 정리합니다.

| 구성 요소 | 역할 |
|---------|------|
| **질문 라우터** | 사용자 질문을 분석하여 MCP Tool(정형)과 RAG Chain(비정형) 중 적절한 경로로 분기 |
| **MCP Tool** | LLM이 PostgreSQL DB를 표준 프로토콜로 호출하는 도구 |
| **RAG Chain** | 사내 문서를 벡터 DB에서 검색하여 LLM에 컨텍스트를 제공하는 체인 |
| **PostgreSQL** | 직원 정보, 연차 신청, 매출 기록 등 정형 데이터를 저장하는 관계형 DB |
| **ChromaDB** | 사내 문서(PDF)를 벡터로 변환하여 저장하는 벡터 데이터베이스 |
| **DeepSeek R1** | DB 결과와 문서 청크를 받아 자연어 답변을 생성하는 로컬 LLM |

---

## 4. 사용 기술 스택 상세

이 책에서 사용하는 모든 기술은 무료이며 로컬에서 동작합니다.

| 역할 | 기술 | 버전 | 선택 이유 |
|------|------|------|---------|
| 프로그래밍 언어 | Python | 3.11 | LangChain, ChromaDB 공식 지원 버전 |
| LLM 추론 런타임 | Ollama | 0.5+ | macOS/Linux/WSL2 네이티브, 모델 관리 단순 |
| 언어 모델 | DeepSeek R1 | latest | 오픈 웨이트, 추론 능력 우수, 무료 |
| 파이프라인 프레임워크 | LangChain | 0.3+ | LCEL 체인 문법, RAG/Agent 표준 |
| 벡터 데이터베이스 | ChromaDB | 0.5+ | 로컬 영속 모드 지원, Python 네이티브 |
| 관계형 데이터베이스 | PostgreSQL | 16 | 실무 표준, Docker Compose로 즉시 구동 |
| API 서버 | FastAPI | 0.110+ | 비동기 처리, Swagger UI 자동 제공 |
| 컨테이너 | Docker / Docker Compose | Docker 24+, Compose v2 | 환경 격리, 재현성 보장 |
| PDF 파싱 | pdfplumber | 최신 | 표·이미지가 없는 일반 PDF 처리 |
| Vision LLM | LLaVA | latest | 복합 레이아웃 PDF를 이미지로 처리 |
| MCP 서버 | FastMCP | 최신 | MCP 프로토콜을 Python으로 빠르게 구현 |

> **팁: LLM Provider 스위칭**
> 이 책의 모든 예제는 `.env` 파일의 `LLM_PROVIDER` 값 하나로 Ollama(로컬)와 OpenAI(클라우드) 간에 전환할 수 있도록 설계되었습니다. 로컬 환경 구성이 어려운 경우 OpenAI API 키를 발급받아 실습을 진행할 수 있습니다.

### MCP를 도입하는 이유

**MCP(Model Context Protocol)** 는 Anthropic이 제안한 오픈 프로토콜로, LLM이 외부 도구(DB, API 등)를 표준화된 방식으로 호출할 수 있게 합니다. 기존 LangChain Tool은 Python 코드에 종속되어 재사용이 어렵지만, MCP는 도구를 프로토콜 수준으로 분리하여 LLM 프레임워크에 관계없이 재사용할 수 있습니다.

이 책에서는 PostgreSQL DB 조회 기능을 MCP Tool로 구현합니다. 정형 데이터(DB)와 비정형 데이터(문서) 두 가지를 단일 에이전트에서 통합 질의하는 것이 이 아키텍처의 핵심입니다.

<!-- [IMAGE PLACEHOLDER: 01_mcp-vs-langchain — LangChain Tool(Python 종속)과 MCP Tool(프로토콜 분리) 방식의 차이를 비교하는 개념도] -->
*그림 1-3: LangChain Tool과 MCP Tool의 구조 비교*

---

## 5. 이 책을 마치면 할 수 있는 것

10개 챕터를 완료하면 다음 역량을 갖추게 됩니다.

1. **RAG 파이프라인 구축**: PDF를 파싱하고, 청킹하고, 임베딩하여 ChromaDB에 저장하는 전체 파이프라인을 직접 구현할 수 있습니다.
2. **로컬 LLM 연동**: Ollama를 활용하여 외부 API 없이 DeepSeek R1 모델을 코드에 연결할 수 있습니다.
3. **MCP 서버 구현**: FastMCP로 PostgreSQL DB를 MCP Tool로 노출하고, LLM 에이전트가 자율적으로 DB를 조회하도록 설계할 수 있습니다.
4. **인텐트 라우팅 설계**: 사용자 질문을 분석하여 정형·비정형 데이터 경로로 분기하는 라우터를 설계할 수 있습니다.
5. **RAG 성능 튜닝**: 청킹 전략 조정, ReRanker 적용, 프롬프트 최적화로 RAG 정확도를 개선하고, 테스트셋을 통해 수치로 측정할 수 있습니다.

### 확장 가능성

이 책에서 구축한 시스템은 출발점입니다. 기반이 완성된 후에는 다음과 같이 확장할 수 있습니다.

- **Graph RAG**: 문서 간 관계를 그래프로 모델링하여 복잡한 추론 질문에 대응
- **멀티에이전트 오케스트레이션**: 여러 전문 에이전트가 협력하는 구조로 발전
- **클라우드 배포**: Docker 이미지를 AWS/GCP에 배포하여 팀 전체가 사용하는 서비스로 전환
- **실시간 문서 동기화**: 사내 문서 업데이트 시 자동으로 벡터 DB를 갱신하는 파이프라인 구축

---

## 6. 정리하며

- **RAG를 선택하는 이유**: 파인튜닝 없이 기존 모델에 외부 지식을 실시간 주입하여, 문서 업데이트 비용과 모델 재학습 복잡도를 모두 낮춥니다.
- **로컬 LLM을 선택하는 이유**: 사내 민감 데이터가 외부로 전송되지 않으며, API 비용 없이 네트워크 독립적으로 운영할 수 있습니다.
- **MCP를 도입하는 이유**: 정형 DB 조회와 비정형 문서 검색을 하나의 에이전트에서 표준 프로토콜로 통합하여 복합 질의에 대응합니다.
- **전체 아키텍처**: 질문 라우터 → MCP Tool(PostgreSQL) + RAG Chain(ChromaDB) → LLM 응답 합성의 흐름으로 동작합니다.
- **이 책의 결과물**: 출처가 포함된 자연어 답변을 반환하는 AI 업무 비서를 로컬 환경에서 완성합니다.

---

1장에서 우리가 만들 시스템의 전체 그림을 확인했습니다. 이제 이 시스템을 직접 구축하기 위한 준비 단계로, 2장에서는 Ollama, PostgreSQL, Python 가상환경을 세팅합니다.



---

# 2. 개발 환경 구축

이 장에서는 이 책의 모든 실습을 실행하기 위한 개발 환경을 구축합니다. **Ollama** 설치, **PostgreSQL** 컨테이너 구동, **Python 3.11** 가상환경 설정, 환경 변수 구성이라는 네 가지 과정을 순서대로 진행합니다. 이 장을 마치면 `src/verify_env.py` 스크립트 하나로 전체 환경의 정상 동작을 일괄 확인할 수 있습니다.

<!-- [IMAGE PLACEHOLDER: 02_env-overview — Ollama, PostgreSQL, Python venv, .env 네 가지 구성 요소가 화살표로 연결된 개발 환경 전체 구성도] -->
*그림 2-1: 2장에서 구축하는 개발 환경 전체 구성*

---

## 1. Ollama 설치 및 DeepSeek R1 모델 다운로드

### Ollama란 무엇인가

**Ollama** 는 로컬 컴퓨터에서 대형 언어 모델(LLM)을 실행하는 경량 런타임입니다. 클라우드 API 없이, 인터넷 연결 없이 LLM을 구동할 수 있어 비용과 보안 측면에서 유리합니다. 도커(Docker)가 컨테이너 이미지를 내려받아 실행하듯, Ollama는 LLM 모델 파일을 내려받아 로컬 서버로 제공합니다.

이 책은 Ollama 위에서 **DeepSeek R1** 모델을 실행합니다. DeepSeek R1은 추론 능력이 뛰어난 오픈소스 모델로, 사내 문서 기반 질의응답에 적합합니다.

### OS별 설치 방법

**macOS**

```bash
# Homebrew를 사용하는 경우
brew install ollama

# 또는 공식 설치 스크립트 사용
curl -fsSL https://ollama.com/install.sh | sh
```

**Ubuntu 22.04+**

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows (WSL2)**

Windows 환경에서는 반드시 WSL2(Windows Subsystem for Linux 2) 내부에서 설치합니다. Windows 네이티브 환경은 지원하지 않습니다.

```bash
# WSL2 터미널에서 실행
curl -fsSL https://ollama.com/install.sh | sh
```

> **팁: Ollama 설치 확인**
> 설치 후 아래 명령으로 버전을 확인하십시오.
> ```bash
> ollama --version
> ```
> `ollama version 0.5.x` 형태의 출력이 나오면 정상 설치된 것입니다.

### 모델 다운로드

Ollama 설치가 완료되면 이 책에서 사용할 두 개의 모델을 내려받습니다.

```bash
# 대화·추론용 LLM (약 4.7GB, 8B 기본 모델)
ollama pull deepseek-r1

# 문서 임베딩용 모델 (약 274MB)
ollama pull nomic-embed-text
```

> **주의: RAM 부족 환경 대응**
> 16GB 미만의 RAM 환경에서는 전체 크기 모델이 매우 느리게 동작합니다.
> 이 경우 더 작은 모델을 사용하십시오.
> ```bash
> ollama pull deepseek-r1:7b
> ```
> `.env` 파일의 `OLLAMA_MODEL=deepseek-r1:7b` 로 변경하면 됩니다.

### 동작 확인

모델 다운로드가 완료되면 간단한 질문으로 동작을 확인합니다.

```bash
ollama run deepseek-r1
```

터미널에 `>>>` 프롬프트가 나타나면 간단한 질문을 입력합니다.

```
>>> 안녕하세요, 자기소개를 해주세요.
```

모델이 응답하면 정상 동작하는 것입니다. `Ctrl + D` 또는 `/bye`를 입력하여 종료합니다.

<!-- [CAPTURE NEEDED: 02_ollama-run — `ollama run deepseek-r1` 실행 후 터미널에서 모델이 응답하는 화면] -->
*그림 2-2: Ollama 모델 실행 및 응답 확인 화면*

---

## 2. PostgreSQL 설치 및 초기 설정

### Docker Compose를 사용하는 이유

PostgreSQL을 컴퓨터에 직접 설치하지 않고 **Docker Compose** 로 구동하는 이유는 세 가지입니다.

1. **환경 격리**: PostgreSQL이 운영 체제 레벨에 설치되지 않아 다른 프로젝트와 충돌하지 않습니다.
2. **재현성**: `docker-compose.yml` 파일 하나로 어떤 환경에서도 동일한 데이터베이스를 재현합니다.
3. **초기화 용이**: 컨테이너를 삭제하고 재생성하면 깨끗한 상태로 돌아갑니다.

### docker-compose.yml 구조 이해

이 책의 `docker-compose.yml`은 **PostgreSQL 16** 컨테이너와 선택사항인 **pgAdmin** 관리 도구를 정의합니다. 핵심 부분을 발췌하여 살펴보겠습니다.

```yaml
# docker-compose.yml (핵심 부분 발췌)
version: "3.9"

services:
  postgres:
    image: postgres:16
    container_name: rag_postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-company_db}
      POSTGRES_USER: ${POSTGRES_USER:-admin}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-changeme}
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-admin} -d ${POSTGRES_DB:-company_db}"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
    driver: local
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: `.env` 파일의 `POSTGRES_*` 환경 변수 (없으면 `:-` 뒤의 기본값 사용)
2. **처리(Process)**: `postgres:16` 이미지를 내려받아 컨테이너를 생성하고, `init/` 폴더의 SQL 스크립트를 최초 실행 시 자동으로 실행
3. **출력(Output)**: 포트 5432에서 접속 가능한 PostgreSQL 서버, `postgres_data` 볼륨에 데이터 영속 저장

각 설정의 의미를 살펴보겠습니다.

- `${POSTGRES_DB:-company_db}`: 환경 변수가 없으면 `company_db`를 기본값으로 사용합니다. 이 책에서는 `.env` 파일에서 값을 주입합니다.
- `./init:/docker-entrypoint-initdb.d`: 로컬의 `init/` 폴더를 컨테이너 안의 초기화 디렉토리에 마운트합니다. 이 폴더의 SQL 파일은 컨테이너 최초 생성 시 자동으로 실행됩니다.
- `healthcheck`: 컨테이너가 준비 완료 상태인지 주기적으로 확인합니다. 준비가 되기 전에 다른 서비스가 접속을 시도하면 실패하는 문제를 예방합니다.

> **참고: pgAdmin 관리 도구**
> `docker-compose.yml`에는 웹 기반 DB 관리 도구인 pgAdmin도 포함되어 있습니다.
> 컨테이너 구동 후 브라우저에서 `http://localhost:5050` 으로 접속하면 SQL을 GUI로 실행할 수 있습니다.
> pgAdmin이 필요 없다면 `docker-compose.yml`의 `pgadmin:` 서비스 블록 전체를 주석 처리하십시오.

### PostgreSQL 컨테이너 구동

```bash
# 백그라운드 모드로 컨테이너 시작
docker-compose up -d

# 컨테이너 상태 확인
docker-compose ps
```

정상 구동 시 아래와 같은 출력이 나타납니다.

```
NAME            IMAGE            STATUS
rag_postgres    postgres:16      Up (healthy)
rag_pgadmin     pgadmin4:latest  Up
```

`STATUS`가 `Up (healthy)`이면 데이터베이스가 정상적으로 준비된 것입니다. `Up (health: starting)`으로 표시되면 잠시 기다린 뒤 다시 확인하십시오.

> **주의: Docker Desktop이 실행 중인지 확인하십시오**
> `docker-compose up -d` 명령 실행 전 Docker Desktop 앱이 실행 중이어야 합니다.
> `Error: Cannot connect to the Docker daemon` 오류가 발생하면 Docker Desktop을 먼저 시작하십시오.

---

## 3. Python 3.11 가상환경 및 패키지 설치

### 가상환경이 필요한 이유

Python **가상환경(venv)** 은 프로젝트별로 독립된 패키지 공간을 만드는 도구입니다. 서로 다른 프로젝트가 같은 패키지의 다른 버전을 요구할 때 충돌 없이 관리할 수 있습니다. 이 책은 Python 3.11과 고정된 패키지 버전을 사용하므로 가상환경을 반드시 사용해야 합니다.

```mermaid
flowchart LR
    A["Python 3.11"] -- "가상환경 생성" --> B["venv"]
    B -- "패키지 설치" --> C["LangChain 0.3"]
    B -- "패키지 설치" --> D["ChromaDB 0.6"]
    B -- "패키지 설치" --> E["psycopg2-binary"]
    G[".env"] -- "설정 로딩" --> B
```

*그림 2-3: Python 가상환경과 패키지 의존성 구조*

### Python 버전 확인

```bash
python --version
# 또는
python3 --version
```

`Python 3.11.x`이 출력되어야 합니다. Python 3.11이 설치되어 있지 않다면 [python.org](https://www.python.org/downloads/)에서 내려받으십시오.

> **팁: macOS에서 pyenv 사용**
> macOS 시스템에 설치된 Python은 버전이 낮을 수 있습니다.
> `pyenv`를 사용하면 여러 Python 버전을 손쉽게 전환할 수 있습니다.
> ```bash
> brew install pyenv
> pyenv install 3.11.9
> pyenv local 3.11.9
> ```

### 가상환경 생성 및 활성화

```bash
# 프로젝트 루트에서 실행합니다.
python -m venv venv

# 활성화 (macOS / Linux)
source venv/bin/activate

# 활성화 (Windows WSL2)
source venv/bin/activate

# 활성화 (Windows 네이티브 — WSL2 사용 권장)
venv\Scripts\activate
```

활성화 후 터미널 프롬프트 앞에 `(venv)`가 표시됩니다. 이후 모든 pip 명령은 이 가상환경 안에서 실행됩니다.

### requirements.txt 기반 패키지 설치

이 책의 `requirements.txt`는 전체 챕터에서 사용하는 패키지를 한 번에 설치하도록 통합 관리합니다. 챕터마다 별도로 설치할 필요가 없습니다.

```bash
pip install -r requirements.txt
```

`requirements.txt`의 핵심 패키지를 살펴보겠습니다.

```text
# requirements.txt (핵심 패키지 발췌)

# 환경 변수 로딩
python-dotenv==1.0.1

# LangChain 파이프라인
langchain==0.3.19
langchain-community==0.3.18
langchain-ollama==0.2.3

# 벡터 데이터베이스
chromadb==0.6.3

# 관계형 DB 연동
psycopg2-binary==2.9.11
sqlalchemy==2.0.38

# HTTP 클라이언트
httpx==0.28.1

# API 서버
fastapi==0.115.8
uvicorn[standard]==0.34.0
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: `requirements.txt` 파일의 패키지 목록 (버전 고정)
2. **처리(Process)**: `pip`가 PyPI에서 각 패키지와 의존성을 내려받아 현재 가상환경에 설치
3. **출력(Output)**: 가상환경의 `site-packages`에 설치된 패키지들, 이후 `import` 구문으로 사용 가능

> **주의: 버전을 임의로 변경하지 마십시오**
> `requirements.txt`의 버전은 챕터 전체의 호환성을 검증한 값입니다.
> 임의로 버전을 올리거나 내리면 예기치 않은 오류가 발생할 수 있습니다.

### 설치 확인

패키지 설치가 완료되면 주요 패키지를 임포트하여 확인합니다.

```bash
python -c "import langchain; import chromadb; import psycopg2; print('패키지 임포트 성공')"
```

`패키지 임포트 성공`이 출력되면 정상적으로 설치된 것입니다.

---

## 4. 환경 변수(.env) 구성 및 LLM Provider 스위칭 설계

### .env 파일로 설정을 분리하는 이유

코드 안에 비밀번호나 서버 주소를 직접 작성하는 것은 위험한 관행입니다. 실수로 코드를 공개 저장소에 올리면 비밀번호가 노출됩니다. **`.env` 파일** 은 이러한 설정을 코드 바깥에 분리하여 관리하는 방법입니다.

이 책은 아래 두 가지 이유에서 `.env` 방식을 채택합니다.

- **보안**: 비밀번호와 API 키를 코드에 하드코딩하지 않습니다. `.env`는 `.gitignore`에 등록되어 Git에 커밋되지 않습니다.
- **유연성**: 개발 환경과 운영 환경에서 서로 다른 설정을 사용할 때 코드를 수정하지 않고 `.env`만 교체합니다.

### .env.example 복사 및 설정

먼저 템플릿을 복사합니다.

```bash
cp .env.example .env
```

그런 다음 `.env` 파일을 편집기로 열어 내용을 확인합니다.

```bash
# .env.example 전체 내용
# AI 업무 비서 구축: RAG + MCP 실전 가이드

# LLM Provider 설정 (현재 지원: ollama)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=deepseek-r1
OLLAMA_VISION_MODEL=llava

# PostgreSQL 설정
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=company_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=changeme

# ChromaDB 설정 (6장부터 사용)
CHROMA_PERSIST_DIR=./chroma_data
CHROMA_COLLECTION=company_docs

# FastAPI CRUD 서버 (4장부터 사용)
CRUD_API_BASE_URL=http://localhost:8000
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: `.env.example` 파일
2. **처리(Process)**: `cp` 명령으로 `.env`로 복사 후, 필요한 값(주로 `POSTGRES_PASSWORD`) 수정
3. **출력(Output)**: 프로젝트 루트에 `.env` 파일 생성, 이후 `python-dotenv`가 읽어 환경 변수로 적재

대부분의 기본값을 그대로 사용해도 무방합니다. 실제 운영 환경이라면 `POSTGRES_PASSWORD`를 강력한 값으로 변경하십시오.

### config.py — 환경 변수 로딩 및 LLM Provider 스위칭 설계

`src/config.py`는 `.env` 파일을 읽어 설정 값을 모듈 상수로 제공합니다. 이 파일의 핵심 설계를 살펴보겠습니다.

```python
# src/config.py (핵심 부분 발췌)
from pathlib import Path
from dotenv import load_dotenv
import os

# .env 파일 자동 로딩
_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=_env_path, override=False)

# LLM Provider 설정
LLM_PROVIDER: str = _get_env("LLM_PROVIDER", "ollama")
OLLAMA_BASE_URL: str = _get_env("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL: str = _get_env("OLLAMA_MODEL", "deepseek-r1")

def get_llm_config() -> dict:
    """현재 LLM_PROVIDER 값에 따른 LLM 설정 딕셔너리를 반환합니다."""

    # --- Input ---
    provider = LLM_PROVIDER.lower()

    # --- Process ---
    if provider == "ollama":
        config = {
            "provider": "ollama",
            "model": OLLAMA_MODEL,
            "base_url": OLLAMA_BASE_URL,
        }
    else:
        print(f"[오류] 지원하지 않는 LLM_PROVIDER 값입니다: '{LLM_PROVIDER}'")
        sys.exit(1)

    # --- Output ---
    return config
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: `.env` 파일의 `LLM_PROVIDER`, `OLLAMA_*` 환경 변수
2. **처리(Process)**: `LLM_PROVIDER` 값을 확인하여 현재 지원하는 `ollama`에 대한 설정 딕셔너리를 구성
3. **출력(Output)**: `{"provider": "ollama", "model": "deepseek-r1", "base_url": "http://localhost:11434"}` 형태의 설정 딕셔너리

### LLM Provider 스위칭 설계의 이유

이 책은 현재 Ollama만 지원하지만, `get_llm_config()` 함수를 이렇게 설계한 데에는 이유가 있습니다. 향후 OpenAI API나 다른 클라우드 서비스로 전환할 때 **코드를 수정하지 않고 `.env` 파일의 `LLM_PROVIDER` 값 하나만 바꾸면** 됩니다.

```mermaid
flowchart TD
    A[".env 파일"] -- "LLM_PROVIDER=ollama" --> B["get_llm_config()"]
    B -- "ollama 분기" --> C["Ollama 설정 반환"]
    B -- "openai 분기(향후)" --> D["OpenAI 설정 반환"]
    C -- "LangChain에 전달" --> E["ChatOllama"]
    D -- "LangChain에 전달" --> F["ChatOpenAI"]
```

*그림 2-4: LLM Provider 스위칭 설계 구조*

3장 이후의 모든 코드는 `get_llm_config()`를 통해 LLM 설정을 받아옵니다. 이 구조 덕분에 LLM 교체가 단 한 줄의 환경 변수 변경으로 가능합니다.

> **참고: PostgreSQL 연결 URL 생성**
> `config.py`의 `get_postgres_url()` 함수는 PostgreSQL 접속 URL을 자동으로 조합합니다.
> ```python
> # 반환 예시
> "postgresql://admin:changeme@localhost:5432/company_db"
> ```
> 3장 이후 코드에서 직접 URL 문자열을 작성할 필요 없이 이 함수를 호출합니다.

---

## 5. 환경 전체 동작 확인

### verify_env.py 실행

개념을 이해했으니 이제 환경이 올바르게 구축되었는지 확인합니다. `src/verify_env.py` 스크립트는 6가지 항목을 순서대로 점검합니다.

```bash
python src/verify_env.py
```

이 스크립트의 핵심 동작을 살펴보겠습니다.

```python
# src/verify_env.py (main 함수 발췌)

def main() -> None:
    """환경 점검 전체 절차를 순서대로 실행합니다."""

    results: dict[str, bool] = {}

    # 1. Python 버전 확인
    results["python_version"] = check_python_version()   # Python 3.11 이상

    # 2. .env 파일 존재 확인
    results["env_file"] = check_env_file()               # .env 파일 존재 여부

    # 3. 환경 변수 로딩 확인
    results["env_vars"] = check_env_vars()               # config.py 로딩 가능 여부

    # 4. Python 패키지 설치 확인
    results["packages"] = check_packages()               # langchain, chromadb 등 import

    # 5. Ollama 서버 확인
    results["ollama"] = check_ollama()                   # localhost:11434 응답 여부

    # 6. PostgreSQL 접속 확인
    results["postgres"] = check_postgres()               # psycopg2 접속 성공 여부
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 현재 시스템 환경 (Python 버전, 설치된 패키지, 실행 중인 서비스)
2. **처리(Process)**: 6가지 항목을 순서대로 확인하고 각 결과를 `True/False`로 수집
3. **출력(Output)**: 항목별 `[OK]` / `[FAIL]` 결과와 전체 통과 여부 출력

### 예상 출력 결과

모든 항목을 통과하면 아래와 같이 출력됩니다.

```
=======================================================
  2장 개발 환경 구축 — 동작 확인
  AI 업무 비서 구축: RAG + MCP 실전 가이드
=======================================================

[1] Python 버전 확인
  [OK] Python 3.11.9

[2] .env 파일 확인
  [OK] .env 파일 확인: /path/to/project/.env

[3] 환경 변수 로딩 (config.py)
  [OK] 환경 변수 로딩 성공 (LLM_PROVIDER=ollama)

[4] Python 패키지 설치 확인
  [OK] python-dotenv
  [OK] langchain
  [OK] chromadb
  [OK] psycopg2-binary
  [OK] httpx
  [OK] fastapi

[5] Ollama 서버 연결 확인
  [OK] Ollama 서버 응답 확인 (URL: http://localhost:11434)
       다운로드된 모델: deepseek-r1:latest, nomic-embed-text:latest

[6] PostgreSQL 접속 확인
  [OK] PostgreSQL 접속 성공
       PostgreSQL 16.x on x86_64-pc-linux-gnu...

=======================================================
  결과: 전체 통과 (6/6)

  개발 환경이 정상적으로 구축되었습니다.
  3장으로 넘어가십시오.
=======================================================
```

<!-- [CAPTURE NEEDED: 02_verify-env — `python src/verify_env.py` 실행 후 모든 항목이 [OK]로 표시된 터미널 전체 화면] -->
*그림 2-5: verify_env.py 전체 통과 결과 화면*

### FAIL 항목별 대응 방법

일부 항목이 실패하더라도 당황하지 마십시오. 각 `[FAIL]` 메시지 아래에 해결 방법이 출력됩니다. 자주 발생하는 오류와 대응 방법을 정리합니다.

| 항목 | 증상 | 해결 방법 |
|------|------|---------|
| Python 버전 | `Python 3.9.x` 출력 | Python 3.11 설치 후 가상환경 재생성 |
| .env 파일 | `.env 파일이 없습니다` | `cp .env.example .env` 실행 |
| Ollama 서버 | `Ollama 서버에 연결할 수 없습니다` | `ollama serve` 명령으로 서버 시작 |
| PostgreSQL | `접속 실패` | `docker-compose up -d` 실행 후 재시도 |
| 패키지 | `[FAIL] chromadb` | `pip install -r requirements.txt` 재실행 |

> **팁: Ollama 서버 자동 시작**
> macOS에서는 Ollama 앱을 설치하면 시스템 시작 시 자동으로 서버가 실행됩니다.
> 수동으로 시작하려면 터미널에서 `ollama serve` 명령을 실행하십시오.
> Ubuntu에서는 `sudo systemctl start ollama` 명령을 사용합니다.

---

## 6. 정리하며

이 장에서 구축한 네 가지 환경 요소는 이 책의 모든 실습을 뒷받침하는 기반이 됩니다.

- **Ollama + DeepSeek R1**: 외부 API 없이 로컬에서 LLM을 실행하는 환경이 완성되었습니다. `ollama pull deepseek-r1`과 `ollama pull nomic-embed-text`로 텍스트 생성과 임베딩 두 가지 모델을 모두 확보했습니다.
- **Docker Compose + PostgreSQL 16**: `docker-compose.yml` 하나로 데이터베이스 환경을 재현합니다. 직접 설치가 아닌 컨테이너 방식이므로 환경 격리와 초기화가 용이합니다.
- **Python 3.11 가상환경 + requirements.txt**: 버전이 고정된 패키지 환경이 격리되었습니다. `venv`와 `requirements.txt`로 어떤 컴퓨터에서도 동일한 환경을 재현할 수 있습니다.
- **.env 설정 + config.py 스위칭 구조**: 비밀번호와 서버 주소를 코드 바깥에 분리했습니다. `LLM_PROVIDER` 환경 변수 하나로 LLM 백엔드를 전환하는 구조는 3장 이후 모든 챕터에서 재사용됩니다.

**다음 장 예고**: 개발 환경이 완성되었습니다. 3장에서는 구축한 Ollama + DeepSeek R1 환경을 사용하여 LLM 단독으로 질문에 답하게 한 뒤, 환각(Hallucination)이 발생하는 순간을 직접 체험합니다. 이 체험이 이 책 전체의 동기, 즉 "왜 RAG가 필요한가"에 대한 답이 됩니다.



---

# 3. DeepSeek R1으로 체험하는 LLM의 한계와 RAG의 필요성

2장에서 Ollama, PostgreSQL, Python 가상환경을 완비했습니다. 이 장에서는 구축된 환경을 사용하여 LLM의 결정적인 약점을 직접 체험합니다.

"LLM이 이미 있는데 왜 RAG까지 필요한가?" 많은 개발자가 처음에 품는 질문입니다. 이 장은 그 질문에 코드로 답합니다. 환각(Hallucination)이 발생하는 순간을 직접 눈으로 확인하고, Context Injection으로 임시 해결을 시도한 뒤, 마지막으로 40줄의 RAG 코드가 그 한계를 어떻게 돌파하는지 4단계로 비교합니다.

<!-- [IMAGE PLACEHOLDER: 03_chapter-overview — 4단계 비교 흐름: LLM 단독(환각) → Context Injection(한계) → RAG 미리보기(성공) → RAG+추론(심화)] -->
*그림 3-1: 이 장에서 체험할 4단계 비교 흐름*

---

## 1. [실패] LLM 단독 질의의 한계

### 1.1 레포 클론 및 실행 준비

먼저 예제 레포를 클론하고 환경을 설정하십시오.

```bash
git clone https://github.com/your-org/CH03_LLM한계와RAG필요성.git
cd CH03_LLM한계와RAG필요성

cp .env.example .env
# .env 파일을 열어 OLLAMA_MODEL, OLLAMA_BASE_URL 값을 확인하십시오

pip install -r requirements.txt

# 임베딩 모델 다운로드 (3번, 4번 실험에서 필요)
ollama pull nomic-embed-text
```

> **참고: .env 기본값 확인**
> `.env.example`에는 `LLM_MODEL_NAME=deepseek-r1:1.5b`가 기본값으로 설정되어 있습니다. 사용 중인 모델명이 다르면 해당 값을 수정하십시오. `deepseek-r1:8b` 이상 모델은 추론 품질이 더 높지만 RAM을 더 많이 사용합니다.

### 1.2 실험 실행

첫 번째 실험을 실행하십시오.

```bash
python src/01_llm_only.py
```

`01_llm_only.py`는 가상의 회사 "테크컴퍼니"에 관한 세 가지 질문을 LLM에게 던집니다. 참고 문서 없이, LLM의 학습 데이터만으로 답변하도록 합니다.

```python
# src/01_llm_only.py 핵심 발췌

QUESTIONS: list[str] = [
    "우리 회사(테크컴퍼니)의 신입사원 연차 발생 규정이 어떻게 돼?",
    "2024년 4분기 마케팅팀 매출 목표는 얼마야?",
    "사내 보안 USB 정책이 어떻게 돼?",
]


def ask_llm(question: str) -> str:
    """
    ChatOllama DeepSeek R1을 단독 호출하여 응답을 반환합니다.

    Input  : 사내 정보를 묻는 질문 문자열
    Process: ChatOllama.invoke()로 컨텍스트 없이 질문을 전달
    Output : LLM 응답 문자열
    """
    # --- Process ---
    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0,  # 재현 가능한 결과를 위해 고정
    )
    response = llm.invoke(question)

    # --- Output ---
    return response.content
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: `QUESTIONS` 상수에 정의된 사내 비공개 정보 질문 3개
2. **처리(Process)**: `ChatOllama.invoke(question)`으로 참고 문서 없이 질문을 그대로 LLM에 전달
3. **출력(Output)**: LLM 응답 문자열 및 환각 관찰 포인트 메시지를 터미널에 출력

실행하면 아래와 같은 응답이 출력됩니다.

> **[환각 응답 예시]**
> 질문: "우리 회사(테크컴퍼니)의 신입사원 연차 발생 규정이 어떻게 돼?"
>
> LLM 답변: "테크컴퍼니의 신입사원 연차 규정은 입사 1년 후 15일의 연차가 발생하며, 이후 매년 1일씩 추가됩니다. 첫 해에는 월 1일의 비율로 최대 11일까지 사용할 수 있습니다..."
>
> [환각 관찰 포인트]
> '테크컴퍼니'의 연차 규정은 사내 취업규칙에만 존재합니다.
> LLM이 일반적인 근로기준법 내용으로 대체하거나, 실제 규정과 다른 내용을 자신 있게 답변하면 환각입니다.

<!-- [CAPTURE NEEDED: 03_llm-only-output — `python src/01_llm_only.py` 실행 후 터미널에 출력된 질문/답변/환각 관찰 포인트 전체] -->
*그림 3-2: LLM 단독 질의 실행 결과 — 환각 응답 확인*

두 번째 질문("2024년 4분기 마케팅팀 매출 목표")에서 LLM은 구체적인 숫자를 제시할 가능성이 높습니다. 이 숫자는 완전한 허구입니다. 이 현상이 바로 **환각(Hallucination)** 입니다.

---

## 2. 왜 LLM은 환각을 일으키는가

방금 목격한 현상의 원인을 이해하십시오. 원인을 알아야 올바른 해결책을 선택할 수 있습니다.

### 2.1 학습 데이터 컷오프

LLM은 특정 시점까지 수집된 인터넷 데이터로 학습합니다. 이를 **학습 데이터 컷오프(Training Cutoff)** 라고 합니다. DeepSeek R1이 2023년 말까지의 데이터로 학습했다고 가정하면, 그 이후에 만들어진 사내 문서나 내부 규정은 학습 데이터에 포함되지 않습니다.

```
LLM의 지식 = 학습 데이터(인터넷 공개 데이터)
           ≠ 사내 비공개 문서
           ≠ 특정 시점 이후 데이터
```

### 2.2 확률적 언어 모델의 본질

더 근본적인 이유가 있습니다. LLM은 "다음에 올 가능성이 높은 토큰"을 예측하는 확률 모델입니다. "신입사원 연차 규정은..."이라는 프롬프트를 받으면, 학습 데이터에서 이 문맥 다음에 자주 등장한 단어들을 이어 붙입니다.

이 과정에서 LLM은 자신이 모른다는 사실을 인지하지 못합니다. 그저 확률적으로 가장 자연스러운 다음 단어를 생성할 뿐입니다. 그 결과 "틀렸지만 그럴듯한" 응답이 자신감 있게 출력됩니다.

```mermaid
flowchart LR
    A["사내 질문"] -- "컨텍스트 없이" --> B["DeepSeek R1"]
    B -- "학습 데이터에서\n가장 확률 높은 토큰 생성" --> C["환각 응답"]
    C -- "자신감 있는\n잘못된 정보" --> D["신뢰 불가"]
```

*그림 3-3: LLM 단독 질의 흐름 — 컨텍스트 없이 확률적 토큰 생성*

> **참고: 환각은 버그가 아닌 설계 특성**
> 환각은 LLM의 결함이 아닙니다. 다음 토큰을 예측하도록 설계된 구조에서 자연스럽게 발생하는 현상입니다. 이 특성을 이해하고 RAG로 보완하는 것이 올바른 접근입니다.

---

## 3. [임시 해결] Context Injection 맛보기

환각을 일으키는 원인이 "참고 문서 부재"라면, 문서를 프롬프트에 직접 넣으면 어떨까요? 이 방법을 **컨텍스트 주입(Context Injection)** 이라고 합니다.

### 3.1 실험 실행

```bash
python src/02_context_injection.py
```

`02_context_injection.py`는 `data/sample_hr_policy.txt` 문서 전체를 프롬프트 앞에 붙여 동일한 세 가지 질문을 실행합니다.

```python
# src/02_context_injection.py 핵심 발췌

def build_prompt(question: str, context: str) -> str:
    """
    질문과 문서 전체를 하나의 프롬프트 문자열로 조합합니다.

    Input  : 사용자 질문, 참고 문서 내용 문자열
    Process: 시스템 역할 안내 + 참고 문서 + 질문을 하나의 문자열로 결합
    Output : LLM에 전달할 완성된 프롬프트 문자열
    """
    # --- Process ---
    prompt = f"""당신은 회사 내부 규정에 대해 답변하는 AI 비서입니다.
아래 [참고 문서]를 바탕으로 질문에 답변하십시오.
참고 문서에 없는 내용은 "해당 내용이 문서에 없습니다"라고 답변하십시오.
반드시 한국어로 답변하십시오.

[참고 문서]
{context}

[질문]
{question}

[답변]"""
    # --- Output ---
    return prompt


def count_tokens(text: str) -> int:
    """대략적인 토큰 수 추정 (len(text) // 4)."""
    return len(text) // 4


def ask_with_context(question: str, context: str) -> dict:
    """
    Input  : 사용자 질문 문자열, 참고 문서 내용 문자열
    Process: 프롬프트 조합 → 토큰 추정 → ChatOllama 호출
    Output : {"response": str, "token_estimate": int, "over_limit": bool}
    """
    # --- Input ---
    prompt = build_prompt(question, context)
    token_estimate = count_tokens(prompt)
    over_limit = token_estimate > TOKEN_WARNING_THRESHOLD  # 4000 초과 시

    if over_limit:
        print(f"  [토큰 경고] 추정 토큰 수: {token_estimate:,}개")
        print("             문서가 많아질수록 이 숫자는 선형으로 증가합니다.")

    # --- Process ---
    llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0)
    response = llm.invoke(prompt)

    # --- Output ---
    return {
        "response": response.content,
        "token_estimate": token_estimate,
        "over_limit": over_limit,
    }
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: `sample_hr_policy.txt` 전체 문서(약 1,500자 이상)와 질문 3개
2. **처리(Process)**: `build_prompt()`로 문서 + 질문을 단일 프롬프트로 조합 → `count_tokens()`로 토큰 추정 → `ChatOllama.invoke()`로 LLM 호출
3. **출력(Output)**: 응답 문자열, 토큰 추정치, 임계값(4,000) 초과 여부가 담긴 딕셔너리

### 3.2 응답 개선 확인과 한계 체감

응답이 눈에 띄게 개선됩니다. 연차 규정 질문에는 "테크컴퍼니" 사내 규정에 맞는 정확한 답변이 출력됩니다. 매출 목표 질문에는 "해당 내용이 문서에 없습니다"라는 올바른 거절도 확인할 수 있습니다.

그러나 터미널 출력에서 핵심 문제가 드러납니다.

```
[토큰 추정] 약 650개 (임계값 4,000개 이내)

한계 정리:
  1. 문서 1개에 이미 약 650개의 토큰을 사용합니다.
  2. 사내 문서가 수십 개라면 전체를 삽입하는 것은 불가능합니다.
  3. 문서가 많을수록 응답 속도가 선형으로 저하됩니다.
  4. LLM의 컨텍스트 한계를 초과하면 문서 내용이 잘립니다.
```

HR 정책 문서 하나만 넣어도 650개의 토큰을 소비합니다. 실제 사내 환경에는 수십, 수백 개의 문서가 있습니다. 이 모든 문서를 프롬프트에 붙이면 LLM의 컨텍스트 한도(보통 4,096~32,768 토큰)를 초과하거나, 처리 속도가 급격히 저하됩니다.

> **주의: Context Injection의 확장성 한계**
> Context Injection은 문서가 1~2개일 때는 동작하지만, 실제 사내 지식베이스처럼 수십 개의 문서가 있는 환경에서는 확장(Scale)이 불가능합니다. 질문마다 매번 모든 문서를 붙여 넣는 것은 비용과 속도 측면에서 현실적이지 않습니다.

```mermaid
flowchart LR
    A["질문 + 문서 전체"] -- "프롬프트 조합" --> B["DeepSeek R1"]
    B -- "문서 기반 답변" --> C["개선된 응답"]
    C -. "문서 1개: 650토큰\n문서 50개: 32,500토큰" .-> D["토큰 한계 초과"]
```

*그림 3-4: Context Injection 흐름 — 응답은 개선되지만 토큰 소비가 선형으로 증가*

---

## 4. [성공] RAG 미리보기 + 청킹 비교

Context Injection의 핵심 문제는 "필요 없는 문서까지 전부 넣는다"는 점입니다. 해결책은 간단합니다. 질문과 관련된 부분만 정밀하게 찾아서 넣으면 됩니다. 이것이 **검색 증강 생성(RAG, Retrieval-Augmented Generation)** 입니다.

<!-- [IMAGE PLACEHOLDER: 03_rag-concept — RAG 개념도: 질문이 벡터DB에서 관련 청크를 검색하고, 그 청크만 LLM에 전달하는 흐름] -->
*그림 3-5: RAG 개념 — 관련 청크만 선별하여 LLM에 전달*

### 4.1 청킹이란 무엇인가

RAG가 "관련 부분만 찾으려면" 문서를 작은 조각으로 나누어야 합니다. 이 과정을 **청킹(Chunking)** 이라 합니다. 도서관에서 책 전체를 빌리는 것이 아니라, 관련 페이지만 복사하는 것과 같습니다.

3번 실험에서는 청킹이 없을 때와 있을 때의 검색 정밀도 차이를 동일한 문서로 나란히 비교합니다.

### 4.2 실험 실행

```bash
python src/03_rag_preview.py
```

> **참고: 처음 실행 시 임베딩 시간 소요**
> `nomic-embed-text` 모델이 처음 실행될 때 모델을 로드하는 시간이 필요합니다. 이후 실행부터는 빠르게 동작합니다.

### 4.3 Part A — 청킹 없이

```python
# src/03_rag_preview.py 핵심 발췌 — Part A

def build_vectorstore_no_chunk(doc: str) -> Chroma:
    """
    문서 전체를 단일 Document로 인메모리 ChromaDB에 저장합니다.

    Input  : 저장할 텍스트 문서 문자열
    Process: 단일 Document 생성 → OllamaEmbeddings → 인메모리 Chroma 생성
    Output : 인메모리 ChromaDB VectorStore 인스턴스
    """
    # --- Input ---
    documents = [
        Document(
            page_content=doc,
            metadata={"source": "hr_policy", "chunk_id": 0, "method": "no_chunk"},
        )
    ]
    # --- Process ---
    embeddings = OllamaEmbeddings(model=EMBED_MODEL, base_url=OLLAMA_BASE_URL)
    # persist_directory 없음 → 인메모리 전용 (재실행 시 소멸)
    vectorstore = Chroma.from_documents(documents=documents, embedding=embeddings)

    # --- Output ---
    return vectorstore
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: `LONG_DOC` — 3개 조항(연차·보안 USB·식대)이 포함된 HR 규정 전문(약 500자)
2. **처리(Process)**: 문서 전체를 단일 `Document` 객체로 만들어 `nomic-embed-text`로 임베딩 → 인메모리 `Chroma`에 저장
3. **출력(Output)**: 문서 1개가 저장된 인메모리 VectorStore

질문("신입사원 리프레시 데이 규정 알려줘")과의 유사도 검색 결과, 검색된 문서 수는 1개이며 그 내용은 연차 조항뿐만 아니라 보안 USB 조항, 식대 조항이 모두 포함됩니다.

### 4.4 Part B — 청킹 있을 때

```python
# src/03_rag_preview.py 핵심 발췌 — Part B

def chunk_text(text: str, chunk_size: int = 200, overlap: int = 20) -> list[str]:
    """
    텍스트를 chunk_size 단위로 분할합니다. overlap만큼 이전 청크와 겹칩니다.

    Input  : 분할할 텍스트 문자열, 청크 크기(자), 오버랩(자)
    Process: chunk_size 간격으로 시작점을 이동하며 슬라이싱
    Output : 청크 문자열 목록
    """
    # --- Process ---
    chunks: list[str] = []
    step = chunk_size - overlap  # 실제 이동 간격 = 청크 크기 - 오버랩
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += step

    # --- Output ---
    return chunks
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: `LONG_DOC` 전문, `chunk_size=200`, `overlap=20`
2. **처리(Process)**: 200자 단위로 슬라이싱, 청크 간 20자 오버랩으로 문맥 단절 방지
3. **출력(Output)**: 여러 개의 청크 문자열 목록 (약 5~7개)

이 청크들이 각각 별도 `Document`로 임베딩되어 저장됩니다. 같은 질문으로 검색하면 "제1조(연차 및 리프레시 데이)" 관련 청크만 선별되어 반환됩니다.

### 4.5 LCEL RAG 체인 구성

두 실험 모두 동일한 LCEL(LangChain Expression Language) 파이프라인을 사용합니다.

```python
# src/03_rag_preview.py 핵심 발췌 — LCEL RAG 체인

def build_rag_chain(vectorstore: Chroma, k: int = 2) -> Any:
    """
    LCEL 기반 RAG 체인을 생성합니다.

    Input  : Chroma VectorStore 인스턴스, 검색할 문서 수 k
    Process: retriever 생성 → 프롬프트 정의 → LCEL | 체인 구성
    Output : 실행 가능한 LCEL Runnable 체인
    """
    # --- Input ---
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})

    # --- Process ---
    prompt = ChatPromptTemplate.from_template(
        """당신은 회사 내부 규정에 대해 답변하는 AI 비서입니다.
아래 [참고 문서]를 바탕으로 질문에 답변하십시오.
참고 문서에 없는 내용은 "해당 내용이 문서에 없습니다"라고 답변하십시오.
반드시 한국어로 답변하십시오.

[참고 문서]
{context}

[질문]
{question}

[답변]"""
    )
    llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0)

    # LCEL 파이프라인: | 연산자로 검색기 → 프롬프트 → LLM → 파서를 연결
    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    # --- Output ---
    return rag_chain, retriever
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: `Chroma` VectorStore 인스턴스, 반환할 최대 문서 수 `k`
2. **처리(Process)**: `as_retriever()`로 검색기 생성 → LCEL `|` 연산자로 `{context + question}` → 프롬프트 → `ChatOllama` → `StrOutputParser` 파이프라인 구성
3. **출력(Output)**: `chain.invoke(query)` 호출로 최종 응답 문자열을 반환하는 Runnable 체인

> **팁: LCEL의 | 연산자**
> LCEL에서 `|` 연산자는 왼쪽 컴포넌트의 출력을 오른쪽 컴포넌트의 입력으로 연결합니다. `retriever | format_docs`는 "검색 결과를 format_docs 함수로 변환하라"는 의미입니다. 이 방식은 기존의 `RetrievalQA` 클래스보다 훨씬 직관적이고 유연합니다.

### 4.6 비교 결과 확인

실행 결과에서 두 파트의 차이를 확인하십시오.

```
══ Part A: 청킹 없이 ══════════════════════════════════════
   검색된 문서 수: 1개  (문서 전체 1개)
   검색 내용 미리보기: [테크컴퍼니 취업규칙 요약] 제1조 (신입사원 연차 및 리프레시 데이...

══ Part B: 청킹 있을 때 ═══════════════════════════════════
   검색된 문서 수: 2개  (관련 청크만 선택됨)
   [청크 0] [테크컴퍼니 취업규칙 요약] 제1조 (신입사원 연차 및 리프레시 데이 규정)...
   [청크 1] 제1조 ... 리프레시 데이는 해당 월에 미사용 시 다음 달로 이월되지 않는다...

── 비교 결과 ──────────────────────────────────────────────
  청킹 없음 (Part A): 검색 문서 1개, 문서 전체 내용 포함
                     → 질문과 무관한 내용(보안 정책, 식대 등)도 컨텍스트에 포함
  청킹 있음 (Part B): 검색 문서 2개, 관련 청크만 선택
                     → 제1조(연차·리프레시 데이) 관련 내용만 컨텍스트에 포함
```

<!-- [CAPTURE NEEDED: 03_rag-comparison — `python src/03_rag_preview.py` 실행 후 Part A와 Part B 결과를 나란히 보여주는 터미널 전체 화면] -->
*그림 3-6: RAG 미리보기 — 청킹 없음(Part A)과 청킹 있음(Part B) 비교 결과*

Part B에서 LLM이 받는 컨텍스트는 연차 관련 청크 2개뿐입니다. 보안 USB 정책이나 식대 내용은 컨텍스트에 포함되지 않으므로 LLM이 더 집중적이고 정확한 답변을 생성합니다.

> **참고: 이 장의 ChromaDB는 인메모리 전용**
> `build_vectorstore_no_chunk()`와 `build_vectorstore_with_chunk()`에서 `persist_directory` 파라미터를 지정하지 않으면 ChromaDB는 인메모리 모드로 동작합니다. 스크립트가 종료되면 저장된 데이터가 모두 소멸됩니다. 영속화(Persist)하여 재사용하는 방법은 6장(벡터 DB 구축)에서 자세히 다룹니다.

---

## 5. [심화] DeepSeek R1 추론 능력 확인

RAG는 단순히 문서를 찾아서 붙여 넣는 도구가 아닙니다. 검색된 문서를 바탕으로 LLM이 **추론(Reasoning)** 까지 수행할 수 있다는 점이 핵심입니다. 이 차이를 직접 확인하십시오.

### 5.1 실험 실행

```bash
python src/04_rag_reasoning.py
```

4번 실험은 3번과 동일한 LCEL 구조를 사용하되, 질문을 단순 정보 검색이 아닌 계산·추론이 필요한 형태로 교체합니다.

```python
# src/04_rag_reasoning.py 핵심 발췌

REASONING_QUESTION: str = (
    "입사 6개월차 신입인데 리프레시 데이 2번 썼어. "
    "몇 번 남았는지 규정 기반으로 계산해줘."
)
```

LLM이 이 질문에 답하려면 다음 단계가 필요합니다.

1. ChromaDB에서 "신입사원 리프레시 데이" 관련 규정 검색
2. 규정 확인: "매월 1회 유급 리프레시 데이를 사용할 수 있다"
3. 계산: 6개월 × 1회 = 총 6회 가능, 2회 사용 → 6 - 2 = 4회 남음
4. 답변 생성

### 5.2 추론에 특화된 프롬프트

```python
# src/04_rag_reasoning.py 핵심 발췌 — 추론 프롬프트

def build_rag_chain(vectorstore: Chroma, k: int = 2) -> tuple[Any, Any]:
    """
    추론·계산 질문에 특화된 LCEL 기반 RAG 체인을 생성합니다.

    Input  : Chroma VectorStore 인스턴스, 검색할 문서 수 k
    Process: retriever 생성 → 추론 프롬프트 정의 → LCEL | 체인 구성
    Output : (LCEL Runnable 체인, retriever) 튜플
    """
    # --- Process ---
    prompt = ChatPromptTemplate.from_template(
        """당신은 회사 내부 규정을 기반으로 계산과 추론을 수행하는 AI 비서입니다.
아래 [참고 문서]의 규정을 근거로 질문에 답변하십시오.

중요 지침:
  1. 계산이 필요한 경우 반드시 계산 과정을 단계별로 제시하십시오.
  2. 규정의 어느 조항을 근거로 답변하는지 명시하십시오.
  3. 참고 문서에 없는 내용은 "해당 내용이 문서에 없습니다"라고 답변하십시오.
  4. 반드시 한국어로 답변하십시오.

[참고 문서]
{context}

[질문]
{question}

[답변 — 규정 근거와 계산 과정을 포함하여]"""
    )
    # ...LCEL 체인 구성 (03_rag_preview.py와 동일)
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 계산·추론이 필요한 질문 `REASONING_QUESTION`과 3개의 `HR_DOCS` 문서
2. **처리(Process)**: `build_vectorstore()`로 인사규정 청크를 임베딩 → LCEL 체인으로 "리프레시 데이" 관련 청크 검색 → 추론 프롬프트에 청크 삽입 → DeepSeek R1이 규정 기반으로 6 - 2 = 4를 계산하여 답변 생성
3. **출력(Output)**: 검색된 근거 문서 출처와 단계별 계산 과정이 포함된 최종 답변

### 5.3 실행 결과 및 DeepSeek R1의 추론 과정

실행 결과에서 핵심을 확인하십시오.

```
[검색 근거 문서] — 2개 청크가 LLM에 전달되었습니다.
-------------------------------------------------------------
  [1] 인사규정 제4조
      [인사규정] 신입사원 연차 및 리프레시 데이: 신입사원은 입사 후 3년간 법정 연...
  [2] 보안규정 제7조
      [보안규정] 보안 USB 사용 정책: 모든 임직원은 회사가 지급한 보안 인증 USB...
-------------------------------------------------------------

LLM 추론 답변:

인사규정 제4조에 따르면, 신입사원은 매월 1회 유급 리프레시 데이를 사용할 수 있습니다.

계산 과정:
1. 입사 6개월차 → 사용 가능한 총 리프레시 데이: 6개월 × 1회 = 6회
2. 이미 사용한 횟수: 2회
3. 남은 횟수: 6 - 2 = 4회

따라서 현재 리프레시 데이는 4번 남아 있습니다.
```

<!-- [CAPTURE NEEDED: 03_rag-reasoning-output — `python src/04_rag_reasoning.py` 실행 후 검색 근거 문서 + 단계별 계산 과정이 포함된 LLM 답변 전체] -->
*그림 3-7: RAG + 추론 실행 결과 — 규정 근거와 계산 과정이 포함된 답변*

LLM이 단순히 규정을 검색해서 반환한 것이 아닙니다. 검색된 규정("매월 1회")을 바탕으로 6 × 1 - 2 = 4라는 계산을 직접 수행했습니다. 이것이 RAG와 LLM 추론 능력의 조합이 강력한 이유입니다.

> **팁: DeepSeek R1의 `<think>` 태그**
> DeepSeek R1의 일부 버전은 응답 전에 `<think>...</think>` 태그로 내부 추론 과정을 먼저 출력합니다. 이 내용은 최종 답변 전에 모델이 어떻게 생각하는지 보여주는 디버그 정보입니다. 7장(RAG Q&A 엔진)의 `LLMService`에서 이 태그를 자동으로 제거하는 처리를 구현합니다.

### 5.4 4단계 비교 정리

이 장에서 실행한 4개의 실험을 한눈에 비교하십시오.

| 실험 | 방법 | 결과 | 한계 |
|------|------|------|------|
| 1단계 `01_llm_only.py` | LLM 단독 질의 | 환각 응답 | 사내 정보 없음 |
| 2단계 `02_context_injection.py` | 문서 전체 삽입 | 응답 개선 | 토큰 한계, 확장 불가 |
| 3단계 `03_rag_preview.py` | 인메모리 RAG | 관련 청크만 검색 | 인메모리 전용 (영속화 없음) |
| 4단계 `04_rag_reasoning.py` | RAG + 추론 | 계산 포함 정확 답변 | 인메모리 전용 |

```mermaid
flowchart TD
    A["Step 1: LLM 단독\n환각 발생"] -- "문서 직접 삽입" --> B["Step 2: Context Injection\n응답 개선 + 토큰 한계"]
    B -- "검색으로 관련 청크만 선택" --> C["Step 3: RAG 미리보기\n정밀 검색 성공"]
    C -- "추론 질문으로 교체" --> D["Step 4: RAG + 추론\n계산 포함 답변"]
```

*그림 3-8: 4단계 비교 흐름 — 각 단계의 개선 포인트*

---

## 6. 정리하며

이 장에서는 4개의 실험을 통해 LLM의 한계와 RAG의 필요성을 직접 체감했습니다.

- **환각은 LLM의 구조적 특성이다**: 학습 데이터 컷오프와 확률적 토큰 예측 방식으로 인해, LLM은 사내 비공개 정보를 모르면서도 그럴듯한 응답을 자신감 있게 생성합니다. 이것이 환각이며, 운영 환경에서 LLM을 단독으로 사용하면 안 되는 이유입니다.

- **Context Injection은 임시 방편이다**: 문서를 프롬프트에 직접 삽입하면 응답은 개선되지만, 문서 수가 늘어날수록 토큰 소비가 선형으로 증가합니다. 실제 사내 지식베이스처럼 수십 개의 문서가 있는 환경에서는 확장이 불가능합니다.

- **RAG는 관련 청크만 정밀하게 선별한다**: 문서를 청크로 분할하고 임베딩 벡터로 저장한 뒤, 질문과 유사도가 높은 청크만 검색하여 LLM에 전달합니다. 이 방식은 토큰 소비를 최소화하면서 응답 정확도를 높입니다.

- **청킹은 RAG 검색 정밀도를 결정한다**: 청킹 없이 문서 전체를 저장하면 질문과 무관한 내용이 컨텍스트에 포함됩니다. 적절한 크기로 청킹하면 관련 내용만 선별되어 LLM이 더 집중적인 답변을 생성합니다.

- **RAG + LLM 추론의 조합이 핵심이다**: RAG는 단순 검색 도구가 아닙니다. 검색된 규정을 바탕으로 LLM이 계산·추론을 수행합니다. "6개월 × 1회 - 2회 = 4회"처럼, 문서에 명시되지 않은 결론도 도출할 수 있습니다.

---

다음 장에서는 이 장에서 사용한 인메모리 ChromaDB를 넘어, 사내 시스템(PostgreSQL DB + FastAPI CRUD API)을 `git clone`으로 확보합니다. RAG가 왜 필요한지 확인한 지금, 4장에서 실제 시스템 인프라를 갖추겠습니다.



---

# 4. 베이스 시스템 확보

이 장에서는 RAG 파이프라인의 기반이 되는 사내 시스템 인프라를 확보합니다. PostgreSQL 데이터베이스와 FastAPI CRUD 서버를 단 하나의 명령으로 구동하고, 테이블 스키마와 API 엔드포인트 구조를 파악합니다. 또한 8장에서 본격적으로 구현할 **MCP(Model Context Protocol)** 의 개념을 미리 익혀 두겠습니다.

3장에서 LLM 단독으로는 사내 정형 데이터를 조회할 수 없다는 한계를 직접 체험했습니다. 이 장은 그 한계를 극복하기 위한 첫 번째 인프라 단계입니다. 직원 정보, 연차 현황, 매출 실적이 담긴 데이터베이스와 그것을 REST API로 노출하는 서버를 확보하고 나면, 이후 챕터에서 LLM이 이 데이터에 접근하는 방법을 단계적으로 구현할 수 있습니다.

---

## 4.1 사내 시스템 git clone으로 확보

### 왜 직접 구축하지 않는가

이 책의 핵심 주제는 RAG 파이프라인과 MCP 에이전트 구현입니다. PostgreSQL 스키마를 설계하고 FastAPI 서버를 처음부터 작성하는 데 시간을 할애하면 정작 중요한 주제에 집중하기 어렵습니다. 따라서 이 챕터는 **이미 완성된 인프라 레포를 clone하여 즉시 구동하는 방식** 을 택합니다.

인프라 코드를 미리 제공하는 데는 또 다른 이유도 있습니다. 실무에서 AI 기능을 추가할 때는 대부분 기존 시스템이 이미 운영 중입니다. "내가 직접 만들지 않은 API와 DB를 LLM과 연결하는 방법"을 익히는 것이 현실에 더 가깝습니다.

> **참고: 이 챕터의 인프라는 CH05~CH08까지 공통으로 사용됩니다.**
> CH04에서 구동한 PostgreSQL과 FastAPI 서버는 이후 챕터에서 계속 실행 상태를 유지해야 합니다. 챕터를 마칠 때 `docker-compose down`을 실행하지 마십시오.

### git clone 및 구동

아래 명령어를 순서대로 실행하십시오.

**1단계 — 레포 clone**

```bash
git clone https://github.com/rag-mcp-guide/rag-infra.git
cd rag-infra
```

> **참고: 로컬 예제 코드 사용**
> GitHub 레포 대신 이 책과 함께 제공된 예제 디렉토리를 사용하려면 `수동/examples/CH04_베이스시스템확보/` 폴더로 이동하십시오.

**2단계 — 환경 변수 설정**

```bash
cp .env.example .env
```

`.env.example` 파일에는 아래와 같은 기본값이 들어 있습니다.

```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=rag_db
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=rag_password
```

기본값 그대로 사용해도 실습에 문제가 없습니다. 포트 충돌이 발생하는 경우에만 `POSTGRES_PORT` 값을 변경하십시오.

**3단계 — 전체 인프라 구동**

```bash
docker-compose up -d
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: `docker-compose.yml` 파일과 `.env` 환경 변수
2. **처리(Process)**: Docker가 `postgres:16-alpine` 이미지를 내려받고 컨테이너를 시작합니다. PostgreSQL 헬스체크가 통과되면 FastAPI 컨테이너 빌드를 시작합니다. `init/01_schema_and_data.sql` 파일이 최초 1회 자동으로 실행되어 테이블과 샘플 데이터가 생성됩니다.
3. **출력(Output)**: PostgreSQL 서버(포트 5432)와 FastAPI 서버(포트 8000)가 백그라운드에서 실행됩니다.

> **주의: 최초 실행은 2~5분이 소요됩니다.**
> Docker 이미지를 처음 내려받고 FastAPI 컨테이너를 빌드하는 데 시간이 걸립니다. 이미지가 캐시된 이후 실행은 30초 이내로 완료됩니다.

**4단계 — 컨테이너 상태 확인**

```bash
docker-compose ps
```

정상 구동 시 아래와 유사한 출력이 나타납니다.

```
NAME          IMAGE                COMMAND                  SERVICE    CREATED       STATUS                   PORTS
rag_fastapi   rag-infra-fastapi    "uvicorn app.main:ap…"   fastapi    2 minutes ago Up 2 minutes             0.0.0.0:8000->8000/tcp
rag_postgres  postgres:16-alpine   "docker-entrypoint.s…"   postgres   2 minutes ago Up 2 minutes (healthy)   0.0.0.0:5432->5432/tcp
```

`STATUS` 컬럼에서 `postgres`가 `healthy`, `fastapi`가 `Up` 상태인지 확인합니다. `starting` 상태라면 30초 더 기다린 후 다시 실행하십시오.

<!-- [CAPTURE NEEDED: 04_docker-compose-ps — docker-compose ps 실행 후 터미널 전체 출력 (두 컨테이너 모두 Up/healthy 상태)] -->
*그림 4-1: docker-compose ps 실행 결과 — 두 컨테이너가 정상 구동된 상태*

### docker-compose.yml 구조 이해

`docker-compose.yml`은 세 가지 서비스를 정의합니다.

```yaml
services:

  postgres:
    image: postgres:16-alpine
    container_name: rag_postgres
    environment:
      POSTGRES_DB:       ${POSTGRES_DB:-rag_db}
      POSTGRES_USER:     ${POSTGRES_USER:-rag_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-rag_password}
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    volumes:
      - ./init:/docker-entrypoint-initdb.d:ro
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-rag_user}"]
      interval: 10s
      timeout: 5s
      retries: 5

  fastapi:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: rag_fastapi
    depends_on:
      postgres:
        condition: service_healthy
    ports:
      - "8000:8000"
    volumes:
      - ./app:/app/app
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: `.env` 파일의 환경 변수 (DB 이름, 사용자, 비밀번호, 포트)
2. **처리(Process)**: `postgres` 서비스가 먼저 시작되고 헬스체크(`pg_isready`)를 통과할 때까지 대기합니다. `fastapi` 서비스는 `depends_on`의 `condition: service_healthy` 조건으로 PostgreSQL이 준비된 후에만 시작됩니다. `./init` 폴더는 읽기 전용(`ro`)으로 마운트되어 SQL 파일이 자동 실행됩니다.
3. **출력(Output)**: 두 컨테이너가 의존성 순서대로 안전하게 구동됩니다.

`depends_on`에 `condition: service_healthy`를 지정하는 이유는 PostgreSQL이 프로세스는 실행 중이지만 아직 연결을 받을 준비가 되지 않은 상태에서 FastAPI가 연결을 시도하는 경쟁 조건(race condition)을 막기 위해서입니다. 헬스체크를 통과한 후에만 FastAPI가 시작되도록 보장합니다.

---

## 4.2 데이터베이스 스키마 분석

이 시스템이 관리하는 데이터는 세 가지입니다: 직원 기본 정보, 연차 신청 현황, 매출 실적. 각 테이블의 구조와 관계를 파악해야 이후 장에서 MCP Tool을 설계할 때 정확한 질의를 구성할 수 있습니다.

### ER 다이어그램

세 테이블의 관계를 아래 다이어그램으로 먼저 확인하십시오.

```mermaid
flowchart LR
    A["employees\n직원 기본 정보"] -- "1:N" --> B["leaves\n연차 신청 현황"]
    A -- "1:N" --> C["sales\n매출 실적"]
    B -- "employee_id 참조" --> A
    C -- "employee_id 참조" --> A
```

*그림 4-2: 세 테이블의 관계 (employees 중심의 1:N 구조)*

`employees` 테이블이 중심입니다. `leaves`와 `sales` 모두 `employee_id` 외래키로 직원 정보를 참조합니다.

<!-- [IMAGE PLACEHOLDER: 04_er-diagram — employees, leaves, sales 세 테이블의 컬럼과 관계를 보여주는 ER 다이어그램] -->
*그림 4-3: ER 다이어그램 — 컬럼 상세 포함*

### DDL 분석

`init/01_schema_and_data.sql` 파일에서 세 테이블의 DDL을 살펴봅니다.

**employees 테이블 — 직원 기본 정보**

```sql
CREATE TABLE IF NOT EXISTS employees (
    id                SERIAL PRIMARY KEY,
    name              VARCHAR(100) NOT NULL,
    department        VARCHAR(100),
    annual_leave_days INTEGER DEFAULT 15,
    used_leave_days   INTEGER DEFAULT 0
);
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 직원 이름, 소속 부서
2. **처리(Process)**: `SERIAL` 타입으로 `id`가 자동 증가합니다. 잔여 연차는 `annual_leave_days - used_leave_days`로 계산합니다. 별도의 잔여 연차 컬럼을 두지 않고 계산으로 처리하므로 데이터 불일치가 발생하지 않습니다.
3. **출력(Output)**: 직원 1건 레코드

설계 포인트: 잔여 연차를 별도 컬럼으로 저장하지 않는 이유는 `annual_leave_days`나 `used_leave_days`가 변경될 때마다 세 컬럼을 동시에 업데이트해야 하는 번거로움과 불일치 위험을 없애기 위해서입니다.

**leaves 테이블 — 연차 신청 현황**

```sql
CREATE TABLE IF NOT EXISTS leaves (
    id          SERIAL PRIMARY KEY,
    employee_id INTEGER     REFERENCES employees(id),
    start_date  DATE,
    end_date    DATE,
    reason      TEXT,
    status      VARCHAR(20) DEFAULT 'pending'
);
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 직원 ID, 연차 시작일, 종료일, 신청 사유
2. **처리(Process)**: `status` 컬럼은 세 가지 값을 가집니다 — `pending`(대기), `approved`(승인), `rejected`(반려). 신청 시 자동으로 `pending` 상태가 됩니다.
3. **출력(Output)**: 연차 신청 레코드 1건

**sales 테이블 — 매출 실적**

```sql
CREATE TABLE IF NOT EXISTS sales (
    id          SERIAL PRIMARY KEY,
    employee_id INTEGER        REFERENCES employees(id),
    department  VARCHAR(100),
    amount      DECIMAL(12, 2),
    sale_date   DATE,
    quarter     VARCHAR(10)
);
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 직원 ID, 부서명, 매출 금액, 발생일
2. **처리(Process)**: `department` 컬럼이 `employees.department`와 중복됩니다. 이는 집계 쿼리 시 JOIN 없이 빠르게 `GROUP BY department`를 실행하기 위한 의도적인 비정규화입니다. `quarter` 컬럼은 `'2024-Q4'` 형식으로 분기별 집계를 용이하게 합니다.
3. **출력(Output)**: 매출 실적 레코드 1건

### 샘플 데이터 구성

실습에 사용하는 샘플 데이터는 현실감 있는 시나리오를 위해 아래와 같이 구성되어 있습니다.

| 구분 | 데이터 수 | 설명 |
|------|---------|------|
| 직원 | 5명 | 영업부 2명, 인사부 1명, 개발부 1명, 마케팅부 1명 |
| 연차 신청 | 10건 | 승인 7건, 대기 2건, 반려 1건 |
| 매출 기록 | 20건 | 2024-Q4, 2025-Q1, 2025-Q2 3개 분기 |

직원 5명의 잔여 연차는 다음과 같습니다.

| 직원 | 부서 | 연차 부여 | 연차 사용 | 잔여 |
|------|------|---------|---------|------|
| 김철수 | 영업부 | 15일 | 10일 | **5일** |
| 이영희 | 인사부 | 15일 | 8일 | 7일 |
| 박민준 | 개발부 | 15일 | 0일 | 15일 |
| 최수정 | 마케팅부 | 15일 | 5일 | 10일 |
| 정대현 | 영업부 | 15일 | 3일 | 12일 |

1장에서 등장했던 "김철수 씨의 남은 연차는 며칠인가요?"라는 질문의 답이 이 테이블에 있습니다. 이 데이터를 LLM이 조회할 수 있게 만드는 것이 8장 MCP 구현의 목표입니다.

---

## 4.3 CRUD API 구조 이해

### FastAPI 앱 구조

`app/main.py`는 FastAPI 애플리케이션의 진입점입니다.

```python
from fastapi import FastAPI
from app.routers import employees, leaves, sales

app = FastAPI(
    title="RAG 기반 AI 업무 비서 — 베이스 CRUD API",
    description=(
        "직원(employees), 연차(leaves), 매출(sales) 데이터를 "
        "조회·생성·수정하는 REST API를 제공합니다."
    ),
    version="1.0.0",
)

app.include_router(employees.router)
app.include_router(leaves.router)
app.include_router(sales.router)
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 세 도메인 라우터 모듈 (`employees`, `leaves`, `sales`)
2. **처리(Process)**: `include_router()`로 각 라우터를 앱에 등록합니다. 각 라우터는 자체 `prefix`와 `tags`를 가지므로 Swagger UI에서 도메인별로 그룹화됩니다.
3. **출력(Output)**: 포트 8000에서 전체 엔드포인트가 활성화된 FastAPI 앱

전체 소스 코드는 GitHub 레포를 참고하십시오.

### 엔드포인트 목록

이 API가 제공하는 10개 엔드포인트는 다음과 같습니다.

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/` | 서버 상태 확인 |
| GET | `/health` | 헬스체크 |
| GET | `/employees` | 직원 전체 조회 |
| GET | `/employees/{id}` | 직원 단건 조회 |
| GET | `/employees/{id}/leave-balance` | 직원 잔여 연차 조회 |
| GET | `/leaves` | 연차 전체 조회 |
| POST | `/leaves` | 연차 신청 |
| PUT | `/leaves/{id}/status` | 연차 승인/반려 |
| GET | `/sales` | 매출 전체 조회 |
| GET | `/sales/summary` | 부서별/분기별 매출 합계 |

이 중에서 `/employees/{id}/leave-balance`와 `/sales/summary` 두 엔드포인트는 8장에서 MCP Tool이 호출하는 핵심 API입니다. "김철수의 잔여 연차"와 "영업부 2025-Q1 매출 합계"를 조회하는 데 직접 사용됩니다.

### 핵심 엔드포인트 코드 분석

`/employees/{id}/leave-balance` 엔드포인트를 살펴봅니다.

```python
@router.get(
    "/{employee_id}/leave-balance",
    response_model=LeaveBalanceResponse,
    summary="직원 잔여 연차 조회",
)
def get_leave_balance(
    employee_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> LeaveBalanceResponse:
    # --- Input ---
    # employee_id: URL 경로에서 추출된 직원 식별자

    # --- Process ---
    employee: Employee = _get_employee_or_404(employee_id, db)
    remaining_days: int = employee.annual_leave_days - employee.used_leave_days

    # --- Output ---
    return LeaveBalanceResponse(
        employee_id=employee.id,
        name=employee.name,
        annual_leave_days=employee.annual_leave_days,
        used_leave_days=employee.used_leave_days,
        remaining_days=remaining_days,
    )
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: URL 경로 파라미터 `employee_id` (정수)
2. **처리(Process)**: `_get_employee_or_404()` 헬퍼 함수로 직원을 조회하고, 없으면 HTTP 404를 반환합니다. 잔여 연차는 `annual_leave_days - used_leave_days`로 계산합니다.
3. **출력(Output)**: `LeaveBalanceResponse` Pydantic 스키마로 직렬화된 JSON

`/sales/summary` 엔드포인트도 확인합니다.

```python
@router.get("/summary", summary="부서별/분기별 매출 합계 조회")
def get_sales_summary(
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    # --- Input ---
    # 파라미터 없음 — 전체 매출 집계 조회

    # --- Process ---
    rows = (
        db.query(
            Sale.department,
            Sale.quarter,
            func.sum(Sale.amount).label("total_amount"),
        )
        .group_by(Sale.department, Sale.quarter)
        .order_by(Sale.department, Sale.quarter)
        .all()
    )

    summary: list[dict] = [
        {
            "department": row.department,
            "quarter": row.quarter,
            "total_amount": float(row.total_amount),
        }
        for row in rows
    ]

    # --- Output ---
    return {"결과": summary}
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 없음 (전체 매출 데이터 집계)
2. **처리(Process)**: SQLAlchemy `func.sum()`으로 `department`와 `quarter` 기준 GROUP BY 집계를 수행합니다. `Decimal` 타입은 JSON 직렬화를 위해 `float`으로 변환합니다.
3. **출력(Output)**: `{"결과": [...]}` 형식의 딕셔너리 — 부서별 분기별 매출 합계 목록

전체 소스 코드는 GitHub 레포를 참고하십시오.

### Swagger UI에서 API 테스트

브라우저에서 아래 주소로 접속하면 Swagger UI를 통해 모든 엔드포인트를 직접 테스트할 수 있습니다.

```
http://localhost:8000/docs
```

<!-- [CAPTURE NEEDED: 04_swagger-ui — 브라우저에서 localhost:8000/docs 를 열었을 때의 Swagger UI 전체 화면 (세 도메인 그룹이 모두 표시된 상태)] -->
*그림 4-4: Swagger UI — 세 도메인(employees, leaves, sales)의 엔드포인트 목록*

### curl / PowerShell로 API 동작 확인

터미널에서 직접 API를 호출하여 샘플 데이터가 정상적으로 반환되는지 확인합니다.

**macOS / Linux**

```bash
# 직원 전체 조회
curl http://localhost:8000/employees

# 김철수(id=1)의 잔여 연차 조회
curl http://localhost:8000/employees/1/leave-balance

# 부서별 분기별 매출 합계
curl http://localhost:8000/sales/summary
```

**Windows (PowerShell)**

```powershell
# 직원 전체 조회
Invoke-RestMethod -Uri "http://localhost:8000/employees"

# 김철수(id=1)의 잔여 연차 조회
Invoke-RestMethod -Uri "http://localhost:8000/employees/1/leave-balance"

# 부서별 분기별 매출 합계
Invoke-RestMethod -Uri "http://localhost:8000/sales/summary"
```

`GET /employees/1/leave-balance` 호출의 예상 응답입니다.

```json
{
  "employee_id": 1,
  "name": "김철수",
  "annual_leave_days": 15,
  "used_leave_days": 10,
  "remaining_days": 5
}
```

`GET /sales/summary` 호출의 예상 응답입니다.

```json
{
  "결과": [
    {"department": "개발부", "quarter": "2025-Q2", "total_amount": 7700000.0},
    {"department": "마케팅부", "quarter": "2024-Q4", "total_amount": 24600000.0},
    {"department": "마케팅부", "quarter": "2025-Q1", "total_amount": 25300000.0},
    {"department": "영업부", "quarter": "2024-Q4", "total_amount": 15800000.0},
    {"department": "영업부", "quarter": "2025-Q1", "total_amount": 14000000.0},
    {"department": "영업부", "quarter": "2025-Q2", "total_amount": 5600000.0},
    {"department": "인사부", "quarter": "2025-Q2", "total_amount": 2700000.0}
  ]
}
```

<!-- [CAPTURE NEEDED: 04_curl-leave-balance — curl http://localhost:8000/employees/1/leave-balance 실행 후 터미널 출력 (JSON 응답 전체)] -->
*그림 4-5: 잔여 연차 조회 API 응답 결과*

> **팁: ORM 계층의 역할**
> `database.py` → `models.py` → `schemas.py`의 3단 계층 구조에 주목하십시오. `database.py`가 SQLAlchemy 엔진과 세션을 관리하고, `models.py`가 테이블과 1:1 대응하는 ORM 클래스를 정의하며, `schemas.py`의 Pydantic 모델이 API 요청/응답을 직렬화합니다. 이 구조 덕분에 SQL 쿼리를 직접 작성하지 않고도 Python 객체로 DB를 조작할 수 있습니다.

### 자주 발생하는 오류 대응

| 오류 메시지 | 원인 | 해결 방법 |
|-----------|------|---------|
| `connection refused` | 컨테이너가 아직 시작 중 | `docker-compose ps` 확인 후 30초 대기 |
| `Address already in use` | 5432 또는 8000 포트 충돌 | `.env`에서 `POSTGRES_PORT` 변경, 기존 프로세스 종료 |
| `fastapi` 컨테이너만 Exited | DB 연결 실패 | `docker-compose logs fastapi`로 오류 확인 |
| 데이터 초기화 필요 | 테이블/데이터 오염 | `docker-compose down -v && docker-compose up -d` 실행 |

> **경고: docker-compose down -v는 모든 데이터를 삭제합니다.**
> `-v` 옵션을 사용하면 PostgreSQL 볼륨이 삭제되어 이후 챕터에서 저장한 데이터도 모두 사라집니다. 데이터를 초기 상태로 되돌려야 하는 명확한 이유가 없다면 `-v` 없이 `docker-compose down`만 사용하십시오.

---

## 4.4 MCP 개념 소개

인프라가 준비되었습니다. 이 절에서는 이 인프라가 8장에서 어떤 방식으로 LLM에 연결되는지 개념을 미리 살펴봅니다.

### LLM은 왜 DB를 직접 조회하지 못하는가

LLM은 텍스트 입력을 받아 텍스트를 출력하는 모델입니다. PostgreSQL에 직접 연결하거나 SQL 쿼리를 실행하는 기능이 없습니다. LLM이 "김철수의 잔여 연차"를 알려면 누군가가 DB를 조회하여 결과를 LLM에게 전달해야 합니다.

3장에서 Context Injection을 통해 문서 내용을 프롬프트에 직접 넣어 응답을 개선했던 것을 기억하십시오. 정형 데이터도 같은 방식으로 처리할 수 있습니다. 그런데 "누군가"가 데이터를 가져오는 역할을 코드로 어떻게 구현하고, LLM이 그 코드를 언제 어떻게 호출하도록 만들 것인가의 문제가 남습니다. 이 문제를 해결하는 표준 방법이 **MCP(Model Context Protocol)** 입니다.

### MCP의 정의

**MCP(Model Context Protocol)** 는 LLM이 외부 도구(데이터베이스, API, 파일 시스템 등)를 표준화된 프로토콜로 호출하기 위해 Anthropic이 제안한 오픈 프로토콜입니다. MCP를 사용하면 LLM은 어떤 외부 시스템이든 동일한 방식으로 호출할 수 있습니다.

간단하게 비유하면, MCP는 LLM과 외부 시스템 사이의 "표준 플러그와 소켓"입니다. 전자 기기가 콘센트 규격에만 맞으면 어느 나라 제품이든 연결할 수 있듯이, MCP 규격에 맞춰 만든 도구는 어느 LLM에서든 호출할 수 있습니다.

```mermaid
flowchart TD
    A["사용자 질문"] --> B["LLM"]
    B -- "도구 호출 요청" --> C["MCP 서버"]
    C -- "DB 조회" --> D["PostgreSQL"]
    D -- "조회 결과" --> C
    C -- "도구 응답" --> B
    B --> E["최종 답변"]
```

*그림 4-6: MCP를 통한 LLM-DB 연결 흐름*

### LangChain Tool과 MCP의 차이

MCP를 이해하기 위해 기존 방식인 **LangChain Tool** 과 비교해 보겠습니다.

| 항목 | LangChain Tool | MCP |
|------|--------------|-----|
| 구현 방식 | Python 함수로 직접 구현 | 표준 프로토콜로 서버 구현 |
| 종속성 | LangChain에 종속 | 언어·프레임워크 독립 |
| 배포 | 동일 프로세스 내 실행 | 별도 서버 프로세스 |
| 재사용성 | 해당 Python 코드에서만 사용 | 다른 AI 클라이언트에서도 사용 가능 |
| 사용 시점 | 빠른 프로토타입 | 운영 수준 표준화 |

LangChain Tool은 Python 함수를 `@tool` 데코레이터로 감싸는 방식이므로 빠르게 구현할 수 있지만 LangChain에 종속됩니다. MCP는 JSON-RPC 기반 프로토콜로 서버를 구현하므로 Claude, GPT, LangChain 등 어느 클라이언트에서도 동일하게 호출할 수 있습니다.

<!-- [IMAGE PLACEHOLDER: 04_mcp-vs-tool — LangChain Tool(Python 직접 호출)과 MCP(프로토콜 서버 경유)의 차이를 보여주는 비교 다이어그램] -->
*그림 4-7: LangChain Tool vs MCP — 아키텍처 비교*

### 이 인프라가 MCP에서 하는 역할

8장에서 구현할 MCP 서버는 이 장에서 확보한 FastAPI 엔드포인트를 호출합니다. MCP Tool의 `get_leave_balance` 도구는 `GET /employees/{id}/leave-balance`를 호출하고, `get_sales_summary` 도구는 `GET /sales/summary`를 호출합니다.

따라서 이 장에서 API 엔드포인트의 요청/응답 구조를 정확히 파악해 두는 것이 중요합니다. MCP Tool을 설계할 때 입력 파라미터와 출력 형식이 API 명세와 일치해야 합니다.

```mermaid
flowchart LR
    A["8장 MCP Tool"] -- "HTTP 호출" --> B["4장 FastAPI"]
    B -- "SQL 쿼리" --> C["PostgreSQL"]
    C -- "결과 반환" --> B
    B -- "JSON 응답" --> A
```

*그림 4-8: 4장 인프라와 8장 MCP Tool의 연결 구조*

> **참고: 이 책에서 MCP 서버는 FastMCP로 구현합니다.**
> 8장에서 `fastmcp` 라이브러리를 사용하여 `@mcp.tool()` 데코레이터 방식으로 MCP 서버를 구현합니다. 지금은 "LLM이 외부 API를 표준 방식으로 호출하는 메커니즘"이라는 개념적 이해로 충분합니다.

---

## 4.5 정리하며

이 장에서는 RAG + MCP 시스템의 기반이 되는 인프라를 확보했습니다.

- **Docker Compose 한 명령으로 인프라 구동**: `docker-compose up -d` 한 번으로 PostgreSQL 16과 FastAPI 서버가 동시에 구동됩니다. `depends_on`의 `condition: service_healthy`로 DB가 준비된 후에만 API 서버가 시작되도록 의존성 순서를 제어합니다.

- **세 테이블의 스키마와 관계 파악**: `employees` 테이블이 중심이며, `leaves`와 `sales`가 `employee_id` 외래키로 참조하는 1:N 구조입니다. 잔여 연차를 계산 컬럼이 아닌 API 레이어에서 처리하는 설계 의도를 이해했습니다.

- **10개 CRUD 엔드포인트 확인**: Swagger UI(`localhost:8000/docs`)와 curl로 전체 엔드포인트를 직접 테스트했습니다. `/employees/{id}/leave-balance`와 `/sales/summary`가 8장 MCP Tool의 주요 호출 대상임을 파악했습니다.

- **MCP 개념 기초 이해**: MCP는 LLM이 외부 도구를 표준 프로토콜로 호출하는 방식입니다. LangChain Tool이 Python 코드에 종속되는 것과 달리 MCP는 언어·프레임워크에 독립적으로 재사용 가능합니다.

다음 장에서는 RAG 파이프라인의 입력이 되는 사내 문서를 표준화합니다. RAG의 검색 품질은 문서 전처리 수준에 크게 좌우됩니다. "쓰레기가 들어가면 쓰레기가 나온다(GIGO)"는 원칙에 따라 수집 전략, 정규화 규칙, 메타데이터 스키마를 체계적으로 설계합니다.



---

# 5. 사내 문서 표준화

4장에서 PostgreSQL과 FastAPI로 구성된 사내 인프라를 확보했습니다. 이제 RAG 시스템에 입력할 문서를 준비해야 합니다. 이 장에서는 **문서 표준화** 파이프라인을 학습합니다. 수집 전략부터 전처리 규칙, 네이밍 표준, 메타데이터 스키마 설계까지 RAG 검색 품질을 결정하는 기준을 수립합니다.

<!-- [IMAGE PLACEHOLDER: 05_chapter_overview — 사내 문서(PDF/Word/HWP)가 표준화 파이프라인을 거쳐 벡터 DB 입력용 정제 문서로 변환되는 흐름 개요] -->
*그림 5-1: 문서 표준화 파이프라인 전체 개요*

---

## 1. RAG 검색 품질을 결정하는 문서 기준

### 1.1 GIGO 원칙

RAG 시스템의 성능은 **LLM 모델 선택보다 입력 문서의 품질에 더 크게 좌우**됩니다. 컴퓨터 과학에서 오래전부터 전해 내려오는 원칙이 있습니다.

> **GIGO(Garbage In, Garbage Out)** — 쓰레기가 들어가면 쓰레기가 나온다.

LLM이 아무리 뛰어나도 엉망인 문서를 넣으면 엉망인 답변이 나옵니다. 반대로 잘 정제된 문서를 입력하면 작은 모델도 정확한 답변을 생성합니다.

아래 두 가지 예시를 비교해 보십시오.

**문서 A (표준화 전)**
```
사내 인사 규정 | 대외비 | 2024.01

제10조 (연차 유급휴가  부여 기준)

①  1년간  80% 이상  출근한 직원에게는   15일의
   유급휴가를  부여한다.

- 1 -

사내 인사 규정 | 대외비 | 2024.01
```

**문서 B (표준화 후)**
```markdown
## 제10조 (연차 유급휴가 부여 기준)

① 1년간 80% 이상 출근한 직원에게는 15일의 유급휴가를 부여한다.
```

문서 A에는 헤더(`사내 인사 규정 | 대외비 | 2024.01`)가 반복되고, 페이지 번호(`- 1 -`)가 섞여 있으며, 과도한 공백이 텍스트를 분열시킵니다. 이 상태로 벡터 DB에 저장하면 검색 엔진은 핵심 정보보다 헤더와 페이지 번호를 더 많이 학습하게 됩니다.

### 1.2 문서 표준화를 별도 챕터로 다루는 이유

6장(벡터 DB 구축)에서 바로 코드 구현으로 들어가면 다음 질문에 답하지 못합니다.

- "어떤 문서를 넣어야 하는가?"
- "PDF와 Word 중 어느 쪽이 더 정확하게 추출되는가?"
- "파일명은 어떤 규칙으로 지어야 나중에 메타데이터로 활용할 수 있는가?"

이 질문에 답하지 못한 채 코드를 작성하면 나중에 검색 결과가 엉망이 되었을 때 원인을 찾기 어렵습니다. 5장은 6장의 전처리 파이프라인이 올바르게 동작하기 위한 **기준을 사전에 확립**하는 챕터입니다.

```mermaid
flowchart LR
    A["사내 문서 수집"] -- "전처리/정규화" --> B["정제된 텍스트"]
    B -- "메타데이터 부착" --> C["표준화된 문서"]
    C -- "6장에서 사용" --> D["벡터 DB 저장"]
```

*그림 5-2: 문서 표준화 흐름 — 5장에서 기준을 수립하고 6장에서 코드로 구현한다*

---

## 2. PDF, Word, Markdown, HWP 수집 전략

### 2.1 문서 유형별 수집 우선순위 매트릭스

사내에 흩어진 문서는 형식이 제각각입니다. 어떤 형식을 어떤 방법으로 수집해야 효율적인지 아래 매트릭스로 정리합니다. 이 기준은 `guides/collection_strategy.md`에 전체 내용이 담겨 있습니다.

| 유형 | 우선순위 | 수집 방법 | 전처리 난이도 | 권장 라이브러리 |
|------|---------|---------|------------|--------------|
| PDF (텍스트 레이어 있음) | 높음 | PyMuPDF | 낮음 | `pymupdf` |
| Word (.docx) | 높음 | python-docx | 낮음 | `python-docx` |
| Markdown | 높음 | 직접 읽기 | 없음 | 표준 라이브러리 |
| HWP / HWPX | 중간 | PDF 변환 후 PDF 파이프라인 위임 | 낮음 (변환 후) | `subprocess` + LibreOffice |
| 스캔 PDF (이미지) | 낮음 | OCR (10장 참조) | 높음 | `easyocr`, `llava` |
| Excel | 중간 | openpyxl | 중간 | `openpyxl`, `pandas` |

**판단 기준**: 동일한 업무 가치가 있는 문서라면, 전처리 난이도가 낮은 유형부터 수집하십시오. 스캔 PDF는 OCR 오류율이 높으므로, 같은 내용의 디지털 원본이 있다면 원본을 우선 사용하십시오.

### 2.2 규칙 기반 파싱 vs AI 기반 파싱

문서 추출 방법은 크게 두 가지로 나뉩니다.

**규칙 기반 파싱(Rule-based Parsing)** 은 `pdfplumber`, `python-docx` 같은 라이브러리가 텍스트 구조를 좌표·스타일 기반으로 추출하는 방식입니다. 빠르고 저렴하며 재현 가능합니다. 디지털 원본 PDF와 Word 문서 대부분이 여기에 해당합니다.

**AI 기반 파싱(Vision LLM)** 은 PDF 페이지를 이미지로 변환하여 멀티모달 LLM이 시각적으로 이해하고 텍스트를 생성하는 방식입니다. 복잡한 다단 레이아웃, 표가 뒤섞인 도해, 스캔 PDF처럼 규칙 기반이 실패하는 케이스에서 사용합니다.

> **팁: AI 기반 파싱은 최후 수단으로 사용하십시오**
> Vision LLM은 규칙 기반보다 처리 시간이 10배 이상 느리고 GPU 리소스를 대량 소비합니다. 먼저 규칙 기반으로 시도하고, 추출 결과가 깨진 경우에만 Vision LLM으로 전환하는 전략이 효율적입니다. 6장에서 이 판단 로직(`is_complex_layout()`)을 직접 구현합니다.

### 2.3 HWP 처리 전략

국내 공공기관과 기업에서 HWP(한컴 한글) 형식이 광범위하게 사용됩니다. HWP 처리 방법은 세 가지가 있습니다.

| 방법 | 도구 | 장점 | 단점 |
|------|------|------|------|
| A. pyhwp | `pip install pyhwp` | 설치 간단 | HWP 5.x만 지원, 표·이미지 추출 불가 |
| B. LibreOffice → DOCX | `libreoffice --convert-to docx` | HWPX 포함, 표 추출 가능 | 복잡한 레이아웃에서 표가 깨짐 |
| C. PDF로 변환 후 PDF 파이프라인 위임 | `libreoffice --convert-to pdf` | 레이아웃 보존, 이후 처리 통일 | LibreOffice 설치 필요 |

이 책에서는 **방법 C** 를 사용합니다. HWP를 PDF로 변환하면 이후 처리는 일반 PDF와 완전히 동일하기 때문입니다. 어떤 도구(한컴오피스, LibreOffice, 클라우드 변환기)로 PDF를 만들든 상관없습니다.

```
HWP 파일
    ↓  LibreOffice (또는 한컴오피스에서 직접 PDF 저장)
PDF 파일  →  CH06 extractor.py (pdfplumber / Vision LLM)  →  Markdown
```

다음은 LibreOffice를 사용하여 HWP 파일을 자동으로 PDF로 변환하는 핵심 코드입니다. 전체 코드는 `guides/collection_strategy.md`를 참고하십시오.

```python
import subprocess
from pathlib import Path

def hwp_to_pdf(hwp_path: str, output_dir: str = ".") -> str:
    """
    LibreOffice headless로 HWP/HWPX를 PDF로 변환합니다.
    사전 조건: brew install libreoffice 또는 apt install libreoffice

    Args:
        hwp_path  : .hwp 또는 .hwpx 파일 경로
        output_dir: PDF 저장 디렉토리

    Returns:
        생성된 PDF 파일 경로 (이후 CH06 파이프라인에 그대로 전달)
    """
    # --- Input ---
    result = subprocess.run(
        ["libreoffice", "--headless", "--convert-to", "pdf",
         "--outdir", output_dir, hwp_path],
        capture_output=True, text=True,
    )

    # --- Process ---
    if result.returncode != 0:
        raise RuntimeError(f"LibreOffice 변환 실패: {result.stderr}")

    # --- Output ---
    pdf_path = str(Path(output_dir) / f"{Path(hwp_path).stem}.pdf")
    return pdf_path
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: HWP 또는 HWPX 파일 경로와 PDF 저장 디렉토리
2. **처리(Process)**: LibreOffice headless 모드로 HWP를 PDF로 변환하고, 변환 실패 시 RuntimeError 발생
3. **출력(Output)**: 변환된 PDF 파일 경로 — 이 경로를 6장 `extractor.py`에 그대로 전달하십시오

### 2.4 수집 우선순위 결정 흐름

```mermaid
flowchart TD
    A["사내 문서 목록 확보"] --> B{"디지털 원본이 있는가?"}
    B -- "없음" --> C["스캔본 → 10장 OCR 참조"]
    B -- "있음" --> D{"파일 형식 확인"}
    D -- "PDF" --> E{"텍스트 레이어 있음?"}
    D -- "Word / Markdown / Excel" --> F["규칙 기반 파싱 적용"]
    D -- "HWP / HWPX" --> G["PDF로 변환 후 PDF 파이프라인"]
    E -- "있음" --> F
    E -- "없음(스캔)" --> C
```

*그림 5-3: 문서 유형별 수집 방법 결정 흐름도*

> **주의: 스캔 PDF 우선순위를 높이지 마십시오**
> 스캔 PDF는 OCR 오류율이 높아 전처리 부담이 큽니다. 같은 내용의 디지털 원본(Word, 텍스트 레이어 PDF)이 존재한다면 반드시 디지털 원본을 먼저 수집하십시오. 스캔본은 원본이 없을 때만 사용하십시오.

---

## 3. 문서 전처리 및 정규화 가이드라인

### 3.1 전처리 규칙 표

수집된 문서를 그대로 벡터 DB에 넣으면 헤더·푸터·과도한 공백이 검색 품질을 떨어뜨립니다. 아래 규칙 표를 기준으로 모든 문서에 동일한 전처리를 적용하십시오. 이 규칙의 전체 내용은 `guides/preprocessing_rules.md`에 정의되어 있습니다.

| 항목 | 처리 방법 | 예시 |
|------|---------|------|
| 헤더/푸터 제거 | 정규식으로 페이지 번호, 문서명 반복 패턴 제거 | `"- 3 -"` → 삭제 |
| 인코딩 통일 | UTF-8 강제 변환 | EUC-KR → UTF-8 |
| 과도한 공백 | 2개 이상 연속 공백 → 단일 공백 | `"연차  규정"` → `"연차 규정"` |
| 중복 개행 | 3개 이상 연속 개행 → 최대 2개 | `"\n\n\n\n"` → `"\n\n"` |
| 표/이미지 | 표: 셀 내용 유지 / 이미지: 10장 OCR 참조 | `"항목 | 값"` 형식 유지 |
| 선행/후행 공백 | 각 줄의 시작·끝 공백 제거 | `"  제1조  "` → `"제1조"` |
| 특수문자 정규화 | 전각 문자 → 반각, 불필요한 특수문자 제거 | `"∙"` → `"-"` |

### 3.2 전처리 전/후 비교

1절에서 잠깐 보여준 비교를 더 상세히 살펴보겠습니다. `data/sample_raw/hr_policy_raw.txt`와 `data/sample_clean/HR_취업규칙_v1.0.md`를 나란히 비교하면 전처리 효과를 직접 확인할 수 있습니다.

**전처리 전 (sample_raw/hr_policy_raw.txt)**

```text
사내 인사 규정 | 대외비 | 2024.01


제1조 (목적)

본 규정은  주식회사 테크노바  (이하 "회사")의  임직원 인사 관리에 관한 기준을
정함으로써  조직의 효율적 운영과  구성원의 권익 보호를  목적으로 한다.


- 1 -


제2장 연차 유급휴가


제10조 (연차 유급휴가 부여 기준)

①  1년간 80% 이상 출근한 직원에게는  15일의 유급휴가를  부여한다.
```

**전처리 후 (sample_clean/HR_취업규칙_v1.0.md)**

```markdown
## 제1조 (목적)

본 규정은 주식회사 테크노바(이하 "회사")의 임직원 인사 관리에 관한 기준을
정함으로써 조직의 효율적 운영과 구성원의 권익 보호를 목적으로 한다.

---

## 제2장 연차 유급휴가

### 제10조 (연차 유급휴가 부여 기준)

① 1년간 80% 이상 출근한 직원에게는 15일의 유급휴가를 부여한다.
```

전처리를 거치면 아래 세 가지가 달라집니다.

1. **헤더/푸터 제거**: `사내 인사 규정 | 대외비 | 2024.01`과 `- 1 -` 같은 반복 패턴이 제거됩니다.
2. **공백 정규화**: 조문 사이에 흩어진 과도한 공백이 단일 공백으로 정리됩니다.
3. **Markdown 변환**: `제2장`, `제10조`가 `##`, `###` 헤더로 변환되어 청킹 기준점이 됩니다.

터미널에서 아래 명령어를 실행하면 원본과 정제본의 차이를 직접 확인할 수 있습니다.

```bash
diff data/sample_raw/hr_policy_raw.txt "data/sample_clean/HR_취업규칙_v1.0.md"
```

`-`로 시작하는 줄은 원본에서 제거된 내용(헤더·푸터·과도한 공백)이고, `+`로 시작하는 줄은 정제본에 추가된 내용(Markdown 헤더 기호)입니다.

### 3.3 최종 출력을 Markdown으로 통일하는 이유

전처리의 최종 출력 형식을 **Markdown** 으로 통일하는 이유는 세 가지입니다.

첫째, **토큰 효율**: HTML과 비교하면 Markdown은 태그가 훨씬 적습니다. `<h2>제목</h2>` 대신 `## 제목`으로 충분하기 때문에 LLM에게 전달되는 토큰 수가 줄어듭니다.

둘째, **LLM 이해도**: LLM은 GitHub, Stack Overflow 등의 인터넷 데이터로 학습되었습니다. `#` 헤더, `|` 표, `- ` 목록 기호를 네이티브로 이해합니다. HTML보다 훨씬 자연스럽게 구조를 파악합니다.

셋째, **청킹 기준점**: 6장에서 문서를 청크로 분할할 때 `#` 헤더를 기준점으로 사용합니다. `## 제2장 연차 유급휴가`와 `## 제3장 정보 보안 규정`은 의미적으로 완전히 다른 내용이므로 헤더를 경계로 분리하면 청크 품질이 높아집니다.

> **참고: 전처리 파이프라인 적용 순서**
> 전처리 함수를 적용할 때는 순서가 중요합니다. `preprocessing_rules.md`에 명시된 권장 순서는 ① 특수문자 정규화 → ② 헤더/푸터 제거 → ③ 공백 정규화입니다. 공백 정규화를 먼저 하면 헤더/푸터 패턴을 인식하기 어려울 수 있으므로 반드시 마지막에 수행하십시오.

---

## 4. 사내 문서 네이밍 표준 규칙

### 4.1 네이밍 포맷 정의

파일명 규칙이 없으면 RAG 시스템이 문서를 구분할 수 없습니다. `2025년본.pdf`, `최종수정(진짜최종).xlsx` 같은 파일이 그대로 들어가면 메타데이터가 꼬여 검색 품질이 크게 저하됩니다. 이 책에서 사용하는 네이밍 표준(Naming Convention)은 다음과 같습니다.

```
{부서}_{문서명}_{버전}.확장자
```

| 구성 요소 | 형식 | 예시 |
|----------|------|------|
| 부서 | 영문 약어 대문자 | `HR`, `FIN`, `SEC`, `OPS`, `DEV` |
| 문서명 | 한글 또는 영문, 공백 없이 | `취업규칙`, `예산기안서`, `보안규정` |
| 버전 | `v{major}.{minor}` | `v1.0`, `v2.1`, `v3.0` |
| 확장자 | 원본 형식 그대로 | `.pdf`, `.docx`, `.xlsx`, `.md` |

### 4.2 잘못된 사례 vs 올바른 사례

| 잘못된 사례 | 올바른 사례 | 개선 이유 |
|------------|------------|---------|
| `2025년본.pdf` | `HR_취업규칙_v1.0.pdf` | 부서·문서명·버전 모두 불명확 |
| `최종수정(진짜최종).xlsx` | `FIN_부서별예산기안서_v3.2.xlsx` | 특수문자, 버전 추적 불가 |
| `보안규정.docx` | `SEC_보안규정_v1.0.docx` | 부서 정보 없음 |
| `신규서비스런칭전략.pdf` | `OPS_신규서비스런칭전략_v1.0.pdf` | 부서 정보 없음 |
| `HR규정(수정중).pdf` | `HR_취업규칙_v2.0.pdf` | 괄호·한글 상태 표시 금지 |
| `연차규정final.pdf` | `HR_연차규정_v1.1.pdf` | `final` 대신 버전 번호 사용 |

### 4.3 부서별 폴더 구조

파일명뿐 아니라 폴더도 부서별로 분리합니다. 폴더명 자체가 메타데이터입니다.

```
data/docs/
├── hr/               ← HR 부서 문서
│   ├── HR_취업규칙_v1.0.pdf
│   └── HR_연차규정_v2.1.pdf
├── finance/          ← Finance 부서 문서
│   ├── FIN_부서별예산기안서_v3.2.xlsx
│   └── FIN_2024상반기매출현황_v1.0.pdf
├── ops/              ← Operations 부서 문서
│   └── OPS_신규서비스런칭전략_v1.0.pdf
└── security/         ← Security 부서 문서
    └── SEC_보안규정_v1.0.docx
```

### 4.4 네이밍 규칙이 메타데이터로 연결되는 원리

네이밍 규칙을 따르면 코드 한 줄로 메타데이터를 자동 추출할 수 있습니다. 6장에서 이 함수가 `extractor.py`에 그대로 이식됩니다.

```python
from pathlib import Path

def parse_filename_metadata(filename: str) -> dict:
    """
    네이밍 규칙 {부서}_{문서명}_{버전}.확장자에서 메타데이터를 자동 추출합니다.

    Args:
        filename: 파일명 (경로 포함 가능)

    Returns:
        {"department": str, "doc_name": str, "version": str, "source": str}

    Example:
        >>> parse_filename_metadata("HR_취업규칙_v1.0.pdf")
        {"department": "HR", "doc_name": "취업규칙", "version": "v1.0", ...}
    """
    # --- Input ---
    stem = Path(filename).stem        # HR_취업규칙_v1.0

    # --- Process ---
    parts = stem.split("_", 2)        # ["HR", "취업규칙", "v1.0"]

    # --- Output ---
    return {
        "department": parts[0] if len(parts) > 0 else "UNKNOWN",
        "doc_name":   parts[1] if len(parts) > 1 else stem,
        "version":    parts[2] if len(parts) > 2 else "v1.0",
        "source":     Path(filename).name,
    }
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 파일명 문자열 (예: `"HR_취업규칙_v1.0.pdf"`)
2. **처리(Process)**: 파일명에서 확장자를 제거하고 언더스코어(`_`)를 최대 2회 분리하여 부서·문서명·버전 추출
3. **출력(Output)**: `{"department": "HR", "doc_name": "취업규칙", "version": "v1.0", "source": "HR_취업규칙_v1.0.pdf"}` 형태의 딕셔너리

실행 결과를 확인하면 네이밍 규칙이 얼마나 강력한지 알 수 있습니다.

```
HR_취업규칙_v1.0.pdf          → {'department': 'HR', 'doc_name': '취업규칙', 'version': 'v1.0'}
FIN_부서별예산기안서_v3.2.xlsx → {'department': 'FIN', 'doc_name': '부서별예산기안서', 'version': 'v3.2'}
SEC_보안규정_v1.0.docx         → {'department': 'SEC', 'doc_name': '보안규정', 'version': 'v1.0'}
```

파일명 하나로 `department`, `doc_name`, `version` 세 가지 메타데이터가 자동으로 추출됩니다. 사람이 수동으로 입력할 필요가 없습니다.

<!-- [IMAGE PLACEHOLDER: 05_naming_to_metadata — 파일명(HR_취업규칙_v1.0.pdf)이 언더스코어를 기준으로 분리되어 department/doc_name/version 메타데이터 필드로 매핑되는 흐름] -->
*그림 5-4: 네이밍 규칙 → 메타데이터 자동 파싱 흐름*

---

## 5. 메타데이터 스키마 설계

### 5.1 메타데이터가 필요한 이유

**메타데이터(Metadata)** 는 문서 자체가 아닌, 문서에 대한 정보입니다. 작성자, 날짜, 부서, 버전 같은 정보가 이에 해당합니다.

메타데이터 없이 RAG를 구현하면 다음 상황이 발생합니다.

- "HR 부서 문서에서만 검색해 주세요" — 필터링 불가
- "2024년 이후 작성된 문서만 검색해 주세요" — 날짜 필터링 불가
- "이 답변이 어느 문서에서 왔나요?" — 출처 표시 불가 (7장에서 필수)

메타데이터를 설계해 두면 ChromaDB에서 부서별·날짜별 필터 검색이 가능하고, 7장에서 답변과 함께 출처를 표시하는 기능을 구현할 수 있습니다.

### 5.2 메타데이터 스키마 정의

아래 스키마는 `data/metadata_schema.json`에 JSON Schema 형식으로 정의되어 있습니다.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "사내 문서 메타데이터 스키마",
  "type": "object",
  "required": ["doc_id", "source_file", "department", "created_date", "version", "doc_type"],
  "properties": {
    "doc_id": {
      "type": "string",
      "description": "문서 고유 ID (UUID 형식)",
      "example": "doc-2024-hr-001"
    },
    "source_file": {
      "type": "string",
      "description": "원본 파일명 (경로 포함)",
      "example": "hr/HR_연차규정_v2.1.pdf"
    },
    "department": {
      "type": "string",
      "enum": ["HR", "기획", "마케팅", "개발", "재무", "전사"],
      "description": "문서 소유 부서"
    },
    "created_date": {
      "type": "string",
      "format": "date",
      "description": "문서 작성일 (YYYY-MM-DD)",
      "example": "2024-01-15"
    },
    "version": {
      "type": "string",
      "description": "문서 버전",
      "example": "v2.1"
    },
    "doc_type": {
      "type": "string",
      "enum": ["규정", "가이드", "보고서", "공지", "매뉴얼"],
      "description": "문서 유형"
    },
    "tags": {
      "type": "array",
      "items": {"type": "string"},
      "description": "검색 태그 (선택)",
      "example": ["연차", "휴가", "인사"]
    },
    "page_count": {
      "type": "integer",
      "description": "총 페이지 수"
    }
  }
}
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 각 문서에 대한 정보 (파일명, 부서, 날짜 등)
2. **처리(Process)**: JSON Schema가 정의한 `required` 필드를 검증하고, `enum` 값으로 부서·문서 유형의 일관성을 강제
3. **출력(Output)**: 유효성이 검증된 메타데이터 딕셔너리 — 6장 `store.py`의 `add_documents()`에 직접 전달

### 5.3 필드별 역할과 ChromaDB 연결

각 필드가 RAG 파이프라인에서 어떤 역할을 하는지 이해하면 스키마를 더 잘 활용할 수 있습니다.

| 필드 | 역할 | 6~7장 활용 |
|------|------|---------|
| `doc_id` | 문서 식별자, 중복 저장 방지 | ChromaDB의 `ids` 파라미터에 사용 |
| `source_file` | 원본 파일 경로 | 7장 출처 표시에 사용 |
| `department` | 부서 분류 | ChromaDB `where={"department": "HR"}` 필터 |
| `created_date` | 작성 시점 | 날짜 범위 필터 (최신 문서 우선) |
| `version` | 버전 관리 | 구버전 문서 필터링 |
| `doc_type` | 문서 유형 | 규정·가이드·보고서 별도 검색 |
| `tags` | 자유 태그 | 키워드 기반 보조 검색 |

### 5.4 네이밍 규칙 → 메타데이터 자동 파싱 연결

4절의 `parse_filename_metadata()`가 추출한 값이 이 스키마 필드와 어떻게 연결되는지 확인하십시오.

```python
# 파일명에서 메타데이터 자동 추출
meta = parse_filename_metadata("HR_취업규칙_v1.0.pdf")
# → {"department": "HR", "doc_name": "취업규칙", "version": "v1.0"}

# 스키마 필드와 매핑
document_metadata = {
    "doc_id":       "doc-2024-hr-001",       # 별도 생성 (UUID)
    "source_file":  meta["source"],           # "HR_취업규칙_v1.0.pdf"
    "department":   meta["department"],       # "HR" ← 파일명 자동 추출
    "version":      meta["version"],          # "v1.0" ← 파일명 자동 추출
    "created_date": "2024-01-15",            # 별도 입력 필요
    "doc_type":     "규정",                  # 별도 입력 필요
}
```

파일명 네이밍 규칙이 잘 잡혀 있으면 `department`와 `version`은 자동으로 채워집니다. 나머지 필드(`created_date`, `doc_type`)만 사람이 입력하면 됩니다.

6장에서 이 메타데이터가 ChromaDB에 저장되는 방식을 직접 확인할 수 있습니다.

```python
# CH06 store.py에서 사용 예시
collection.add(
    documents=[chunk_text],
    metadatas=[{
        "doc_id":      "doc-2024-hr-001",
        "source_file": "hr/HR_취업규칙_v1.0.pdf",
        "department":  "HR",
        "page_count":  5
    }],
    ids=[chunk_id]
)
```

> **팁: `department` 필드를 enum으로 제한하는 이유**
> `department` 필드에 `"hr"`, `"HR"`, `"인사팀"` 처럼 같은 의미의 값이 여러 형태로 입력되면 필터 검색이 정확하게 동작하지 않습니다. JSON Schema의 `enum`으로 허용 값을 미리 고정해 두면 입력 단계에서 오류를 방지할 수 있습니다.

---

## 6. 정리하며

이 장에서는 RAG 시스템의 품질을 결정하는 **문서 표준화 파이프라인** 전체를 설계했습니다. 핵심 내용을 정리합니다.

- **GIGO 원칙**: 문서 품질이 RAG 검색 정확도를 좌우합니다. LLM 모델을 교체하기 전에 입력 문서를 먼저 점검하십시오.
- **수집 우선순위**: 디지털 원본(텍스트 레이어 PDF, Word, Markdown)을 우선 수집하고, 스캔 PDF는 최후 수단으로 남겨 두십시오. HWP는 PDF로 변환 후 동일한 PDF 파이프라인을 사용하십시오.
- **전처리 순서**: 특수문자 정규화 → 헤더/푸터 제거 → 공백 정규화 순서를 반드시 준수하십시오. 최종 출력은 Markdown으로 통일하면 LLM 이해도와 청킹 품질이 동시에 향상됩니다.
- **네이밍 표준**: `{부서}_{문서명}_{버전}.확장자` 포맷을 강제하면 파일명 파싱만으로 부서·버전 메타데이터가 자동 추출됩니다. `final`, `수정중`, 괄호 표기는 절대 사용하지 마십시오.
- **메타데이터 스키마**: `doc_id`, `source_file`, `department`, `version`, `created_date`, `doc_type` 6개 필수 필드를 설계했습니다. 이 스키마는 6장 ChromaDB 저장과 7장 출처 표시에 그대로 사용됩니다.

### 표준화 완료 체크리스트

6장으로 넘어가기 전에 아래 7가지 항목을 확인하십시오.

- [ ] 수집 대상 문서 목록이 확정되고 부서별 협조가 완료되었는가
- [ ] 모든 문서가 디지털 원본(텍스트 레이어 PDF, Word, Markdown) 또는 PDF 변환본으로 준비되었는가
- [ ] 파일명이 `{부서}_{문서명}_{버전}.확장자` 형식으로 변경되었는가
- [ ] 부서별 폴더(`hr/`, `finance/`, `ops/`, `security/`)가 생성되고 파일이 분류되었는가
- [ ] 전처리(헤더/푸터 제거, 공백 정규화, 인코딩 통일)가 완료되었는가
- [ ] 전처리 출력이 Markdown 형식으로 저장되었는가
- [ ] `metadata_schema.json`의 6개 필수 필드(`doc_id`, `source_file`, `department`, `created_date`, `version`, `doc_type`)가 각 문서에 매핑되었는가

### 다음 챕터 예고

표준화된 문서가 준비되었습니다. 6장에서는 이 문서들을 벡터 DB에 저장하는 전체 파이프라인을 구현합니다. `extractor.py`로 PDF에서 텍스트를 추출하고, `chunker.py`로 청크로 분할하며, `nomic-embed-text` 임베딩 모델로 벡터를 생성하고, `ChromaDB PersistentClient`로 영속 저장합니다. 5장에서 설계한 `parse_filename_metadata()`가 6장 코드에 그대로 이식되는 것을 확인할 수 있습니다.



---

# 6. 벡터 DB 구축

이 장에서는 PDF 문서에서 출발하여 **ChromaDB** 에 벡터를 저장하기까지의 전체 파이프라인을 구축합니다.
5장에서 표준화한 사내 문서를 실제로 처리하여, AI가 의미 기반으로 검색할 수 있는 지식 저장소를 완성합니다.

<!-- [IMAGE PLACEHOLDER: 06_pipeline_overview — PDF 문서에서 벡터 DB까지 5단계 전체 파이프라인 흐름 (PDF → 파싱 → 청킹 → 임베딩 → ChromaDB)] -->
*그림 6-1: CH06 전체 파이프라인 개요*

---

## 1. [실습 준비] 데이터 파일 확인

### 1.1 레포지토리 Clone

먼저 이 챕터의 예제 코드를 내려받겠습니다.

```bash
git clone https://github.com/your-org/CH06_vector-db.git
cd CH06_vector-db
```

> **참고: 레포 주소**
> 실제 GitHub 주소는 이 책의 공식 페이지(README)에서 확인하십시오.

패키지를 설치하고 환경 변수를 설정합니다.

```bash
pip install -r requirements.txt
cp .env.example .env
```

`.env` 파일을 열어 필요한 항목을 확인합니다.

```bash
# LLM Provider 설정 (ollama 또는 openai)
LLM_PROVIDER=ollama

# Vision LLM 모델명 (--vision 플래그 사용 시)
LLM_MODEL_NAME=llava:7b

# Ollama 설정
OLLAMA_BASE_URL=http://localhost:11434

# 임베딩 모델
EMBED_MODEL=nomic-embed-text

# ChromaDB 설정
CHROMA_PERSIST_DIR=./outputs/chroma_db
COLLECTION_NAME=rag_docs
```

이 챕터는 외부 클라우드 API 키가 필요하지 않습니다. 로컬 Ollama 서버만 실행 중이면 됩니다. Ollama 임베딩 모델을 미리 준비하십시오.

```bash
ollama pull nomic-embed-text    # 임베딩 모델 (필수)
ollama pull llava:7b            # Vision LLM (--vision 플래그 사용 시만 필요)
```

### 1.2 데이터 파일 구조 확인

`data/docs/` 폴더에는 5장의 네이밍 규칙을 준수하는 사내 문서 샘플이 들어 있습니다.

```
data/
└── docs/
    ├── hr/
    │   ├── HR_취업규칙_v1.0.pdf         ← 규칙 기반 파싱 실습
    │   └── HR_정보보안서약서.pdf          ← 부서 필터 검색 실습
    └── ops/
        └── OPS_신규서비스_런칭전략.pdf   ← Vision LLM 실습 (복합 레이아웃)
```

파일명이 `{부서}_{문서명}_{버전}.pdf` 형식을 따르고 있음을 확인할 수 있습니다. 이 규칙 덕분에 코드가 파일명만으로 부서(`HR`, `OPS`)와 버전(`v1.0`)을 자동으로 추출합니다. 5장에서 수립한 표준화 기준이 6장 코드에 직접 연결되는 첫 번째 순간입니다.

### 1.3 파이프라인 전체 흐름 미리보기

PDF에서 ChromaDB까지는 다음 5단계로 진행됩니다.

```mermaid
flowchart LR
    A["PDF 문서"] -- "파싱" --> B["원시 텍스트"]
    B -- "청킹" --> C["텍스트 청크"]
    C -- "임베딩" --> D["벡터"]
    D -- "저장" --> E["ChromaDB"]
    E -- "검색" --> F["유사도 결과"]
```

*그림 6-2: PDF → ChromaDB 5단계 파이프라인*

각 단계는 독립된 모듈로 구현되어 있습니다. 전체를 관통하는 진입점은 `src/main.py`의 `run_pipeline()` 함수이며, `--vision` 플래그 하나로 규칙 기반 모드와 Vision LLM 모드를 전환할 수 있습니다.

---

## 2. [규칙 기반] PDF 파싱

### 2.1 pdfplumber를 선택하는 이유

PDF 파싱 라이브러리는 크게 두 가지입니다. **pdfplumber** 와 PyMuPDF(fitz)입니다.

| 항목 | pdfplumber | PyMuPDF |
|------|-----------|---------|
| 표 감지 | O (extract_tables() 내장) | X |
| 속도 | 보통 | 빠름 |
| 사용 목적 | 표 포함 PDF (취업규칙, 계약서) | 순수 텍스트 위주 PDF |

사내 문서에는 연차 규정표, 예산 집계표처럼 표 구조가 많습니다. pdfplumber는 표를 감지하여 셀 내용을 Markdown 표 형식으로 보존하므로, RAG 검색 시 표 데이터가 온전히 검색됩니다.

### 2.2 extractor.py — 핵심 함수 발췌

전체 코드는 GitHub 레포의 `src/extractor.py`를 참고하십시오. 아래에서는 핵심 함수 3개를 발췌하여 설명합니다.

**함수 1: extract_text_pdfplumber()**

```python
def extract_text_pdfplumber(pdf_path: str) -> list[dict]:
    """pdfplumber로 PDF 페이지별 텍스트를 추출합니다."""

    # --- Input ---
    source_name = Path(pdf_path).name
    pages: list[dict] = []

    # --- Process ---
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            has_table = False
            text_parts: list[str] = []

            # 표 감지: 페이지에서 표 영역을 찾습니다
            tables = page.extract_tables()
            if tables:
                has_table = True
                plain_text = page.extract_text()
                if plain_text and plain_text.strip():
                    text_parts.append(plain_text.strip())

                # 각 표를 Markdown 형식으로 변환
                for table in tables:
                    md_table = _table_to_markdown(table)
                    if md_table:
                        text_parts.append(md_table)
            else:
                plain_text = page.extract_text()
                if plain_text and plain_text.strip():
                    text_parts.append(plain_text.strip())

            combined_text = "\n\n".join(text_parts).strip()
            if combined_text:
                pages.append({
                    "page": page_num + 1,
                    "text": combined_text,
                    "source": source_name,
                    "has_table": has_table,
                })

    # --- Output ---
    return pages
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: PDF 파일 경로 문자열
2. **처리(Process)**: pdfplumber로 페이지를 순회하면서 표 감지(`extract_tables()`) → 표는 Markdown 표로 변환, 일반 텍스트는 그대로 추출
3. **출력(Output)**: 페이지별 딕셔너리 리스트 `[{"page": int, "text": str, "source": str, "has_table": bool}]`

표가 있는 페이지는 `has_table=True`로 표시됩니다. 이 플래그는 나중에 청킹 전략 선택에 활용됩니다.

---

**함수 2: parse_filename_metadata()**

5장에서 수립한 네이밍 규칙(`{부서}_{문서명}_{버전}.pdf`)이 드디어 코드로 연결됩니다.

```python
def parse_filename_metadata(pdf_path: str) -> dict:
    """파일명에서 메타데이터를 자동 추출합니다.

    예: HR_취업규칙_v1.0.pdf
        → {"department": "HR", "doc_name": "취업규칙", "version": "v1.0"}
    """
    # --- Input ---
    stem = Path(pdf_path).stem  # 확장자 제외 파일명

    # --- Process ---
    parts = stem.split("_")

    if len(parts) >= 3:
        department = parts[0]
        version_candidate = parts[-1]
        if re.match(r"^v\d+(\.\d+)*$", version_candidate):
            version = version_candidate
            doc_name = "_".join(parts[1:-1])
        else:
            version = "unknown"
            doc_name = "_".join(parts[1:])
    elif len(parts) == 2:
        department, doc_name = parts[0], parts[1]
        version = "unknown"
    else:
        department = doc_name = version = "unknown"

    # --- Output ---
    return {
        "department": department,
        "doc_name": doc_name,
        "version": version,
        "source": Path(pdf_path).name,
    }
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: PDF 파일 경로 (또는 파일명)
2. **처리(Process)**: 파일명을 `_` 기준으로 분리 → 첫 세그먼트는 부서, 마지막 세그먼트가 `v숫자.숫자` 패턴이면 버전, 중간이 문서명
3. **출력(Output)**: `{"department": "HR", "doc_name": "취업규칙", "version": "v1.0", "source": "HR_취업규칙_v1.0.pdf"}`

이 함수를 통해 파일명을 사람이 직접 태그하지 않아도, 코드가 부서와 버전을 자동으로 인식합니다. ChromaDB에 이 메타데이터를 함께 저장하면 "HR 부서 문서 중에서만 검색"처럼 필터 검색이 가능합니다.

---

**함수 3: is_complex_layout()**

pdfplumber가 텍스트를 제대로 추출하지 못하는 상황을 감지합니다.

```python
def is_complex_layout(pages: list[dict], threshold: float = 0.3) -> bool:
    """규칙 기반 파싱 품질을 판단합니다.

    A4 기준 기대 글자 수(1,500자) 대비 실제 추출량이
    threshold 미만이면 Vision LLM 사용을 권장합니다.
    """
    # --- Process ---
    expected_chars_per_page = 1500
    total_chars = sum(len(p["text"]) for p in pages)
    avg_chars_per_page = total_chars / len(pages)
    ratio = avg_chars_per_page / expected_chars_per_page

    # --- Output ---
    return ratio < threshold   # True → Vision LLM 권장
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 페이지 딕셔너리 리스트, 판단 임계값(기본 0.3)
2. **처리(Process)**: 페이지당 평균 글자 수를 A4 기대치(1,500자)와 비교하여 비율 계산
3. **출력(Output)**: `True`면 Vision LLM 사용 권장, `False`면 규칙 기반으로 충분

> **팁: threshold 값 조정**
> 기본값 0.3(30%)은 일반적인 텍스트 문서 기준입니다. 표나 양식이 많은 문서는 0.2로 낮추고, 텍스트 밀도가 높은 법령 문서는 0.5로 높여보십시오.

### 2.3 규칙 기반 파싱의 한계

다단(multi-column) 레이아웃, 스캔본, 결재란이 포함된 PDF에서 pdfplumber는 종종 텍스트를 뒤섞거나 거의 추출하지 못합니다. 이 실패 케이스가 바로 다음 섹션 Vision LLM이 등장하는 이유입니다.

`OPS_신규서비스_런칭전략.pdf`처럼 도표와 그래픽이 많은 문서를 규칙 기반으로 파싱하면 `is_complex_layout()`이 `True`를 반환하며 경고를 출력합니다.

```
[권장] OPS_신규서비스_런칭전략.pdf은 복잡한 레이아웃이 감지되었습니다.
       --vision 플래그 사용을 고려하십시오.
```

---

## 3. [AI 기반] Vision LLM으로 Markdown 변환

### 3.1 Vision LLM을 최후 수단으로 쓰는 이유

모든 PDF에 Vision LLM을 사용하면 될 것 같지만, 그렇지 않습니다.

| 항목 | 규칙 기반 | Vision LLM |
|------|---------|-----------|
| 처리 속도 | 빠름 (초 단위) | 느림 (페이지당 수십 초) |
| GPU/메모리 | 불필요 | 필요 (llava:7b 기준 8GB+ VRAM) |
| 정확도 (일반 텍스트) | 높음 | 비슷하거나 낮을 수 있음 |
| 정확도 (복합 레이아웃) | 낮음 | 높음 |

올바른 전략은 규칙 기반으로 먼저 시도하고, 복합 레이아웃이 감지되면 Vision LLM으로 폴백(fallback)하는 것입니다. 이것이 비용과 품질 사이의 최선의 트레이드오프입니다.

<!-- [IMAGE PLACEHOLDER: 06_vision_fallback — 규칙 기반 우선, Vision LLM 폴백 전략 흐름도] -->
*그림 6-3: 규칙 기반 → Vision LLM 폴백 전략*

### 3.2 vision_extractor.py — 핵심 함수 발췌

전체 코드는 `src/vision_extractor.py`를 참고하십시오.

**함수 1: pdf_page_to_image()**

```python
def pdf_page_to_image(pdf_path: str, page_num: int, dpi: int = 150) -> bytes:
    """PDF의 특정 페이지를 PNG 이미지 바이트로 변환합니다."""

    # --- Process ---
    doc = fitz.open(pdf_path)
    page = doc[page_num]

    # DPI에 맞춰 확대 행렬 계산 (기본 72 DPI 기준)
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)
    pixmap = page.get_pixmap(matrix=matrix)
    image_bytes = pixmap.tobytes("png")
    doc.close()

    # --- Output ---
    return image_bytes
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: PDF 경로, 페이지 번호 (0-indexed), 해상도(DPI)
2. **처리(Process)**: PyMuPDF로 PDF 페이지를 열고 DPI 비율에 맞는 변환 행렬을 적용하여 PNG 이미지로 래스터화
3. **출력(Output)**: PNG 형식 이미지 바이트 데이터

> **팁: DPI 기본값 150의 의미**
> 150 DPI는 Vision LLM이 텍스트를 인식하기에 충분하면서 처리 시간을 합리적으로 유지하는 값입니다. 해상도를 300 DPI로 높이면 정확도가 올라가지만 처리 시간도 늘어납니다.

---

**함수 2: call_vision_llm()**

```python
def call_vision_llm(image_base64: str, page_num: int) -> str:
    """Vision LLM에 이미지를 전달하여 Markdown 텍스트로 변환합니다.

    LLM_PROVIDER 환경변수에 따라 Ollama 또는 OpenAI API를 사용합니다.
    """
    provider = _LLM_PROVIDER.lower().strip()

    # --- Process ---
    if provider == "ollama":
        markdown_text = _call_ollama_vision(image_base64)
    else:
        markdown_text = _call_openai_vision(image_base64)

    # --- Output ---
    return markdown_text
```

Ollama 방식의 실제 API 호출 코드는 다음과 같습니다.

```python
def _call_ollama_vision(image_base64: str) -> str:
    url = f"{_OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": _LLM_MODEL_NAME,   # llava:7b 등
        "prompt": _VISION_PROMPT,
        "images": [image_base64],   # base64 인코딩 이미지
        "stream": False,
    }
    response = requests.post(url, json=payload, timeout=600)
    return response.json().get("response", "").strip()
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: base64 인코딩 이미지, 페이지 번호
2. **처리(Process)**: `LLM_PROVIDER` 환경변수에 따라 Ollama(`/api/generate`) 또는 OpenAI Chat Completions API 호출. 프롬프트는 "이 PDF 페이지를 Markdown으로 변환하세요. 표는 Markdown 표로, 제목은 #으로 표현하세요."
3. **출력(Output)**: Vision LLM이 생성한 Markdown 텍스트 문자열

`LLM_PROVIDER` 환경변수 하나로 로컬 Ollama와 클라우드 OpenAI를 전환할 수 있게 설계한 이유가 있습니다. 처음에는 Ollama(무료)로 개발하고, 품질이 더 중요한 프로덕션 환경에서는 OpenAI(유료)로 교체할 때 코드를 바꿀 필요가 없습니다.

---

**함수 3: extract_pdf_to_markdown()**

PDF 전체를 처리하여 `.md` 파일로 저장하는 최상위 함수입니다.

```python
def extract_pdf_to_markdown(
    pdf_path: str,
    output_dir: str = "./outputs/markdown"
) -> str:
    """PDF 전체를 Vision LLM으로 처리하여 Markdown 파일로 저장합니다."""

    pdf_stem = Path(pdf_path).stem
    md_output_path = os.path.join(output_dir, f"{pdf_stem}.md")

    # --- Process ---
    all_markdown_parts: list[str] = []

    for page_idx in range(total_pages):
        page_num = page_idx + 1
        image_bytes = pdf_page_to_image(pdf_path, page_num=page_idx, dpi=150)
        image_base64 = image_to_base64(image_bytes)
        page_markdown = call_vision_llm(image_base64, page_num=page_num)

        page_header = f"\n\n---\n<!-- 페이지 {page_num} -->\n\n"
        all_markdown_parts.append(page_header + page_markdown)

    full_markdown = f"# {pdf_stem}\n\n" + "".join(all_markdown_parts)

    with open(md_output_path, "w", encoding="utf-8") as f:
        f.write(full_markdown)

    # --- Output ---
    return os.path.abspath(md_output_path)
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: PDF 파일 경로, 출력 디렉토리
2. **처리(Process)**: 페이지별로 이미지 변환 → Vision LLM 호출 → Markdown 조합. 페이지 구분자(`<!-- 페이지 N -->`)를 삽입하여 나중에 청킹 시 페이지 경계를 추적
3. **출력(Output)**: `outputs/markdown/HR_취업규칙_v1.0.md` 경로의 Markdown 파일

Vision LLM 처리가 완료되면 `outputs/markdown/` 폴더에 각 PDF와 동일한 이름의 `.md` 파일이 생성됩니다. 이 파일이 다음 단계 청킹의 입력이 됩니다.

> **주의: Vision LLM 처리 시간**
> llava:7b 기준 페이지당 약 30~120초 소요됩니다. 10페이지 문서라면 최대 20분이 걸릴 수 있습니다. CPU 전용 환경에서는 더 오래 걸립니다. GPU가 있는 환경에서는 5~20배 빠릅니다.

---

## 4. 청킹 전략

### 4.1 청킹이란 무엇인가

청킹(Chunking)은 긴 문서를 검색에 적합한 작은 단위로 분할하는 과정입니다. 도서관에 비유하면, 책 전체를 통째로 선반에 올리는 것이 아니라 장(chapter)별로 나눠서 색인을 만드는 것과 같습니다.

청킹이 필요한 이유는 다음 두 가지입니다.

첫째, LLM의 컨텍스트 윈도우는 유한합니다. 문서 전체를 한 번에 보낼 수 없으므로 관련 부분만 발췌하여 전달해야 합니다.

둘째, 검색 정밀도 향상입니다. "연차 신청 방법"을 질문했을 때 인사 규정 책 전체보다 "연차 사용 절차" 섹션만 반환하는 것이 훨씬 유용합니다.

### 4.2 두 가지 청킹 전략 비교

이 챕터에서는 두 가지 전략을 함께 제공하고 비교 결과를 출력합니다.

```mermaid
flowchart TD
    A["추출된 텍스트"] -- "규칙 기반 파싱 결과" --> B["Fixed-size 청킹"]
    A -- "Vision LLM 결과(Markdown)" --> C["Markdown 헤더 청킹"]
    B -- "500자 고정 분할" --> D["청크 리스트"]
    C -- "## 섹션 기준 분할" --> D
```

*그림 6-4: 두 가지 청킹 전략*

### 4.3 chunker.py — 핵심 함수 발췌

전체 코드는 `src/chunker.py`를 참고하십시오.

**함수 1: fixed_size_chunk()**

```python
def fixed_size_chunk(
    pages: list[dict],
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[dict]:
    """고정 크기 슬라이딩 윈도우 방식으로 텍스트를 청킹합니다."""

    # --- Process ---
    for source, page_group in groupby(pages, key=lambda p: p["source"]):
        full_text = "\n".join(p["text"] for p in page_list)

        start = 0
        while start < len(full_text):
            end = start + chunk_size
            chunk_text = full_text[start:end].strip()

            if chunk_text:
                chunks.append({
                    "chunk_id": f"{source}_fs_chunk_{chunk_index}",
                    "text": chunk_text,
                    "metadata": {
                        "source": source,
                        "page": page_num,
                        "chunk_index": chunk_index,
                        "department": department,
                    },
                })
                chunk_index += 1

            step = chunk_size - overlap   # 겹침 구간만큼 뒤로 이동
            start += step

    # --- Output ---
    return chunks
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 페이지 딕셔너리 리스트, 청크 크기(기본 500자), 겹침 크기(기본 50자)
2. **처리(Process)**: 페이지 텍스트를 하나로 연결한 후 500자씩 슬라이딩. `overlap=50`이므로 인접 청크가 50자씩 겹쳐 문장 경계에서의 정보 손실을 줄임
3. **출력(Output)**: `chunk_id`, `text`, `metadata`(source, page, department) 포함 청크 리스트

`overlap` 값이 0이면 문장 중간에서 청크가 잘릴 수 있습니다. 예를 들어 "연차는 사용 전월 말일" 이라는 핵심 정보가 두 청크에 걸쳐 분리되면, 어느 청크를 검색해도 완전한 정보를 얻지 못합니다. 50자 겹침은 이를 방지하는 안전장치입니다.

---

**함수 2: markdown_chunk()**

```python
def markdown_chunk(
    markdown_text: str,
    source: str,
    max_chunk_size: int = 500,
) -> list[dict]:
    """Markdown 헤더(##) 기준으로 텍스트를 의미 단위로 청킹합니다."""

    # --- Process ---
    # ## 헤더를 기준으로 섹션 분리
    section_pattern = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)
    matches = list(section_pattern.finditer(markdown_text))

    # 헤더 기준 섹션 추출
    for i, match in enumerate(matches):
        section_title = match.group(2).strip()
        section_start = match.start()
        section_end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown_text)
        section_text = markdown_text[section_start:section_end].strip()

        # max_chunk_size 초과 시 추가 분할 (섹션 제목 유지)
        if len(section_text) <= max_chunk_size:
            chunks.append({
                "chunk_id": f"{source}_mk_chunk_{chunk_index}",
                "text": section_text,
                "metadata": {
                    "source": source,
                    "section_title": section_title,  # 섹션 제목 보존
                    "department": department,
                    "chunk_index": chunk_index,
                },
            })
        # ... (초과 시 추가 분할 생략)

    # --- Output ---
    return chunks
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: Markdown 텍스트, 출처 파일명, 최대 청크 크기
2. **처리(Process)**: `##`, `###` 헤더를 섹션 경계로 인식하여 분리 → 섹션이 `max_chunk_size` 초과 시 추가 분할 → 메타데이터에 `section_title` 포함
3. **출력(Output)**: `section_title` 메타데이터가 포함된 청크 리스트

Markdown 청킹의 핵심 장점은 메타데이터에 `section_title`이 보존된다는 점입니다. "연차 사용 절차" 섹션에서 나온 청크는 검색 결과에 섹션 제목도 함께 반환되어 사용자가 출처를 정확히 파악할 수 있습니다.

---

**함수 3: compare_strategies()**

두 전략의 결과를 나란히 비교합니다.

```python
def compare_strategies(pages: list[dict], markdown_path: str) -> None:
    """Fixed-size 청킹과 Markdown 청킹 결과를 비교 출력합니다."""

    fixed_chunks = fixed_size_chunk(pages)
    with open(markdown_path, "r", encoding="utf-8") as f:
        markdown_text = f.read()
    mk_chunks = markdown_chunk(markdown_text, source=source)

    print("\n[청킹 전략 비교]")
    print("=" * 65)
    print(f"  {'항목':22s}  {'Fixed-size':>14}  {'Markdown 헤더':>14}")
    print(f"  {'청크 수':22s}  {fixed_stats['count']:>14,}  {mk_stats['count']:>14,}")
    print(f"  {'평균 길이 (문자)':22s}  {fixed_stats['avg_len']:>14.1f}  {mk_stats['avg_len']:>14.1f}")
    print(f"  {'섹션 제목 보존':22s}  {'X':>14}  {'O':>14}")
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 페이지 리스트, Markdown 파일 경로
2. **처리(Process)**: 두 전략으로 각각 청킹하여 청크 수·평균 길이·섹션 보존 여부를 집계
3. **출력(Output)**: 표 형태의 비교 결과를 표준 출력으로 내보냄

규칙 기반으로 파싱한 경우 기본 실행 시 비교 결과가 자동으로 출력됩니다. 예상 출력은 다음과 같습니다.

```
[청킹 전략 비교]
=================================================================
  항목                      Fixed-size   Markdown 헤더
  ---------------------------------------------------------
  청크 수                           42              28
  평균 길이 (문자)               482.3           498.7
  섹션 제목 보존                    X               O
=================================================================
```

> **팁: 어떤 전략을 선택할까**
> 순수 텍스트 위주 문서(계약서, 정책 문서)는 Fixed-size 청킹으로 충분합니다. 헤더 구조가 명확한 문서(취업규칙, 기술 명세서)는 Markdown 헤더 청킹이 검색 정밀도를 높입니다. 이 챕터에서는 규칙 기반 파싱 결과에 Fixed-size를, Vision LLM 결과에 Markdown 청킹을 적용합니다.

---

## 5. 임베딩 + ChromaDB 저장

### 5.1 임베딩이란 무엇인가

임베딩(Embedding)은 텍스트를 의미를 보존하는 숫자 벡터로 변환하는 과정입니다. "연차 신청 방법"과 "휴가 사용 절차"는 문자는 다르지만 의미가 비슷하므로, 임베딩 공간에서 가까운 위치에 놓입니다. 벡터 DB는 이 거리를 기반으로 유사한 내용을 검색합니다.

<!-- [IMAGE PLACEHOLDER: 06_embedding_concept — 텍스트가 벡터 공간에서 유사한 의미끼리 군집하는 모습 (연차, 휴가, 보안, 매출 텍스트가 각각 다른 위치에 분포)] -->
*그림 6-5: 임베딩 벡터 공간에서의 의미 군집*

이 챕터에서는 `nomic-embed-text` 모델을 사용합니다. 768차원 벡터를 생성하며, Ollama를 통해 완전히 로컬에서 실행됩니다.

### 5.2 embedder.py — 핵심 함수 발췌

전체 코드는 `src/embedder.py`를 참고하십시오.

**함수 1: embed_single()**

```python
def embed_single(text: str, model_name: str = _DEFAULT_EMBED_MODEL) -> list[float]:
    """단일 텍스트를 Ollama REST API로 임베딩 벡터로 변환합니다."""

    # --- Input ---
    url = f"{_OLLAMA_BASE_URL}/api/embeddings"
    payload = {"model": model_name, "prompt": text}

    # --- Process ---
    response = requests.post(url, json=payload, timeout=60)

    if response.status_code != 200:
        raise RuntimeError(f"Ollama API 오류: {response.text}")

    embedding = response.json().get("embedding")

    # --- Output ---
    return embedding
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 임베딩할 텍스트 문자열, 모델명(기본: `nomic-embed-text`)
2. **처리(Process)**: Ollama REST API의 `/api/embeddings` 엔드포인트에 POST 요청. LangChain을 사용하지 않고 `requests`로 직접 호출하여 API 동작 원리를 투명하게 확인 가능
3. **출력(Output)**: 768차원 float 리스트

LangChain 없이 `requests`로 직접 호출하는 이유가 있습니다. 이 챕터는 임베딩 API의 동작 원리를 배우는 것이 목적입니다. 추상화 레이어가 없으므로 요청과 응답 구조를 직접 볼 수 있습니다. 7장에서는 LangChain `OllamaEmbeddings`를 사용하므로, 두 방식을 비교하여 이해할 수 있습니다.

---

**함수 2: embed_texts()**

```python
def embed_texts(
    texts: list[str],
    model_name: str = _DEFAULT_EMBED_MODEL,
    batch_delay: float = 0.05,
) -> list[list[float]]:
    """텍스트 리스트를 배치로 임베딩합니다."""

    # --- Process ---
    for batch_start in range(0, total, _BATCH_SIZE):
        batch_end = min(batch_start + _BATCH_SIZE, total)
        batch = texts[batch_start:batch_end]

        for idx_in_batch, text in enumerate(batch):
            embedding = embed_single(text, model_name=model_name)
            embeddings.append(embedding)

        # 진행 상황 출력
        completed = min(batch_end, total)
        print(f"    진행: {completed}/{total} ({completed / total * 100:.1f}%)")

        if batch_end < total:
            time.sleep(batch_delay)   # 서버 과부하 방지

    # --- Output ---
    return embeddings
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 텍스트 문자열 리스트, 모델명, 배치 간 대기 시간
2. **처리(Process)**: 10개씩 배치로 나눠 순차 처리. 진행률을 실시간으로 출력. 배치 완료 후 0.05초 대기하여 Ollama 서버 과부하 방지
3. **출력(Output)**: 입력 텍스트와 동일한 순서의 임베딩 벡터 리스트

### 5.3 store.py — ChromaDB 영속 저장

전체 코드는 `src/store.py`를 참고하십시오.

> **참고: PersistentClient vs EphemeralClient**
> 3장에서는 `EphemeralClient`(인메모리)를 사용하여 프로그램 종료 시 데이터가 사라졌습니다. 이 챕터에서는 `PersistentClient`를 사용하므로 `outputs/chroma_db/` 폴더에 데이터가 디스크에 저장됩니다. 7장에서 RAG Q&A 엔진이 이 폴더를 그대로 읽어 사용합니다.

**함수 1: get_client()**

```python
def get_client(persist_dir: str = _DEFAULT_PERSIST_DIR) -> chromadb.PersistentClient:
    """ChromaDB PersistentClient를 초기화하고 반환합니다."""

    # --- Process ---
    abs_persist_dir = os.path.abspath(persist_dir)
    os.makedirs(abs_persist_dir, exist_ok=True)
    client = chromadb.PersistentClient(path=abs_persist_dir)

    # --- Output ---
    print(f"  ChromaDB 클라이언트 초기화 완료: 경로={abs_persist_dir}")
    return client
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 영속 저장 디렉토리 경로 (환경변수 `CHROMA_PERSIST_DIR`)
2. **처리(Process)**: 디렉토리를 생성(없으면)하고 `PersistentClient`를 초기화. 이미 데이터가 있으면 기존 데이터를 그대로 사용
3. **출력(Output)**: `chromadb.PersistentClient` 인스턴스

---

**함수 2: create_collection()**

```python
def create_collection(
    client: chromadb.PersistentClient,
    name: str = _DEFAULT_COLLECTION_NAME,
) -> chromadb.Collection:
    """ChromaDB 컬렉션을 생성하거나 기존 컬렉션을 반환합니다."""

    # --- Process ---
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},  # 코사인 유사도 사용
    )

    # --- Output ---
    print(f"  컬렉션 '{collection_name}' 준비 완료 (현재 문서 수: {collection.count()})")
    return collection
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: `PersistentClient` 인스턴스, 컬렉션 이름
2. **처리(Process)**: 동일한 이름의 컬렉션이 있으면 재사용, 없으면 새로 생성. `hnsw:space: cosine`으로 코사인 유사도를 거리 함수로 설정
3. **출력(Output)**: `chromadb.Collection` 인스턴스

코사인 유사도를 거리 함수로 사용하는 이유가 있습니다. 코사인 유사도는 벡터의 크기(문서 길이)와 무관하게 방향(의미)만 비교합니다. 짧은 FAQ 항목과 긴 정책 문서를 공정하게 비교할 수 있어 사내 문서처럼 길이가 다양한 데이터에 적합합니다.

---

**함수 3: add_documents()**

```python
def add_documents(
    collection: chromadb.Collection,
    chunks: list[dict],
    embeddings: list[list[float]],
) -> int:
    """청크와 임베딩 벡터를 ChromaDB 컬렉션에 저장합니다."""

    # --- Process ---
    ids = [chunk["chunk_id"] for chunk in chunks]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]

    # ChromaDB 허용 타입(str, int, float, bool)으로 변환
    safe_metadatas = [
        {k: str(v) if not isinstance(v, (str, int, float, bool)) else v
         for k, v in meta.items()}
        for meta in metadatas
    ]

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=safe_metadatas,
    )

    # --- Output ---
    return len(chunks)
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: ChromaDB 컬렉션, 청크 리스트, 임베딩 벡터 리스트
2. **처리(Process)**: `upsert()` 호출로 동일한 `chunk_id`가 있으면 덮어쓰고, 없으면 새로 삽입. 메타데이터 타입을 ChromaDB 허용 타입으로 안전 변환
3. **출력(Output)**: 저장된 청크 수

`insert()` 대신 `upsert()`를 사용하는 이유가 있습니다. 동일한 PDF를 다시 인제스트해도 중복이 생기지 않습니다. 문서를 수정하고 재실행하면 자동으로 최신 버전으로 교체됩니다.

---

**함수 4: search()**

```python
def search(
    collection: chromadb.Collection,
    query_embedding: list[float],
    k: int = 3,
    filter_dept: str | None = None,
) -> list[dict]:
    """쿼리 임베딩과 가장 유사한 문서를 벡터 검색합니다."""

    # --- Process ---
    # 부서 필터 설정 (metadata.department 기준)
    where_filter = {"department": filter_dept} if filter_dept else None

    query_params = {
        "query_embeddings": [query_embedding],
        "n_results": min(k, collection.count()),
        "include": ["documents", "metadatas", "distances"],
    }
    if where_filter:
        query_params["where"] = where_filter

    result = collection.query(**query_params)

    # --- Output ---
    return [
        {"text": doc, "metadata": meta, "distance": round(dist, 6)}
        for doc, meta, dist in zip(documents, metadatas, distances)
    ]
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: ChromaDB 컬렉션, 쿼리 임베딩 벡터, 반환 수(k), 부서 필터
2. **처리(Process)**: `filter_dept`가 있으면 `where` 절로 특정 부서만 필터링. `n_results`를 실제 문서 수와 min 처리하여 빈 컬렉션 오류 방지
3. **출력(Output)**: 유사도 높은 순 검색 결과 리스트 `[{"text": str, "metadata": dict, "distance": float}]`

`distance` 값이 낮을수록 쿼리와 유사한 문서입니다. 코사인 거리 기준으로 0.0이 완전 일치, 2.0이 완전 반대입니다. 일반적으로 0.3 이하면 높은 관련성으로 봅니다.

---

### 5.4 파이프라인 전체 실행

이제 전체 파이프라인을 실행할 준비가 되었습니다.

**규칙 기반 모드 (기본)**

```bash
# Ollama 서버가 실행 중인지 확인
ollama serve

# 파이프라인 실행
python src/main.py
```

<!-- [CAPTURE NEEDED: 06_pipeline-run — `python src/main.py` 실행 후 터미널 전체 화면. [1/5]부터 [5/5]까지 진행 단계와 테스트 검색 결과 3개가 출력된 상태] -->
*그림 6-6: 규칙 기반 파이프라인 실행 결과*

**Vision LLM 모드**

```bash
# llava 모델이 준비된 경우
python src/main.py --vision
```

`main.py`의 `run_pipeline()` 함수는 5단계로 진행 상황을 출력합니다.

```
=================================================================
  CH06 벡터 DB 구축 파이프라인
  파싱 모드: 규칙 기반 (pdfplumber)
=================================================================

[1/5] PDF 파일 확인 중...
  확인: HR_취업규칙_v1.0.pdf [부서=HR, 문서명=취업규칙, 버전=v1.0]
  확인: HR_정보보안서약서.pdf [부서=HR, 문서명=정보보안서약서, 버전=unknown]
  확인: OPS_신규서비스_런칭전략.pdf [부서=OPS, 문서명=신규서비스, 버전=unknown]
  총 3개 PDF 파일 확인 완료.

[2/5] PDF 파싱 중... (모드: 규칙 기반 (pdfplumber))
  완료: HR_취업규칙_v1.0.pdf → 5페이지 추출 (표 포함 페이지: 2개)
  완료: HR_정보보안서약서.pdf → 3페이지 추출 (표 포함 페이지: 0개)
  완료: OPS_신규서비스_런칭전략.pdf → 4페이지 추출 (표 포함 페이지: 1개)
  파싱 완료: 총 12개 페이지/섹션

[3/5] 텍스트 청킹 중...
  Fixed-size 청킹 완료: 42개 청크 생성

[청킹 전략 비교]
=================================================================
  항목                      Fixed-size   Markdown 헤더
  ---------------------------------------------------------
  청크 수                           42              28
  평균 길이 (문자)               482.3           498.7
  섹션 제목 보존                    X               O
=================================================================

[4/5] 임베딩 변환 중...
  모델: nomic-embed-text, 예상 차원: 768
  임베딩 시작: 총 42개 텍스트, 배치 크기=10, 모델=nomic-embed-text
    진행: 10/42 (23.8%)
    진행: 20/42 (47.6%)
    진행: 30/42 (71.4%)
    진행: 40/42 (95.2%)
    진행: 42/42 (100.0%)
  임베딩 완료: 42개 벡터, 차원=768

[5/5] ChromaDB 저장 및 검색 테스트 중...
  ChromaDB 클라이언트 초기화 완료: 경로=.../outputs/chroma_db
  컬렉션 'rag_docs' 준비 완료 (현재 문서 수: 0)
  42개 청크 저장 완료. 컬렉션 총 문서 수: 42

  컬렉션 통계:
    총 문서 수: 42
    부서별 분포:
      HR: 28개
      OPS: 14개

  테스트 검색 (3회):
  ------------------------------------------------------------

  검색 1: '연차 신청은 어떻게 하나요?' [전체]
    [1] 거리=0.1243 | HR_취업규칙_v1.0.pdf | 부서=HR
         연차는 사용 예정일 전월 말일까지 HR 포털을 통해 신청합니다...
    [2] 거리=0.1891 | HR_취업규칙_v1.0.pdf | 부서=HR
         제15조(연차유급휴가) 사용자는 1년간 80퍼센트 이상 출근한...
    [3] 거리=0.2317 | HR_정보보안서약서.pdf | 부서=HR
         본 서약서는 임직원의 정보 보호 의무를 규정합니다...

=================================================================
  파이프라인 완료.
  저장 경로: .../outputs/chroma_db
=================================================================
```

파이프라인이 완료되면 `outputs/chroma_db/` 폴더에 ChromaDB 데이터가 저장됩니다. 이 데이터는 7장 RAG Q&A 엔진이 그대로 이어받아 사용합니다.

> **주의: ChromaDB 데이터 재사용**
> 동일한 PDF를 다시 실행하면 기존 데이터를 덮어씁니다(`upsert`). 새 PDF를 추가하고 싶을 때는 `data/docs/` 폴더에 파일을 넣고 재실행하면 기존 데이터는 유지되고 새 파일만 추가됩니다.

---

## 6. 정리하며

이 장에서는 PDF 문서를 ChromaDB 벡터 저장소에 저장하기까지의 전체 파이프라인을 단계별로 구현했습니다.

- **규칙 기반 → AI 기반 폴백 전략**: pdfplumber로 빠르게 처리하고, `is_complex_layout()`이 복잡한 레이아웃을 감지하면 Vision LLM으로 전환합니다. 모든 PDF에 Vision LLM을 쓰는 것보다 비용과 속도 면에서 효율적입니다.

- **5장 표준화 규칙의 실증**: `parse_filename_metadata()`가 `{부서}_{문서명}_{버전}.pdf` 파일명을 파싱하여 `department`, `version` 메타데이터를 자동으로 추출합니다. 5장에서 수립한 규칙이 코드에 직접 연결되었습니다.

- **두 가지 청킹 전략 비교**: Fixed-size 청킹은 구현이 단순하고 범용적입니다. Markdown 헤더 청킹은 섹션 제목을 메타데이터로 보존하여 검색 정밀도를 높입니다. 문서 유형에 따라 전략을 선택하십시오.

- **임베딩 API 직접 호출**: LangChain 없이 `requests`로 Ollama의 `/api/embeddings` 엔드포인트를 직접 호출했습니다. API 동작 원리를 이해한 상태에서 7장에서 LangChain 추상화 레이어를 만나면 그 역할이 명확히 보입니다.

- **ChromaDB PersistentClient**: `EphemeralClient`(인메모리, 3장)와 달리 `PersistentClient`는 데이터를 디스크에 저장합니다. 프로그램을 재시작해도 임베딩 데이터가 유지되므로 재처리 비용이 없습니다. 저장된 `outputs/chroma_db/` 폴더는 7장 RAG Q&A 엔진의 입력이 됩니다.

### 자주 발생하는 오류와 해결법

| 오류 | 원인 | 해결 |
|------|------|------|
| `ConnectionRefusedError` | Ollama 서버 미실행 | `ollama serve` 실행 후 재시도 |
| `nomic-embed-text` 모델 없음 | 임베딩 모델 미다운로드 | `ollama pull nomic-embed-text` |
| `PermissionError` (ChromaDB) | 디렉토리 권한 부족 | `chmod 755 outputs/` 또는 `CHROMA_PERSIST_DIR` 경로 변경 |
| PDF 텍스트 추출량 0 | 스캔본 또는 이미지 위주 PDF | `--vision` 플래그 사용 |
| `RuntimeError: Ollama API 오류` | Vision LLM 모델 미설치 | `ollama pull llava:7b` |

---

다음 장에서는 이 ChromaDB를 연결하여 FastAPI 기반의 RAG Q&A 엔진을 구현합니다. 사용자가 질문을 입력하면 벡터 검색으로 관련 문서를 찾고, DeepSeek R1이 출처를 표시하며 답변을 생성하는 서비스가 완성됩니다.



---

# 7. RAG Q&A 엔진 구현

이 장에서는 6장에서 구축한 ChromaDB 벡터 데이터베이스를 바탕으로 **RAG Q&A 엔진** 을 FastAPI 서비스로 완성합니다. 사용자가 브라우저에서 질문을 입력하면, LLM이 질문의 의도를 분석하여 최적의 검색 경로를 선택하고, 사내 문서에서 근거를 찾아 답변을 생성하는 전체 흐름을 구현합니다.

이 장의 핵심 질문은 다음과 같습니다.

- "ChromaDB에 저장된 문서를 어떻게 HTTP 서비스로 노출하는가?"
- "LLM이 질문의 의도를 분석하여 검색 전략을 결정하는 인텐트 라우팅(Intent Routing)은 어떻게 구현하는가?"
- "프롬프트를 코드와 분리하여 관리하면 어떤 장점이 생기는가?"

6장에서는 PDF 파싱 → 청킹 → 임베딩 → ChromaDB 저장이라는 데이터 적재 파이프라인을 완성했습니다. 이제 적재된 데이터를 조회하여 사용자에게 답변하는 서비스 계층을 구현할 차례입니다.

---

```mermaid
flowchart LR
    A["브라우저\n(qa.html)"] -- "POST /admin/qa/query" --> B["qa.py\n라우터"]
    B --> C["QAService\nhybrid_search()"]
    C -- "router_prompt.j2" --> D["LLMService\nclassify_intent()"]
    D -- "route 결정" --> E["VectorService\nsearch_unstructured()"]
    E --> F["ChromaDB\nCH06 산출물"]
    F -- "청크 + 점수" --> G["QAService\nget_ai_answer()"]
    G -- "answer_prompt.j2" --> H["LLM\n답변 생성"]
    H -- "답변 + 출처" --> A
```

*그림 7-1: RAG Q&A 엔진 전체 요청 처리 흐름*

---

## 7.1 FastAPI로 RAG 서비스 제공하기

### FastAPI를 선택하는 이유

RAG Q&A 엔진을 구현할 때 웹 프레임워크로 **FastAPI** 를 선택합니다. 이유는 세 가지입니다.

첫째, **비동기 처리** 입니다. LLM 호출은 수 초에서 수십 초가 걸리는 블로킹 연산입니다. FastAPI는 `async/await` 기반으로 동작하므로, 한 요청이 LLM 응답을 기다리는 동안 다른 요청을 처리할 수 있습니다. 이를 통해 서버 자원을 효율적으로 사용합니다.

둘째, **Swagger UI 자동 제공** 입니다. FastAPI로 엔드포인트를 정의하면 `/docs` 경로에서 자동으로 API 문서가 생성됩니다. 코드와 문서를 별도로 관리할 필요가 없습니다.

셋째, **실무 배포 표준** 입니다. FastAPI는 uvicorn ASGI 서버와 함께 사용하여 프로덕션 환경에도 바로 배포할 수 있는 구조를 갖춥니다.

### 프로젝트 구조 확인

레포지토리를 클론하면 아래와 같은 구조를 확인할 수 있습니다.

```
CH07_RAG_QA엔진구현/
├── app/
│   ├── main.py                    ← FastAPI 앱 진입점
│   ├── routers/
│   │   ├── ui.py                  ← HTML 페이지 라우터
│   │   └── qa.py                  ← Q&A REST API
│   ├── services/
│   │   ├── llm_service.py         ← LLM 초기화 + 프롬프트 렌더링
│   │   ├── vector_service.py      ← ChromaDB 벡터 검색
│   │   └── qa_service.py          ← RAG 파이프라인 오케스트레이터
│   ├── prompts/
│   │   ├── router_prompt.j2       ← 인텐트 분류 프롬프트
│   │   └── answer_prompt.j2       ← 답변 생성 프롬프트
│   ├── templates/                 ← Jinja2 HTML 템플릿
│   └── static/                    ← CSS / JS 정적 파일
├── scripts/
│   └── ingest.py                  ← PDF → ChromaDB 인제스트 스크립트
└── data/
    ├── docs/                      ← 사내 문서 샘플 (PDF)
    └── chroma_db/                 ← ingest.py 실행 후 자동 생성
```

라우터는 `app/routers/` 아래에 기능별로 분리되어 있습니다. `ui.py`는 HTML 페이지를 렌더링하고, `qa.py`는 REST API 엔드포인트를 담당합니다. 서비스 로직은 `app/services/` 아래에 계층별로 분리되어 있습니다.

<!-- [IMAGE PLACEHOLDER: 07_app_structure — FastAPI 앱 폴더 구조와 계층별 역할(라우터/서비스/프롬프트) 관계도] -->
*그림 7-2: CH07 FastAPI 앱 계층 구조*

### 실습 준비: 레포 클론 및 환경 설정

아래 순서대로 실습 환경을 준비하십시오.

**1단계: 레포지토리 클론**

```bash
git clone https://github.com/{repo}/CH07_RAG_QA엔진구현
cd CH07_RAG_QA엔진구현
```

**2단계: 환경 변수 설정**

`.env.example` 파일을 복사하여 `.env`를 생성하고 자신의 환경에 맞게 수정하십시오.

```bash
cp .env.example .env
```

`.env` 파일의 주요 설정값은 다음과 같습니다.

```env
# LLM Provider (ollama | openai)
LLM_PROVIDER=ollama

# LLM 모델명 (Ollama: deepseek-r1:1.5b)
LLM_MODEL_NAME=deepseek-r1:1.5b

# Ollama 서버
OLLAMA_BASE_URL=http://localhost:11434

# 임베딩 모델 (CH06과 반드시 동일)
EMBED_MODEL=nomic-embed-text

# ChromaDB 경로 (CH06 산출물 위치)
CHROMA_PERSIST_DIR=./data/chroma_db
COLLECTION_NAME=rag_docs
```

> **주의: 임베딩 모델은 CH06과 동일해야 합니다**
> `EMBED_MODEL`은 CH06에서 사용한 `nomic-embed-text`와 반드시 일치해야 합니다. 서로 다른 임베딩 모델로 저장된 벡터와 검색 쿼리를 비교하면 유사도 계산이 올바르지 않습니다.

**3단계: 패키지 설치**

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

`requirements.txt`에는 다음 패키지들이 포함되어 있습니다.

```
fastapi==0.115.5
uvicorn==0.32.1
jinja2==3.1.4
langchain==0.3.7
langchain-community==0.3.7
langchain-ollama==0.2.1
chromadb==0.5.23
pymupdf>=1.24.0
python-dotenv==1.0.1
```

**4단계: Ollama 모델 확인**

```bash
ollama pull deepseek-r1:1.5b
ollama pull nomic-embed-text
```

### FastAPI 앱 진입점: `app/main.py`

`app/main.py`는 FastAPI 애플리케이션의 진입점입니다. 핵심 역할은 세 가지입니다. 첫째, 라우터를 등록합니다. 둘째, 정적 파일(CSS, JS)을 마운트합니다. 셋째, 루트(`/`) 접근을 대시보드로 리다이렉트합니다.

```python
# app/main.py (핵심 부분 발췌)

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from app.routers.ui import router as ui_router
from app.routers.qa import router as qa_router

app = FastAPI(
    title="RAG Q&A 엔진",
    description="CH07 — ChromaDB 기반 사내 문서 RAG Q&A 서비스",
    version="1.0.0",
)

# 정적 파일 마운트
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 라우터 등록 (qa_router를 ui_router보다 먼저 등록)
app.include_router(qa_router)
app.include_router(ui_router)

@app.get("/")
def root() -> RedirectResponse:
    return RedirectResponse(url="/admin/dashboard", status_code=302)
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: FastAPI 앱 객체가 생성되고, `app/` 하위의 라우터 모듈이 임포트됩니다.
2. **처리(Process)**: `qa_router`를 먼저 등록하여 `/admin/qa/query`(POST) 경로가 `/admin/qa`(GET) HTML 라우터보다 우선 처리됩니다. `StaticFiles`를 마운트하여 `/static` 경로로 CSS·JS를 제공합니다.
3. **출력(Output)**: `http://127.0.0.1:8000` 접속 시 `/admin/dashboard`로 자동 리다이렉트됩니다.

> **팁: 라우터 등록 순서가 중요합니다**
> FastAPI는 라우터를 등록한 순서대로 경로를 매칭합니다. `qa_router`(`POST /admin/qa/query`)를 `ui_router`(`GET /admin/qa`) 앞에 등록하지 않으면, `/admin/qa` 경로가 중복될 때 충돌이 발생할 수 있습니다.

### 서버 실행 및 첫 접속

프로젝트 루트(CH07_RAG_QA엔진구현 폴더)에서 실행하십시오.

```bash
python -m app.main
```

또는 uvicorn을 직접 실행하십시오.

```bash
uvicorn app.main:app --reload
```

서버가 정상 기동되면 아래와 같은 로그가 출력됩니다.

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
[LLMService] 초기화 중 (제공자: ollama, 모델: deepseek-r1:1.5b)
[VectorService] 초기화 중 (임베딩 모델: nomic-embed-text, DB 경로: ./data/chroma_db)
[VectorService] ChromaDB 연결 완료.
[QAService] 오케스트레이터 초기화 완료.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

<!-- [CAPTURE NEEDED: 07_server_startup — 서버 기동 직후 터미널 전체 화면 (LLMService, VectorService, QAService 초기화 로그 포함)] -->
*그림 7-3: RAG Q&A 엔진 서버 기동 성공 화면*

브라우저에서 `http://127.0.0.1:8000` 에 접속하면 대시보드 화면으로 이동합니다. 대시보드에서 ChromaDB 문서 수, 사용 중인 LLM 모델, 임베딩 모델 정보를 확인할 수 있습니다.

<!-- [CAPTURE NEEDED: 07_dashboard — 브라우저 대시보드 화면 (ChromaDB 문서 수, 모델 정보 카드 표시)] -->
*그림 7-4: RAG Q&A 엔진 대시보드 화면*

---

## 7.2 LLM 서비스 계층 구성

### 서비스 계층을 분리하는 이유

RAG Q&A 엔진에서 LLM 호출 로직을 별도 클래스(`LLMService`)로 분리하는 이유는 **교체 용이성** 때문입니다. 개발 환경에서는 무료 로컬 모델(Ollama + DeepSeek R1)을 사용하다가, 상용 환경에서는 OpenAI의 GPT-4o로 전환하는 일이 잦습니다. `LLMService`가 없다면 LLM 호출 코드가 곳곳에 흩어져 전환할 때 수십 곳을 수정해야 합니다. 계층으로 분리해 두면 `.env` 파일의 `LLM_PROVIDER` 값 하나만 바꾸면 됩니다.

프롬프트도 마찬가지입니다. 프롬프트를 Python 코드 안에 문자열로 하드코딩하면, 프롬프트를 수정할 때마다 코드 파일을 열어 수정하고 재배포해야 합니다. `.j2` 확장자의 **Jinja2 템플릿 파일** 로 관리하면 개발자가 아닌 기획자나 운영자도 프롬프트를 직접 수정할 수 있으며, 버전 관리 시스템에서 프롬프트 변경 이력을 명확히 추적할 수 있습니다.

<!-- [IMAGE PLACEHOLDER: 07_llm_service_layer — LLMService 계층 구조: Ollama/OpenAI 전환 패턴, Jinja2 프롬프트 파일 분리 구조] -->
*그림 7-5: LLMService 계층과 LLM 제공자 전환 구조*

### `LLMService` 클래스

`app/services/llm_service.py`의 `LLMService` 클래스는 네 가지 메서드를 제공합니다.

- `_init_engine()`: 환경 변수를 읽어 `ChatOllama` 또는 `ChatOpenAI` 엔진을 초기화합니다.
- `render_prompt()`: Jinja2 템플릿 파일을 렌더링하여 프롬프트 문자열을 반환합니다.
- `invoke()`: LLM을 호출하고, DeepSeek R1의 `<think>` 태그를 제거한 응답을 반환합니다.
- `generate_answer()`: `answer_prompt.j2`로 최종 답변을 생성합니다.
- `classify_intent()`: `router_prompt.j2`로 질문의 라우팅 의도를 분류합니다.

```python
# app/services/llm_service.py (핵심 부분 발췌)

class LLMService:
    """LLM 초기화 및 프롬프트 렌더링 서비스."""

    def __init__(self) -> None:
        self.provider = os.getenv("LLM_PROVIDER", "ollama").lower()
        default_model = "gpt-4o-mini" if self.provider == "openai" else "deepseek-r1:1.5b"
        self.model_name = os.getenv("LLM_MODEL_NAME", default_model)

        # Jinja2 환경: app/prompts/ 디렉토리를 로더로 사용
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_dir = os.path.join(base_dir, "prompts")
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        self._init_engine()

    def invoke(self, prompt: str) -> str:
        """LLM을 호출하고 응답 문자열을 반환합니다."""
        response = self.llm.invoke(prompt)
        if hasattr(response, "content"):
            response = response.content

        # DeepSeek-R1 <think>...</think> 사고 과정 제거
        if isinstance(response, str) and "<think>" in response and "</think>" in response:
            response = response.split("</think>")[-1].strip()

        return str(response)

    def classify_intent(self, query: str) -> dict:
        """router_prompt.j2로 질문의 라우팅 의도를 분류합니다."""
        rendered_prompt = self.render_prompt("router_prompt.j2", query=query)
        response = self.invoke(rendered_prompt)

        try:
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            return {"route": "hybrid", "reason": "JSON 파싱 실패 — hybrid로 대체"}
        except Exception:
            return {"route": "hybrid", "reason": "인텐트 분석 오류 — hybrid로 대체"}


# 싱글톤 인스턴스
llm_service = LLMService()
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 환경 변수 `LLM_PROVIDER`, `LLM_MODEL_NAME`, `OLLAMA_BASE_URL`을 읽어 LLM 제공자와 모델을 결정합니다.
2. **처리(Process)**: `_init_engine()`에서 `provider` 값에 따라 `ChatOllama` 또는 `ChatOpenAI` 엔진 인스턴스를 생성합니다. `invoke()` 호출 시 LLM 응답에서 `<think>...</think>` 태그를 제거하여 깔끔한 답변만 반환합니다.
3. **출력(Output)**: 모듈 하단의 `llm_service = LLMService()` 싱글톤 인스턴스를 다른 서비스가 `import`하여 사용합니다.

> **참고: DeepSeek R1의 `<think>` 태그**
> DeepSeek R1 모델은 답변 전에 내부 추론 과정을 `<think>...</think>` 태그 안에 출력합니다. 이 태그는 모델이 어떻게 생각했는지 보여주는 "사고 로그"입니다. 최종 사용자에게는 이 내용이 필요하지 않으므로, `</think>` 이후의 텍스트만 추출하여 반환합니다.

### Jinja2 프롬프트 템플릿

프롬프트 파일은 `app/prompts/` 폴더에 `.j2` 확장자로 저장됩니다. Jinja2 템플릿은 `{{ 변수명 }}` 문법으로 동적 값을 삽입합니다.

**`router_prompt.j2` — 인텐트 분류 프롬프트:**

```jinja2
{# 질문 의도 분석 — 검색 전략 결정 #}
당신은 사내 AI 비서의 질문 분석기(Router)입니다.
사용자의 [질문]을 분석하여 어떤 데이터 소스를 검색해야 할지 결정하세요.

[데이터 소스]
- unstructured: 사내 규정, 가이드라인, 정책 문서 검색이 필요한 경우
- hybrid: 명확히 구분하기 어렵거나 복합 정보가 필요한 경우

[출력 형식]
반드시 아래 JSON 형식으로만 답변하세요. 다른 설명은 생략합니다.
{"route": "unstructured|hybrid", "reason": "의도 분석 결과"}

[질문]
{{ query }}
```

**`answer_prompt.j2` — 답변 생성 프롬프트:**

```jinja2
{# 최종 답변 생성 프롬프트 #}
당신은 사내 AI 비서입니다.
아래 [컨텍스트] 정보를 바탕으로 [질문]에 친절하고 정확하게 답변하세요.

[규칙]
- 반드시 한국어로 답변하세요.
- 정보가 부족하면 아는 범위에서만 답변하고 추측하지 마세요.
- 문서 내용은 핵심을 요약하여 답변하세요.

[컨텍스트]
{{ context }}

[질문]
{{ query }}
```

두 프롬프트 파일을 코드가 아닌 별도 파일로 관리하므로, 프롬프트를 수정할 때 Python 코드를 전혀 건드릴 필요가 없습니다. 10장에서 다루는 프롬프트 튜닝 작업도 이 파일만 수정하면 적용됩니다.

> **팁: `router_prompt.j2`에서 JSON만 반환하도록 지시하는 이유**
> LLM이 자유 형식으로 답변하면 파싱이 어렵습니다. "반드시 JSON 형식으로만 답변하세요"라고 명시하면 `classify_intent()` 메서드가 응답에서 JSON을 추출하여 `route` 값을 정확히 꺼낼 수 있습니다. 파싱에 실패하더라도 기본값 `"hybrid"`로 대체하여 서비스가 중단되지 않습니다.

---

## 7.3 벡터 검색 서비스 연결

### CH06 산출물을 그대로 사용하는 이유

7장의 `VectorService`는 6장에서 구축한 ChromaDB를 그대로 활용합니다. 별도의 재임베딩 과정이 필요 없습니다. 이유는 명확합니다. ChromaDB에 문서를 저장할 때 사용한 임베딩 모델(`nomic-embed-text`)과 검색 쿼리를 임베딩할 때 사용하는 모델이 동일해야 유사도 비교가 정확합니다. 6장과 7장이 같은 모델(`nomic-embed-text`)을 사용하므로, 6장의 ChromaDB를 `data/chroma_db/` 폴더에 복사하는 것만으로 7장 실습이 가능합니다.

### 문서 인제스트: `scripts/ingest.py`

6장의 ChromaDB를 그대로 복사할 수도 있지만, 7장에서는 독립적으로 문서를 인제스트할 수 있는 `scripts/ingest.py` 스크립트도 제공합니다. `data/docs/` 폴더에 사내 PDF 문서를 넣고 아래 명령어를 실행하면 ChromaDB가 생성됩니다.

```bash
# 전체 인제스트
python scripts/ingest.py

# 파일 지정 인제스트 (저사양 환경 권장)
python scripts/ingest.py --file HR_사내규정_v1.0.pdf

# ChromaDB 초기화 후 전체 재인제스트
python scripts/ingest.py --reset
```

`ingest.py`는 5단계 파이프라인으로 동작합니다.

```
[1/5] PDF 탐색 (data/docs/ 하위 PDF 파일 목록 수집)
  ↓
[2/5] 페이지 캡처 (PyMuPDF로 PNG 저장 → data/pages/)
  ↓
[3/5] Vision 파싱 (Vision LLM으로 Markdown 변환 → data/markdown/)
  ↓
[4/5] 청킹 (## 헤더 기준 섹션 분할, 500자 초과 시 슬라이딩 분할)
  ↓
[5/5] 임베딩 + ChromaDB 저장 (nomic-embed-text → data/chroma_db/)
```

> **팁: RAM에 따른 Vision 모델 선택**
>
> | RAM | Vision 모델 | 채팅 LLM | 인제스트 예상 시간(파일당) |
> |-----|------------|---------|----------------------|
> | 8GB 이하 | `moondream` | `deepseek-r1:1.5b` | 1~2분 |
> | 16GB | `llava:7b` | `deepseek-r1:1.5b` | 3~5분 |
> | 32GB+ | `llava:13b` | `qwen2.5:7b` | 1~2분 |
>
> `.env` 파일의 `VISION_MODEL` 값을 자신의 환경에 맞게 설정하십시오.

### `VectorService` 클래스

`app/services/vector_service.py`의 `VectorService` 클래스는 ChromaDB에 연결하고 유사도 검색을 제공합니다.

```python
# app/services/vector_service.py (핵심 부분 발췌)

class VectorService:
    """ChromaDB 벡터 검색 서비스 — Ollama 임베딩 사용."""

    def __init__(self) -> None:
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        embed_model = os.getenv("EMBED_MODEL", "nomic-embed-text")
        collection_name = os.getenv("COLLECTION_NAME", "rag_docs")

        from langchain_ollama import OllamaEmbeddings
        self.embeddings = OllamaEmbeddings(base_url=ollama_url, model=embed_model)
        self.vector_db: Chroma | None = None

        if os.path.exists(VECTOR_DB_DIR):
            self.vector_db = Chroma(
                persist_directory=VECTOR_DB_DIR,
                embedding_function=self.embeddings,
                collection_name=collection_name,
            )
            print("[VectorService] ChromaDB 연결 완료.")
        else:
            print(f"[VectorService] 경고: {VECTOR_DB_DIR} 디렉토리가 없습니다.")

    def search_unstructured(self, query: str, k: int = 3) -> list[dict]:
        """비정형 문서 유사도 검색을 수행합니다."""
        # --- Process ---
        raw_results = self.vector_db.similarity_search_with_score(query, k=k)

        # --- Output ---
        formatted = []
        for doc, distance in raw_results:
            # Chroma 거리 → 유사도 변환 (낮은 거리 = 높은 유사도)
            similarity = max(0.0, 1.0 - float(distance))
            formatted.append({
                "content": doc.page_content,
                "source": doc.metadata.get("source", "알 수 없음"),
                "score": round(similarity, 4),
            })
        return formatted


# 싱글톤 인스턴스
vector_service = VectorService()
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 검색 쿼리 문자열과 반환할 문서 수(`k=3`)를 입력받습니다.
2. **처리(Process)**: `similarity_search_with_score(query, k=k)`로 ChromaDB에서 유사도 검색을 수행합니다. Chroma가 반환하는 `distance` 값(낮을수록 유사)을 `1.0 - distance` 수식으로 `score`(높을수록 유사)로 변환합니다.
3. **출력(Output)**: `[{"content": "...", "source": "파일명", "score": 0.87}, ...]` 형태의 리스트를 반환합니다.

> **참고: Chroma의 거리와 유사도**
> ChromaDB의 `similarity_search_with_score()`는 코사인 거리(cosine distance)를 반환합니다. 거리는 낮을수록 가깝습니다. 이를 독자가 이해하기 쉬운 유사도(similarity)로 변환하기 위해 `1.0 - distance` 공식을 사용합니다. 결과적으로 0에 가까울수록 관련성이 낮고, 1에 가까울수록 관련성이 높습니다.

**싱글톤 패턴을 사용하는 이유**: `VectorService` 초기화 시 OllamaEmbeddings 연결과 ChromaDB 로드에 시간이 걸립니다. 이를 FastAPI 요청마다 반복하면 응답 속도가 크게 저하됩니다. 모듈 하단에서 `vector_service = VectorService()`로 한 번만 생성한 후, 이후 모든 요청에서 이 인스턴스를 재사용합니다.

---

## 7.4 인텐트 라우팅과 RAG Q&A 오케스트레이션

### 인텐트 라우팅이 필요한 이유

"연차 사용 기준은 어떻게 됩니까?"와 "김철수 씨의 연차는 며칠이나 남았습니까?" — 이 두 질문은 모두 연차에 관한 것이지만, 필요한 정보의 성격이 다릅니다. 전자는 HR 규정 문서(비정형 데이터)에서 찾아야 하고, 후자는 직원 DB(정형 데이터)에서 조회해야 합니다.

모든 질문에 대해 무조건 벡터 검색을 수행하면 두 가지 문제가 생깁니다. 첫째, 정형 DB 조회 질문에 대해 문서에서 엉뚱한 내용을 찾아 답변합니다. 둘째, 불필요한 검색을 수행하여 응답 속도가 느려집니다.

**인텐트 라우팅(Intent Routing)** 은 LLM이 질문을 먼저 분석하여 "이 질문은 문서 검색으로 해결 가능한가, 아니면 DB 조회가 필요한가"를 결정하는 과정입니다. 도서관 안내 데스크 직원이 "이 책은 인문학 섹션에 있습니다" 또는 "그 데이터는 열람실 컴퓨터로 조회하십시오"라고 적절히 안내하는 것과 같습니다.

```mermaid
flowchart TD
    A["사용자 질문"] -- "classify_intent()" --> B["LLMService"]
    B -- "router_prompt.j2" --> C{"route 결정"}
    C -- "unstructured" --> D["VectorService\n문서 벡터 검색"]
    C -- "hybrid" --> D
    D -- "청크 + 점수" --> E["get_ai_answer()"]
    E -- "answer_prompt.j2" --> F["LLM 답변 생성"]
    F --> G["답변 + 출처 반환"]
```

*그림 7-6: 인텐트 라우팅 흐름도*

### `QAService` 클래스

`app/services/qa_service.py`의 `QAService`는 인텐트 라우팅 → 벡터 검색 → LLM 답변 생성의 전체 파이프라인을 오케스트레이션합니다.

```python
# app/services/qa_service.py (핵심 부분 발췌)

class QAService:
    """RAG Q&A 파이프라인 오케스트레이터."""

    def hybrid_search(self, query: str) -> dict:
        """인텐트 라우팅을 적용한 문서 검색을 수행합니다."""
        # --- Input ---
        print(f"[QAService] 질문 수신: {query[:50]}...")

        # --- Process ---
        # 1. 인텐트 분류
        analysis = llm_service.classify_intent(query)
        route = analysis.get("route", "hybrid")
        print(f"[QAService] 라우팅 결정: {route} (사유: {analysis.get('reason', '-')})")

        # CH07: 비정형 문서 검색만 지원 (CH08에서 structured 경로 추가)
        if route == "structured":
            route = "hybrid"

        unstructured = []
        if route in ("unstructured", "hybrid"):
            unstructured = vector_service.search_unstructured(query)

        # --- Output ---
        return {"query": query, "unstructured": unstructured, "route": route}

    def get_ai_answer(self, query: str, search_results: dict) -> str:
        """검색 결과로 컨텍스트를 구성하고 LLM 답변을 생성합니다."""
        # --- Input ---
        unstructured_docs = search_results.get("unstructured", [])

        # --- Process ---
        context_parts = []
        if unstructured_docs:
            context_parts.append("[사내 문서 내용]")
            for doc in unstructured_docs:
                source = doc.get("source", "알 수 없음")
                content = doc.get("content", "")
                context_parts.append(f"- {content} (출처: {source})")
        else:
            context_parts.append("[관련 문서를 찾지 못했습니다. 일반 지식으로 답변합니다.]")

        context_text = "\n".join(context_parts)

        # --- Output ---
        return llm_service.generate_answer(query, context_text)


# 싱글톤 인스턴스
qa_service = QAService()
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 사용자 질문 문자열이 `hybrid_search(query)`로 전달됩니다.
2. **처리(Process)**:
   - `llm_service.classify_intent(query)`로 LLM이 질문을 분석하여 `route` 값(`unstructured` 또는 `hybrid`)을 결정합니다.
   - `route` 값에 따라 `vector_service.search_unstructured(query)`를 호출하여 ChromaDB에서 관련 문서 청크를 검색합니다.
   - `get_ai_answer()`에서 검색 결과를 `[사내 문서 내용]` 형식의 컨텍스트로 조립한 뒤, `llm_service.generate_answer()`를 호출합니다.
3. **출력(Output)**: LLM이 생성한 답변 문자열을 반환합니다.

> **참고: CH07에서 `structured` 라우팅이 `hybrid`로 대체되는 이유**
> CH07은 비정형 문서(ChromaDB) 검색만 지원합니다. LLM이 질문을 DB 조회가 필요한 `structured`로 분류하더라도, 이 장에서는 `hybrid` 경로로 대체하여 문서 검색으로 처리합니다. DB 조회(PostgreSQL)와 MCP Agent는 8장에서 확장됩니다.

### Q&A REST API: `app/routers/qa.py`

`app/routers/qa.py`는 브라우저에서 전송된 질문을 받아 `QAService`를 호출하고 결과를 JSON으로 반환합니다.

```python
# app/routers/qa.py (핵심 부분 발췌)

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.qa_service import qa_service

router = APIRouter(prefix="/admin/qa", tags=["qa"])

class QueryRequest(BaseModel):
    """질문 요청 스키마."""
    query: str

@router.post("/query")
async def query_qa(request: QueryRequest) -> dict:
    """사용자 질문을 처리하여 RAG 기반 답변을 반환합니다."""
    # --- Input ---
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="질문이 비어 있습니다.")

    # --- Process ---
    try:
        search_results = qa_service.hybrid_search(query)
        answer = qa_service.get_ai_answer(query, search_results)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"질문 처리 중 오류: {str(exc)}")

    # --- Output ---
    return {
        "query": query,
        "answer": answer,
        "route": search_results["route"],
        "unstructured_data": search_results["unstructured"],
    }
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: `POST /admin/qa/query` 요청 본문에서 `{"query": "연차 사용 기준은?"}` 형태의 JSON을 수신합니다.
2. **처리(Process)**: `qa_service.hybrid_search()`로 인텐트 라우팅 + 벡터 검색을 수행한 뒤, `qa_service.get_ai_answer()`로 LLM 답변을 생성합니다. 오류 발생 시 HTTP 500을 반환합니다.
3. **출력(Output)**: `{"query": "...", "answer": "...", "route": "hybrid", "unstructured_data": [...]}` 형태의 JSON을 반환합니다. `unstructured_data`에는 각 청크의 `content`, `source`, `score`가 포함됩니다.

Swagger UI(`http://127.0.0.1:8000/docs`)에서 엔드포인트를 직접 테스트할 수도 있습니다.

<!-- [CAPTURE NEEDED: 07_swagger_ui — Swagger UI 화면에서 POST /admin/qa/query 엔드포인트를 펼쳐 요청/응답 스키마가 표시된 상태] -->
*그림 7-7: Swagger UI에서 Q&A 엔드포인트 확인*

---

## 7.5 웹 채팅 인터페이스 구현

### HTML 템플릿 구조

`app/templates/` 폴더에는 세 개의 HTML 파일이 있습니다.

- `base.html`: 공통 레이아웃(사이드바, 네비게이션, CSS/JS 링크)을 정의합니다. 모든 페이지가 이 파일을 `{% extends "base.html" %}`로 상속합니다.
- `dashboard.html`: 시스템 상태(ChromaDB 문서 수, 모델 정보)를 카드 형식으로 표시합니다.
- `qa.html`: 채팅 인터페이스를 제공합니다. 질문 입력창, 채팅 기록 영역, 출처 카드 아코디언이 포함됩니다.

`ui.py` 라우터는 이 템플릿들을 Jinja2로 렌더링하여 HTML 응답을 반환합니다.

```python
# app/routers/ui.py (핵심 부분 발췌)

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    """대시보드 화면을 렌더링합니다."""
    doc_count = 0
    db_status = "연결 끊김"
    if vector_service.vector_db is not None:
        collection = vector_service.vector_db._collection
        doc_count = collection.count()
        db_status = "정상"

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "doc_count": doc_count,
            "db_status": db_status,
            "llm_model": os.getenv("LLM_MODEL_NAME", "deepseek-r1:1.5b"),
            "embed_model": os.getenv("EMBED_MODEL", "nomic-embed-text"),
        },
    )
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 브라우저에서 `GET /admin/dashboard` 요청이 들어옵니다.
2. **처리(Process)**: `vector_service.vector_db._collection.count()`로 ChromaDB에 저장된 문서 청크 수를 조회합니다. 환경 변수에서 LLM 모델명과 임베딩 모델명을 읽어 템플릿 컨텍스트에 추가합니다.
3. **출력(Output)**: `dashboard.html`에 동적 데이터가 채워진 HTML 페이지가 브라우저로 반환됩니다.

### 비동기 채팅: `app/static/js/qa.js`

`qa.js`는 채팅 인터페이스의 모든 클라이언트 동작을 담당합니다. 핵심 함수는 `submitQuery()`입니다.

```javascript
// app/static/js/qa.js (핵심 부분 발췌)

async function submitQuery(event) {
    if (event) event.preventDefault();
    const query = queryInput.value.trim();
    if (!query) return;

    // 사용자 메시지 DOM 추가
    const userMsgDiv = document.createElement('div');
    userMsgDiv.className = 'chat-message user-message';
    userMsgDiv.textContent = query;  // XSS 방지: textContent 사용
    chatHistory.appendChild(userMsgDiv);

    loadingIndicator.style.display = 'flex';

    try {
        const response = await fetch('/admin/qa/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
        });

        const data = await response.json();

        // AI 답변 + 출처 카드 렌더링
        const aiMsgDiv = document.createElement('div');
        aiMsgDiv.innerHTML = `
            <div class="avatar">AI</div>
            <div class="message-content">
                <div class="ai-ans-text">${data.answer}</div>
                ${renderSourceAccordion(data)}
            </div>
        `;
        chatHistory.appendChild(aiMsgDiv);
        saveChatHistory();  // localStorage에 대화 내역 저장

    } finally {
        loadingIndicator.style.display = 'none';
        scrollToBottom();
    }
}
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 사용자가 채팅 입력창에 질문을 입력하고 전송 버튼을 클릭합니다.
2. **처리(Process)**: `fetch('/admin/qa/query', { method: 'POST', ... })`로 서버에 비동기 요청을 전송합니다. 응답 대기 중에는 로딩 표시기를 보여줍니다. 응답을 받으면 `renderSourceAccordion(data)`로 출처 카드 HTML을 생성합니다.
3. **출력(Output)**: 브라우저 채팅 영역에 AI 답변과 출처 카드가 렌더링됩니다. 대화 내역은 `localStorage`에 저장되어 페이지를 새로고침해도 유지됩니다.

### 출처 카드 렌더링

사용자가 AI 답변의 근거를 확인할 수 있도록 **출처 카드(Source Card)** 를 제공합니다. 서버에서 반환된 `unstructured_data` 배열의 각 항목을 카드 형태로 표시합니다.

```javascript
// renderSourceAccordion() 핵심 로직

function renderSourceAccordion(data) {
    const uniqueDocs = /* content 기준 중복 제거 */;

    const docsHtml = uniqueDocs.map(doc => {
        const source = doc.source || '출처 불명';
        const preview = doc.content.substring(0, 150) + '...';
        const score = doc.score.toFixed(2);
        return `
            <div class="source-item">
                <small>${source}</small>
                <p>${preview}</p>
                <div class="source-score">유사도: ${score}</div>
            </div>
        `;
    }).join('');

    return `
        <div class="route-badge">라우팅: ${data.route}</div>
        <div class="source-container">
            <div class="source-header" onclick="this.parentElement.classList.toggle('active')">
                <span>분석 근거 보기 (출처 문서)</span>
            </div>
            <div class="source-body">${docsHtml}</div>
        </div>
    `;
}
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 서버 응답 JSON의 `unstructured_data` 배열 (`[{content, source, score}, ...]`)을 입력받습니다.
2. **처리(Process)**: `content` 기준으로 중복 문서를 제거합니다. 각 문서의 `source`, `content` 앞 150자, `score`를 카드 HTML로 변환합니다. "분석 근거 보기" 버튼을 클릭하면 `active` 클래스 토글로 아코디언이 펼쳐집니다.
3. **출력(Output)**: 라우팅 결과 배지와 출처 카드 아코디언 HTML을 반환합니다.

출처 카드가 중요한 이유는 AI 답변의 신뢰성 때문입니다. 사용자는 "이 답변이 어떤 문서를 기반으로 생성되었는가?"를 출처 카드에서 직접 확인합니다. 유사도 점수가 낮은 경우(0.5 미만) 사용자 스스로 판단하여 답변의 신뢰도를 평가할 수 있습니다.

### Q&A 채팅 화면 접속

브라우저에서 `http://127.0.0.1:8000/admin/qa` 에 접속한 뒤, 질문을 입력하고 전송해 보십시오.

예시 질문을 입력하여 RAG 동작을 확인하십시오.

- "연차 신청 절차는 어떻게 됩니까?"
- "보안 정책의 주요 내용을 알려주십시오."
- "신규 서비스 런칭 전 체크리스트를 알려주십시오."

<!-- [CAPTURE NEEDED: 07_qa_chat — 브라우저 Q&A 채팅 화면에서 질문 입력 후 AI 답변과 출처 카드 아코디언이 펼쳐진 상태] -->
*그림 7-8: RAG Q&A 채팅 화면 — 답변 및 출처 카드 표시*

> **팁: ChromaDB가 없는 경우의 동작**
> `data/chroma_db/` 폴더가 없더라도 서버는 정상 기동됩니다. `VectorService`가 지연 초기화(lazy initialization)를 지원하여, 폴더가 없으면 경고 로그만 출력하고 서비스를 시작합니다. 질문을 보내면 "관련 문서를 찾지 못했습니다"라는 응답이 반환됩니다. `scripts/ingest.py`를 먼저 실행하여 ChromaDB를 생성한 뒤 질문하십시오.

---

## 7.6 정리하며

이 장에서는 6장에서 구축한 ChromaDB를 기반으로 완전한 RAG Q&A 웹 서비스를 구현했습니다.

- **FastAPI 서비스 계층화**: `ui.py`(HTML 라우터), `qa.py`(REST API), `llm_service.py`, `vector_service.py`, `qa_service.py` 다섯 파일로 책임을 분리하였습니다. 각 계층이 독립적으로 교체·확장 가능한 구조입니다.

- **Jinja2 프롬프트 템플릿**: 프롬프트를 `.j2` 파일로 분리하여 Python 코드 변경 없이 프롬프트를 수정할 수 있게 했습니다. `LLM_PROVIDER` 환경 변수 하나로 Ollama와 OpenAI를 전환하는 설계도 `LLMService` 계층 덕분에 가능합니다.

- **인텐트 라우팅**: LLM이 사용자 질문의 의도를 `router_prompt.j2`로 분석하여 검색 전략(`unstructured` / `hybrid`)을 결정합니다. 모든 질문에 벡터 검색을 강제하지 않고 의도에 따라 최적 경로를 선택합니다.

- **출처 카드와 투명성**: 답변과 함께 `source`(파일명)와 `score`(유사도)를 출처 카드로 제공합니다. 사용자가 AI 답변의 근거를 직접 검증할 수 있습니다.

- **싱글톤 서비스 공유**: `llm_service`, `vector_service`, `qa_service`를 모듈 수준에서 단일 인스턴스로 생성합니다. FastAPI 앱이 시작될 때 한 번만 초기화하므로 매 요청마다 초기화 비용이 발생하지 않습니다.

### 자주 발생하는 오류와 해결법

| 오류 | 원인 | 해결법 |
|------|------|--------|
| `[VectorService] 경고: ./data/chroma_db 디렉토리가 없습니다` | ChromaDB가 생성되지 않음 | `python scripts/ingest.py` 실행 |
| `ConnectionRefusedError` (LLM 호출 시) | Ollama 서버가 실행 중이지 않음 | `ollama serve` 실행 확인 |
| `모델 로드 실패` | 지정한 모델이 설치되지 않음 | `ollama pull deepseek-r1:1.5b` 실행 |
| 답변에 `<think>` 태그가 포함됨 | DeepSeek R1 출력 처리 미적용 | `LLMService.invoke()` 코드의 `<think>` 제거 로직 확인 |
| 검색 결과가 비어있음 | ChromaDB 컬렉션명 불일치 | `.env`의 `COLLECTION_NAME` 값이 CH06과 동일한지 확인 |
| `Import error: langchain_ollama` | 패키지 미설치 | `pip install langchain-ollama` 실행 |

### 다음 장 예고

7장에서는 비정형 문서(ChromaDB) 검색에 집중했습니다. 그러나 실제 업무에서는 "김철수 씨의 남은 연차는 며칠입니까?"와 같이 PostgreSQL 데이터베이스를 조회해야 하는 정형 질문이 빈번합니다.

8장에서는 **MCP(Model Context Protocol)** 를 이용하여 PostgreSQL 조회 기능을 LLM 에이전트가 호출할 수 있는 도구(Tool)로 등록합니다. 7장의 FastAPI 서버에 MCP Agent 탭이 추가되고, 정형 + 비정형 데이터를 모두 처리하는 통합 에이전트가 완성됩니다.

> **전체 코드는 GitHub 레포지토리를 참고하십시오.**
> 이 장에서 발췌된 코드는 핵심 로직 위주로 일부 생략되었습니다. 전체 소스 코드(`app/templates/`, `app/static/css/`, `scripts/ingest.py` 포함)는 예제 레포지토리에서 확인하십시오.



---

# 8. 통합 에이전트 설계 (MCP + RAG)

이 장에서는 **MCP(Model Context Protocol)** 를 이용하여 PostgreSQL DB 조회 도구를 LLM에게 노출하고, **ReAct 에이전트** 가 자율적으로 도구를 선택·실행하는 시스템을 구현합니다. 7장에서 완성한 RAG Q&A 엔진은 비정형 문서 검색을 담당했습니다. 이 장에서는 그 위에 정형 데이터(직원·휴가·매출)를 조회하는 MCP Agent 탭을 추가하여, 하나의 웹 서비스에서 두 가지 질의 방식을 모두 처리할 수 있도록 확장합니다.

이 장을 마치면 "홍길동의 남은 연차가 며칠이고, 연차 신청 기한은 어떻게 되나요?"와 같이 정형 DB 조회와 비정형 문서 검색이 동시에 필요한 복합 질의를 처리할 수 있습니다.

<!-- [IMAGE PLACEHOLDER: 08_chapter_overview — CH08 전체 파이프라인: 브라우저 → FastAPI → MCPAgentService → FastMCP 서버 서브프로세스 → PostgreSQL, 좌측에 CH07 RAG 경로도 함께 표시] -->
*그림 8-1: 8장 전체 구성 개요*

---

## 8.1 MCP란 무엇인가

### MCP의 정의와 등장 배경

**MCP(Model Context Protocol)** 는 Anthropic이 제안한 오픈 프로토콜로, LLM이 외부 도구와 데이터 소스를 표준 방식으로 사용할 수 있게 해 줍니다. 마치 USB가 다양한 기기를 컴퓨터에 꽂기 위한 표준 규격이듯, MCP는 LLM이 외부 기능을 호출하기 위한 표준 규격입니다.

MCP가 등장하기 전에는 LLM에게 외부 도구를 붙이기 위해 각 프레임워크(LangChain, LlamaIndex 등)마다 서로 다른 방식의 Tool을 구현해야 했습니다. 한 번 만든 LangChain Tool은 Claude Desktop이나 Cursor에서 재사용할 수 없었고, 도구를 새 환경에 연동할 때마다 처음부터 다시 구현해야 했습니다.

MCP는 이 문제를 해결합니다. MCP 서버를 한 번 만들면 Claude Desktop, Cursor, LangChain 등 MCP를 지원하는 어떤 클라이언트에서도 동일한 도구를 재사용할 수 있습니다.

```mermaid
flowchart LR
    A["LangChain\n(클라이언트)"] -- "MCP 프로토콜" --> C["MCP 서버\n(DB 도구)"]
    B["Claude Desktop\n(클라이언트)"] -- "MCP 프로토콜" --> C
    C -- "SQL 조회" --> D["PostgreSQL"]
```

*그림 8-2: MCP 서버는 클라이언트에 무관하게 재사용 가능*

### LangChain Tool과 MCP의 차이

두 방식을 직접 비교하면 MCP의 장점이 명확해집니다.

| 비교 항목 | LangChain Tool | MCP |
|----------|---------------|-----|
| 결합 방식 | Python 코드에 직접 종속 | 표준 프로토콜로 분리 |
| 재사용 범위 | 해당 LangChain 앱 내부만 | 모든 MCP 클라이언트 |
| 서버/클라이언트 분리 | 분리 없음 | 완전 분리 (별도 프로세스) |
| JSON Schema | 수동 작성 필요 | 데코레이터로 자동 생성 |
| 프로토콜 변경 | 앱 재배포 필요 | 서버만 교체 가능 |

### FastMCP 소개

**FastMCP** 는 Python에서 MCP 서버를 빠르게 구현하는 프레임워크입니다. 저수준 MCP 프로토콜을 직접 구현하는 대신, FastAPI처럼 데코레이터(`@mcp.tool()`) 하나로 도구를 등록하고 JSON Schema를 자동 생성합니다.

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Company DB Assistant")

@mcp.tool()
def list_employees() -> str:
    """전체 직원 목록을 조회합니다."""
    ...
```

`@mcp.tool()` 데코레이터를 붙이는 것만으로 해당 함수의 이름, docstring, 파라미터 타입이 JSON Schema로 자동 변환됩니다. LLM은 이 JSON Schema를 보고 "어떤 도구가 있고, 어떤 파라미터로 호출하면 되는지"를 파악합니다.

> **참고: FastMCP 설치 패키지**
> FastMCP는 `mcp[cli]` 패키지에 포함되어 있습니다. `requirements.txt`의 `mcp[cli]>=1.0.0`을 설치하면 `mcp.server.fastmcp` 모듈을 사용할 수 있습니다.

---

## 8.2 실습 준비 — 레포 클론과 환경 설정

이 챕터의 예제 코드는 독립 레포로 제공됩니다. 이전 챕터의 산출물(ChromaDB, PostgreSQL)을 의존하지 않고, 레포 내에서 모두 자체 생성합니다.

### 1단계: 레포 클론

```bash
git clone https://github.com/your-org/CH08_MCP_QA에이전트.git
cd CH08_MCP_QA에이전트
```

### 2단계: 가상환경 생성 및 패키지 설치

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3단계: 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 아래 항목을 확인하십시오.

```dotenv
# LLM Provider (ollama | openai)
LLM_PROVIDER=ollama

# LLM 모델명
LLM_MODEL_NAME=deepseek-r1:1.5b

# Ollama 서버
OLLAMA_BASE_URL=http://localhost:11434

# 임베딩 모델
EMBED_MODEL=nomic-embed-text

# ChromaDB
CHROMA_PERSIST_DIR=./data/chroma_db
COLLECTION_NAME=rag_docs

# PostgreSQL
DATABASE_URL=postgresql://company:company1234@localhost:5432/company_db
```

> **팁: 저사양 환경 모델 선택**
> RAM이 8GB 이하라면 `LLM_MODEL_NAME=deepseek-r1:1.5b`와 Vision 모델로 `moondream`을 사용하십시오. 16GB 이상이라면 `deepseek-r1:8b` 또는 `llava:7b`를 권장합니다.

### 4단계: PostgreSQL 컨테이너 실행 및 DB 초기화

```bash
docker-compose up -d
python -m app.database.init_db
```

### 5단계: PDF 인제스트 (ChromaDB 구축)

```bash
python scripts/ingest.py
```

> **참고: 저사양 환경에서의 파일 지정 인제스트**
> 전체 인제스트에 시간이 오래 걸리는 환경이라면 `--file` 옵션으로 한 파일씩 처리하십시오.
> ```bash
> python scripts/ingest.py --file HR_취업규칙_v1.0.pdf
> ```

### 6단계: 서버 실행

```bash
python -m app.main
```

브라우저에서 `http://127.0.0.1:8000` 에 접속하면 대시보드가 표시됩니다.

<!-- [CAPTURE NEEDED: 08_dashboard — `python -m app.main` 실행 후 브라우저에서 http://127.0.0.1:8000/admin/dashboard 접속 화면. 직원 수와 총 매출 통계 카드가 표시된 상태] -->
*그림 8-3: CH08 대시보드 — PostgreSQL 통계 카드가 추가된 화면*

---

## 8.3 PostgreSQL 연결과 DB 초기화

개념을 이해했으니 이제 직접 구현해 보겠습니다. 먼저 PostgreSQL 연결 계층을 살펴봅니다.

### docker-compose.yml — PostgreSQL 컨테이너 설정

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: company_db
      POSTGRES_USER: company
      POSTGRES_PASSWORD: company1234
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: `docker-compose up -d` 명령어 실행
2. **처리(Process)**: PostgreSQL 16 컨테이너를 로컬 5432 포트에 바인딩하고, `postgres_data` 볼륨에 데이터를 영속 저장
3. **출력(Output)**: `company_db` 데이터베이스가 초기화된 PostgreSQL 서버

> **참고: Docker Compose로 DB를 구동하는 이유**
> 직접 PostgreSQL을 설치하면 OS마다 설치 경로와 설정 방법이 다르고, 실습 후 삭제도 번거롭습니다. Docker Compose를 사용하면 `docker-compose up -d` 한 줄로 모든 환경에서 동일하게 구동되고, `docker-compose down -v`로 깔끔하게 정리됩니다.

### PostgresConnectionWrapper — 연결 래퍼 패턴

`app/database/connection.py`는 psycopg2 연결을 `PostgresConnectionWrapper`로 감쌉니다. 이 클래스가 왜 필요한지 이해하는 것이 중요합니다.

psycopg2의 기본 커서는 결과를 튜플로 반환합니다. `cursor.fetchone()`이 `(1, '홍길동', '인사팀')`처럼 반환하면, 코드 어디서나 인덱스(`row[0]`, `row[1]`)로 접근해야 합니다. 컬럼이 추가·삭제되면 모든 인덱스를 수동으로 수정해야 합니다.

`PostgresConnectionWrapper`는 `RealDictCursor`를 사용하여 결과를 딕셔너리(`{"id": 1, "name": "홍길동", "dept": "인사팀"}`)로 반환합니다. 컬럼 이름으로 접근하므로 스키마 변경에 강인하고, 코드 가독성도 높아집니다.

```python
# app/database/connection.py (핵심 발췌)

class PostgresConnectionWrapper:
    """psycopg2 연결을 DictCursor 기반으로 래핑합니다."""

    def __init__(self, conn: psycopg2.extensions.connection) -> None:
        self.conn = conn
        self.cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def execute(self, query: str, params: tuple | None = None) -> None:
        self.cursor.execute(query, params)

    def fetchall(self) -> list[dict]:
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]

    def fetchone(self) -> dict | None:
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def commit(self) -> None:
        self.conn.commit()

    def close(self) -> None:
        self.cursor.close()
        self.conn.close()


def get_db_connection() -> PostgresConnectionWrapper:
    """SQLAlchemy raw_connection()을 PostgresConnectionWrapper로 반환합니다."""
    try:
        raw_conn = engine.raw_connection()
        return PostgresConnectionWrapper(raw_conn)
    except Exception as exc:
        raise Exception(
            f"PostgreSQL 연결에 실패했습니다. "
            f"docker-compose up -d 명령으로 컨테이너를 실행하십시오. 오류: {exc}"
        ) from exc
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: `DATABASE_URL` 환경 변수 (기본값: `postgresql://company:company1234@localhost:5432/company_db`)
2. **처리(Process)**: SQLAlchemy Engine의 `raw_connection()`으로 psycopg2 연결을 획득하고, `RealDictCursor`를 장착한 `PostgresConnectionWrapper`로 감쌈
3. **출력(Output)**: `execute`, `fetchall`, `fetchone`, `commit`, `close` 메서드를 제공하는 연결 래퍼 객체

> **참고: SQLAlchemy를 Engine 획득에만 사용하는 이유**
> SQLAlchemy ORM 전체를 도입하면 모델 정의, 세션 관리 등 학습 부담이 커집니다. 이 프로젝트는 SQLAlchemy의 연결 풀 관리 기능만 활용하고, 실제 쿼리는 psycopg2 DictCursor로 직접 실행합니다. 학습 비용을 최소화하면서도 연결 풀의 안정성은 그대로 누립니다.

### init_db.py — 테이블 생성과 샘플 데이터

`app/database/init_db.py`의 `init_db()` 함수는 세 단계로 동작합니다.

```python
# app/database/init_db.py (핵심 발췌)

def init_db() -> None:
    """PostgreSQL 테이블 생성 + 샘플 데이터 삽입."""
    conn = get_db_connection()
    try:
        # [1/3] 테이블 생성
        conn.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id        SERIAL PRIMARY KEY,
                name      VARCHAR(50)  NOT NULL,
                dept      VARCHAR(50)  NOT NULL,
                email     VARCHAR(100) UNIQUE NOT NULL,
                hire_date DATE         NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leave_balance (
                id          SERIAL PRIMARY KEY,
                employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
                year        INTEGER NOT NULL,
                total       INTEGER NOT NULL DEFAULT 15,
                used        NUMERIC(4,1) NOT NULL DEFAULT 0,
                remaining   NUMERIC(4,1) NOT NULL DEFAULT 15
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id          SERIAL PRIMARY KEY,
                dept        VARCHAR(50)  NOT NULL,
                amount      BIGINT       NOT NULL,
                date        DATE         NOT NULL,
                description TEXT
            )
        """)
        conn.commit()

        # [2/3] 직원 10명 및 휴가 데이터 삽입
        # (홍길동, 김철수, 이영희 등 5개 부서)
        # ...

        # [3/3] 매출 30건 삽입 (최근 90일)
        # ...
    finally:
        conn.close()
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: `DATABASE_URL` 환경 변수
2. **처리(Process)**: `CREATE TABLE IF NOT EXISTS`로 `employees`, `leave_balance`, `sales` 세 테이블을 생성하고, 직원 10명·휴가 데이터·매출 30건을 삽입
3. **출력(Output)**: 인사팀·개발팀·영업팀·마케팅팀·기술지원팀에 소속된 직원 10명, 각 직원의 연차 현황, 최근 90일 매출 30건이 저장된 DB

> **팁: 이미 데이터가 존재할 때**
> `init_db.py`는 실행 시 직원 수를 먼저 확인합니다. 이미 데이터가 있으면 삽입을 건너뜁니다. 처음부터 다시 초기화하려면 `docker-compose down -v && docker-compose up -d`로 볼륨까지 삭제한 후 재실행하십시오.

### crud.py — DB 조회 함수 구조

`app/database/crud.py`는 직원·휴가·매출 테이블의 CRUD 함수를 모아 둔 모듈입니다. 모든 함수는 `PostgresConnectionWrapper`를 첫 번째 인수로 받아 DB에 독립적인 단위 테스트가 가능합니다.

```mermaid
flowchart LR
    A["직원(employees)"] -- "employee_id FK" --> B["휴가(leave_balance)"]
    C["매출(sales)"] -- "dept 참조" --> A
```

*그림 8-4: 세 테이블의 관계 — employees가 중심*

핵심 함수 목록은 다음과 같습니다.

| 분류 | 함수 | 설명 |
|------|------|------|
| 직원 | `list_employees(conn)` | 전체 직원 목록 조회 |
| 직원 | `get_employee(conn, employee_id)` | 특정 직원 상세 조회 |
| 휴가 | `get_leave_by_employee(conn, employee_id)` | 특정 직원의 잔여 휴가 조회 |
| 휴가 | `use_leave(conn, employee_id, days)` | 휴가 사용 등록 및 차감 |
| 매출 | `get_sales_by_dept(conn, dept_name)` | 부서별 매출 집계 |
| 매출 | `get_sales_period(conn, start, end)` | 기간별 매출 조회 |

전체 코드는 GitHub 레포의 `app/database/crud.py`를 참고하십시오.

---

## 8.4 MCP 서버 구현 (FastMCP)

### mcp_server.py 전체 구조

`mcp/mcp_server.py`는 FastMCP 서버로, PostgreSQL의 직원·휴가·매출 데이터를 9개의 MCP 도구로 노출합니다.

```python
# mcp/mcp_server.py (전체 구조 발췌)

from mcp.server.fastmcp import FastMCP
from app.database.connection import get_db_connection
from app.database import crud

mcp = FastMCP("Company DB Assistant")

# ─── 직원 도구 (2개) ───────────────────────────
@mcp.tool()
def list_employees() -> str:
    """전체 직원 목록을 조회합니다."""
    conn = get_db_connection()
    try:
        employees = crud.list_employees(conn)
        return json.dumps(employees, ensure_ascii=False, indent=2)
    finally:
        conn.close()

@mcp.tool()
def get_employee(employee_id: int) -> str:
    """특정 직원의 상세 정보를 조회합니다."""
    conn = get_db_connection()
    try:
        employee = crud.get_employee(conn, employee_id)
        if not employee:
            return json.dumps({"error": f"직원 ID {employee_id}를 찾을 수 없습니다."})
        return json.dumps(employee, ensure_ascii=False, indent=2)
    finally:
        conn.close()

# ─── 휴가 도구 (3개) ───────────────────────────
@mcp.tool()
def list_leaves() -> str: ...

@mcp.tool()
def get_leave_balance(employee_id: int) -> str: ...

@mcp.tool()
def use_leave(employee_id: int, days: float) -> str: ...

# ─── 매출 도구 (4개) ───────────────────────────
@mcp.tool()
def list_sales(limit: int = 10) -> str: ...

@mcp.tool()
def create_sale(dept: str, amount: int, date: str, description: str = "") -> str: ...

@mcp.tool()
def get_sales_period(start: str, end: str) -> str: ...

@mcp.tool()
def get_sales_by_dept(dept_name: str) -> str: ...

# ─── 서버 실행 ─────────────────────────────────
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: `@mcp.tool()` 데코레이터로 등록된 함수의 docstring과 타입 힌트
2. **처리(Process)**: FastMCP가 함수 시그니처를 분석하여 JSON Schema를 자동 생성하고, `crud.py` 함수를 호출하여 PostgreSQL에서 데이터를 조회
3. **출력(Output)**: JSON 문자열 형태의 조회 결과 (MCP 클라이언트가 파싱하여 LLM에게 전달)

### @mcp.tool() 데코레이터의 동작 원리

`@mcp.tool()`이 붙은 함수는 MCP 서버에 등록될 때 다음 정보가 자동으로 JSON Schema로 변환됩니다.

- 함수명 → 도구 이름 (`"name": "get_employee"`)
- docstring → 도구 설명 (`"description": "특정 직원의 상세 정보를 조회합니다."`)
- 파라미터 타입 힌트 → 입력 스키마 (`"inputSchema": {"employee_id": {"type": "integer"}}`)

LLM은 이 JSON Schema를 읽고 "어떤 상황에서 어떤 파라미터로 이 도구를 호출해야 하는지"를 스스로 판단합니다. 개발자는 docstring과 타입 힌트만 잘 작성하면 됩니다.

<!-- [IMAGE PLACEHOLDER: 08_mcp_schema_flow — @mcp.tool() 데코레이터가 Python 함수를 JSON Schema로 변환하는 과정. 왼쪽에 Python 함수 코드, 오른쪽에 JSON Schema 구조] -->
*그림 8-5: @mcp.tool() 데코레이터의 JSON Schema 자동 생성*

### stdio 모드로 실행되는 이유

`mcp.run(transport="stdio")`는 MCP 서버가 표준 입출력(stdin/stdout)을 통해 클라이언트와 통신하는 방식입니다.

MCP 서버를 HTTP 서버로 운영하는 방법도 있지만, stdio 모드를 선택하는 데는 이유가 있습니다.

- **프로세스 격리**: MCP 서버가 별도 프로세스로 실행됩니다. 서버가 크래시나도 클라이언트(FastAPI 앱)에 영향이 없습니다.
- **간단한 보안**: HTTP 서버로 노출하지 않으므로 외부에서 직접 접근할 수 없습니다.
- **포트 충돌 없음**: 추가 포트 설정이 필요하지 않습니다.

클라이언트(MCPAgentService)는 매 요청마다 `mcp_server.py`를 서브프로세스로 실행하고, stdin/stdout으로 명령을 주고받은 뒤 서브프로세스를 종료합니다. 처음에는 비효율적으로 보일 수 있지만, 이 방식이 격리와 안정성 측면에서 가장 단순한 접근입니다.

---

## 8.5 MCP 에이전트 서비스 구현

이 섹션이 이 장의 핵심입니다. `app/services/mcp_agent_service.py`는 MCP 서버를 실행하고, 도구를 LangChain Tool로 변환하고, ReAct 에이전트를 통해 질문에 답변하는 전체 흐름을 담당합니다.

### ReAct 에이전트란

**ReAct(Reason + Act)** 는 LLM이 도구를 사용할 때 따르는 추론 패턴입니다.

```
Question: 홍길동의 남은 연차는?
Thought: 먼저 홍길동의 직원 ID를 알아야 한다.
Action: list_employees
Action Input: {}
Observation: [{"id": 1, "name": "홍길동", "dept": "인사팀"}, ...]

Thought: id=1이 홍길동이다. 이제 휴가 잔여를 조회한다.
Action: get_leave_balance
Action Input: {"employee_id": 1}
Observation: {"total": 15, "used": 5, "remaining": 10}

Thought: 잔여 연차가 10일임을 확인했다.
Final Answer: 홍길동 님의 남은 연차는 10일입니다.
```

LLM이 "Thought → Action → Observation" 루프를 반복하며 스스로 도구 호출 순서를 결정합니다. 사용자가 복잡한 질문을 할 때에도 개발자가 분기 로직을 코드로 작성하지 않아도 됩니다. LLM이 상황에 따라 자율적으로 판단합니다.

### MCPToolWrapper — async를 sync로 변환하는 브릿지

MCP 도구는 비동기(`async`) 기반으로 설계되어 있습니다. 반면 LangChain의 기본 `Tool`은 동기(`sync`) 함수를 기대합니다. 두 방식의 불일치를 해결하는 것이 `MCPToolWrapper`의 역할입니다.

```python
# app/services/mcp_agent_service.py (MCPToolWrapper 핵심 발췌)

class MCPToolWrapper:
    """MCP 도구를 LangChain Tool로 변환하는 래퍼."""

    def __init__(self, session: Any, tool_info: Any) -> None:
        self.session = session
        self.tool_name = tool_info.name
        self.tool_description = tool_info.description or f"{tool_info.name} 도구"

    async def _call(self, **kwargs: Any) -> str:
        """MCP 도구를 비동기로 호출합니다."""
        try:
            result = await self.session.call_tool(self.tool_name, arguments=kwargs)
            content = result.content
            if isinstance(content, list) and content:
                return content[0].text if hasattr(content[0], "text") else str(content[0])
            return str(content)
        except Exception as exc:
            return f"도구 실행 오류: {exc}"

    def _sync_call(self, tool_input: str) -> str:
        """LangChain Tool에서 동기 호출하기 위한 래퍼입니다."""
        try:
            kwargs = json.loads(tool_input) if tool_input.strip() else {}
        except (json.JSONDecodeError, ValueError):
            kwargs = {"input": tool_input}

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, self._call(**kwargs))
                    result = future.result(timeout=30)
            else:
                result = loop.run_until_complete(self._call(**kwargs))
        except Exception as exc:
            result = f"비동기 실행 오류: {exc}"
        return result

    def to_langchain_tool(self) -> Tool:
        """LangChain Tool 객체로 변환합니다."""
        return Tool(
            name=self.tool_name,
            description=self.tool_description,
            func=self._sync_call,
        )
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: MCP `ClientSession` 객체와 `tool_info` (도구명, 설명, 스키마)
2. **처리(Process)**: `_call()`은 async로 MCP 서버를 호출하고, `_sync_call()`은 `asyncio.run()` 또는 `ThreadPoolExecutor`를 통해 이벤트 루프 충돌 없이 동기 브릿지를 제공. `to_langchain_tool()`이 LangChain `Tool` 객체로 변환
3. **출력(Output)**: `func=self._sync_call`이 연결된 LangChain `Tool` 객체

> **참고: asyncio 이벤트 루프 충돌 처리**
> FastAPI는 자체 이벤트 루프를 실행합니다. 이미 실행 중인 루프에서 `asyncio.run()`을 호출하면 `RuntimeError`가 발생합니다. `_sync_call()`은 이 상황을 감지하고, 이벤트 루프가 실행 중이면 `ThreadPoolExecutor`를 통해 별도 스레드에서 `asyncio.run()`을 호출합니다. 별도 스레드는 새로운 이벤트 루프를 가지므로 충돌이 발생하지 않습니다.

### MCPAgentService.run_agent() — 전체 실행 흐름

`MCPAgentService.run_agent()`는 한 번의 질문에 대해 다음 과정을 처리합니다.

```python
# app/services/mcp_agent_service.py (run_agent 핵심 발췌)

class MCPAgentService:

    def run_agent(self, query: str) -> dict:
        """MCP Agent를 실행하여 질문에 답변합니다."""

        async def _async_run() -> dict:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client

            # [1] MCP 서버 서브프로세스 실행
            server_params = StdioServerParameters(
                command=sys.executable,
                args=[_MCP_SERVER_PATH],
                env=None,
            )

            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    # [2] 도구 목록 수집 → MCPToolWrapper → LangChain Tools
                    tools_response = await session.list_tools()
                    langchain_tools = []
                    for tool_info in tools_response.tools:
                        wrapper = MCPToolWrapper(session, tool_info)
                        langchain_tools.append(wrapper.to_langchain_tool())

                    # [3] ReAct Agent 구성
                    agent = create_react_agent(
                        llm=llm_service.llm,
                        tools=langchain_tools,
                        prompt=REACT_PROMPT,
                    )

                    # [4] AgentExecutor 실행
                    executor = AgentExecutor(
                        agent=agent,
                        tools=langchain_tools,
                        verbose=True,
                        max_iterations=8,
                        handle_parsing_errors=True,
                        return_intermediate_steps=True,
                    )
                    result = executor.invoke({"input": query})

                    # [5] 중간 도구 호출 기록 정리
                    agent_steps = []
                    for action, observation in result.get("intermediate_steps", []):
                        agent_steps.append({
                            "tool": action.tool,
                            "input": action.tool_input,
                            "output": str(observation),
                        })

                    return {"answer": result.get("output", ""), "steps": agent_steps}

        result_dict = asyncio.run(_async_run())
        return result_dict


mcp_agent_service = MCPAgentService()
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 사용자 자연어 질문 문자열 (`query`)
2. **처리(Process)**:
   - `StdioServerParameters`로 `mcp_server.py`를 서브프로세스 실행
   - `session.list_tools()`로 9개 도구 목록 수집 후 `MCPToolWrapper`로 변환
   - `create_react_agent(llm, tools, REACT_PROMPT)`로 ReAct 에이전트 구성
   - `AgentExecutor.invoke({"input": query})`로 Thought→Action→Observation 루프 실행 (최대 8회)
3. **출력(Output)**: `{"answer": 최종 답변 문자열, "steps": [{"tool", "input", "output"} 목록]}`

> **주의: max_iterations 설정**
> `max_iterations=8`은 에이전트가 한 질문에 대해 최대 8번의 도구 호출을 허용합니다. 이 값을 너무 크게 설정하면 LLM이 불필요한 루프에 빠져 응답이 늦어집니다. 대부분의 질문은 2~3번 도구 호출로 해결되므로 8은 충분한 안전 마진입니다.

### REACT_PROMPT — ReAct 프롬프트 구조

```python
REACT_PROMPT = PromptTemplate.from_template(
    """다음 도구를 활용하여 질문에 답변하세요.

사용 가능한 도구:
{tools}

답변 형식을 반드시 준수하세요:
Question: 입력된 질문
Thought: 다음에 무엇을 해야 할지 생각합니다
Action: 사용할 도구 이름 [{tool_names}] 중 하나
Action Input: 도구에 전달할 JSON 입력
Observation: 도구 실행 결과
...(Thought/Action/Action Input/Observation을 필요한 만큼 반복)
Thought: 이제 최종 답변을 알았습니다
Final Answer: 한국어로 작성한 최종 답변

Question: {input}
Thought:{agent_scratchpad}"""
)
```

프롬프트에서 `{tools}`와 `{tool_names}` 플레이스홀더는 AgentExecutor가 실행 시점에 실제 도구 목록으로 채워 줍니다. `Final Answer:`로 시작하는 줄이 나타나면 AgentExecutor가 루프를 종료하고 해당 텍스트를 최종 답변으로 반환합니다.

전체 흐름을 한눈에 볼 수 있는 다이어그램입니다.

```mermaid
flowchart TD
    A["사용자 질문"] --> B["run_agent()"]
    B --> C["StdioServerParameters\nmcp_server.py 서브프로세스"]
    C --> D["list_tools()\n9개 도구 수집"]
    D --> E["MCPToolWrapper\nasync → sync 변환"]
    E --> F["create_react_agent\nReAct 루프"]
    F --> G["LLM Thought"]
    G --> H["도구 Action 실행"]
    H --> F
    F --> I["Final Answer 반환"]
```

*그림 8-6: MCPAgentService.run_agent() 실행 흐름*

---

## 8.6 FastAPI에 MCP Agent 통합

7장에서 만든 FastAPI 앱에 MCP Agent 탭을 추가합니다. 7장의 `/admin/qa/query` 엔드포인트는 그대로 유지하고, 새로운 `/admin/qa/agent` 엔드포인트만 추가합니다.

### POST /admin/qa/agent 엔드포인트

```python
# app/routers/qa.py (신규 엔드포인트)

@router.post("/admin/qa/agent")
async def query_agent(request: QueryRequest) -> dict:
    """
    MCP Agent 모드로 질문에 답변합니다.
    """
    query_text = request.query.strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="질의 내용이 비어 있습니다.")

    try:
        from app.services.mcp_agent_service import mcp_agent_service
        result = mcp_agent_service.run_agent(query_text)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"MCP Agent 실행 중 오류가 발생했습니다: {exc}",
        ) from exc

    return {
        "query": query_text,
        "answer": result.get("answer", ""),
        "steps": result.get("steps", []),
        "mode": "mcp_agent",
    }
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: `{"query": "홍길동의 남은 연차는?"}` 형태의 POST 요청
2. **처리(Process)**: `mcp_agent_service.run_agent(query_text)`를 호출하여 ReAct Agent 실행
3. **출력(Output)**: `{"query", "answer", "steps", "mode": "mcp_agent"}` — 최종 답변과 도구 사용 기록을 함께 반환

> **참고: import를 함수 안에서 하는 이유**
> `mcp_agent_service`는 임포트 시점에 LLM 서비스를 초기화합니다. FastAPI 앱 시작 시 전체 모듈을 일괄 임포트하면 LLM 초기화 오류가 앱 구동 자체를 막을 수 있습니다. 함수 내에서 임포트하면 실제 요청이 들어왔을 때 초기화를 시도하므로, 초기화 실패가 해당 엔드포인트의 500 오류로만 처리됩니다.

### agent.html — MCP Agent 채팅 UI

`app/templates/agent.html`은 MCP Agent 전용 채팅 화면을 제공합니다. RAG 채팅(`qa.html`)과 별도 탭으로 분리되어 있습니다.

주요 UI 구성 요소는 다음과 같습니다.

- 질문 입력창 및 전송 버튼
- 추천 질문 버튼 4개 (직원 목록, 휴가 잔여, 부서 매출, 최근 매출)
- 응답 영역: 최종 답변 텍스트
- "도구 사용 기록" 아코디언 (tool → input → output 순서)

```javascript
// app/static/js/agent.js (핵심 발췌)

async function sendAgentQuery() {
    const query = document.getElementById("query-input").value.trim();
    if (!query) return;

    // POST /admin/qa/agent 호출
    const response = await fetch("/admin/qa/agent", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({query})
    });

    const data = await response.json();

    // 최종 답변 렌더링
    renderAnswer(data.answer);

    // 도구 사용 기록 아코디언 렌더링
    if (data.steps && data.steps.length > 0) {
        renderSteps(data.steps);
    }
}
```

`data.steps` 배열에는 에이전트가 실행한 도구 호출 기록이 순서대로 담겨 있습니다. 아코디언 UI로 펼쳐 보면 LLM이 어떤 도구를 어떤 파라미터로 호출했고, 어떤 결과를 받았는지 추적할 수 있습니다. 디버깅과 신뢰성 검증 모두에 유용합니다.

### 브라우저에서 동작 확인

서버가 실행 중이라면 `http://127.0.0.1:8000/admin/agent` 에 접속하여 아래 질문들을 직접 입력해 보십시오.

| 질문 | 예상 도구 호출 경로 |
|------|-----------------|
| 전체 직원 목록을 보여주세요 | `list_employees()` → Final Answer |
| 홍길동의 남은 연차는? | `list_employees()` → `get_leave_balance(1)` → Final Answer |
| 영업팀의 총 매출은? | `get_sales_by_dept("영업팀")` → Final Answer |
| 최근 매출 10건을 보여주세요 | `list_sales(10)` → Final Answer |

<!-- [CAPTURE NEEDED: 08_agent_ui — http://127.0.0.1:8000/admin/agent 접속 후 "홍길동의 남은 연차는?"를 질문하고, 도구 사용 기록 아코디언이 펼쳐진 화면. list_employees와 get_leave_balance 두 도구 호출 기록이 표시된 상태] -->
*그림 8-7: MCP Agent 채팅 UI — 도구 사용 기록 아코디언*

### 전체 시스템 아키텍처 최종 확인

7장까지 구축한 RAG 경로와 8장에서 추가한 MCP Agent 경로가 하나의 FastAPI 앱 안에 공존합니다.

```mermaid
flowchart TD
    A["브라우저 사용자"] --> B["FastAPI\n(app/main.py)"]
    B --> C["POST /admin/qa/query\nRAG 경로 (CH07)"]
    B --> D["POST /admin/qa/agent\nMCP Agent 경로 (CH08)"]
    C --> E["QAService\nChromaDB + LLM"]
    D --> F["MCPAgentService\nReAct Agent"]
    F --> G["FastMCP 서버\n(서브프로세스)"]
    G --> H["PostgreSQL\n직원/휴가/매출"]
```

*그림 8-8: RAG 경로(CH07)와 MCP Agent 경로(CH08) 공존 구조*

### 자주 발생하는 오류와 해결법

| 오류 | 원인 | 해결 방법 |
|------|------|---------|
| `Connection refused (localhost:5432)` | PostgreSQL 컨테이너 미실행 | `docker-compose up -d` 재실행 |
| `MCP Server 시작 실패` | `mcp_server.py` 경로 오류 | `_MCP_SERVER_PATH` 경로 확인 (`mcp/mcp_server.py`) |
| `asyncio.run() cannot be called when another loop is running` | 이벤트 루프 충돌 | `ThreadPoolExecutor` 브릿지 코드가 없는 경우. `mcp_agent_service.py` 최신 버전 확인 |
| `AgentExecutor max_iterations reached` | LLM이 루프에서 빠져나오지 못함 | 프롬프트 언어 확인 (한국어 질문에 한국어 프롬프트 권장), `max_iterations` 값 증가 |
| `Ollama 연결 실패` | `ollama serve` 미실행 | `ollama serve` 실행 후 `ollama run deepseek-r1:1.5b` 확인 |

---

## 8.7 정리하며

이 장에서는 MCP 프로토콜을 활용하여 PostgreSQL DB 조회 도구를 노출하고, LangChain ReAct 에이전트가 자율적으로 도구를 선택·실행하는 시스템을 구현했습니다.

- **FastMCP로 MCP 서버를 빠르게 구현합니다**: `@mcp.tool()` 데코레이터 하나로 docstring과 타입 힌트가 JSON Schema로 자동 변환됩니다. 직원·휴가·매출 9개 도구를 등록하여 PostgreSQL을 MCP 프로토콜로 노출했습니다.

- **MCPToolWrapper가 async-sync 불일치를 해결합니다**: MCP 도구는 비동기 기반이고 LangChain Tool은 동기를 기대합니다. `_sync_call()`이 `asyncio.run()` 또는 `ThreadPoolExecutor`를 통해 이 불일치를 브릿지합니다. FastAPI 이벤트 루프와의 충돌도 이 방식으로 방지합니다.

- **ReAct 에이전트가 도구 호출 순서를 자율 결정합니다**: 사용자가 "홍길동의 연차"를 물으면 에이전트는 스스로 `list_employees()` → `get_leave_balance()` 순서로 도구를 호출합니다. 개발자가 분기 로직을 코드로 작성하지 않아도 됩니다.

- **stdio 모드로 서버-클라이언트를 격리합니다**: MCP 서버가 별도 서브프로세스로 실행되어, 서버 크래시가 FastAPI 앱에 영향을 주지 않습니다.

- **7장 RAG 경로와 8장 MCP 경로가 동일한 FastAPI 앱에 공존합니다**: `/admin/qa/query`(RAG)와 `/admin/qa/agent`(MCP Agent) 두 엔드포인트가 독립적으로 동작합니다.

다음 장 예고: 9장에서는 이 장에서 구현한 MCP 도구와 7장의 RAG Chain을 LangChain LCEL로 하나의 파이프라인으로 통합합니다. SQLiteCache로 응답 캐싱을 적용하고, MetricsCollector로 응답 시간과 캐시 히트율을 측정하는 운영 설정도 추가합니다.



---

# 9. LangChain 최종 연결

이 장에서는 지금까지 챕터별로 구축해 온 모든 구성 요소를 단일 파이프라인으로 통합합니다. 7장의 RAG Chain과 8장의 MCP Tool을 LangChain 표준 인터페이스인 **Tool** 규격으로 통일하고, **AgentExecutor(ReAct)** 가 질문에 따라 적절한 도구를 자동 선택하여 답변을 생성하도록 연결합니다. 또한 운영 환경에서 필수적인 Timeout, Retry, 로깅, 캐싱을 설정하고, 응답 시간과 캐시 히트율을 측정하는 모니터링 체계를 구축합니다.

이 장을 마치면 터미널 단 하나에서 "김철수의 남은 연차와 연차 규정을 알려줘" 같은 복합 질의에 정확하게 답변하는 AI 업무 비서 v2를 실행할 수 있습니다.

<!-- [IMAGE PLACEHOLDER: 09_chapter-overview — 9장 전체 구성요소 통합 흐름: 사용자 입력 → AgentExecutor → MCP Tools / RAG Tool → FastAPI / ChromaDB → 응답 합성] -->
*그림 9-1: 9장 통합 파이프라인 전체 구조*

---

## 1. Router / Agent / RAG Chain / MCP Tool 통합 구성

### 1.1 통합 아키텍처 개요

8장에서 설계한 MCP 에이전트는 FastMCP 서버를 서브프로세스로 실행하고 비동기 브릿지를 통해 도구를 호출하는 구조였습니다. 9장에서는 이 구조를 더 단순화합니다. **FastAPI REST API** 를 직접 호출하는 LangChain Tool 3종과 ChromaDB 검색 Tool 1종을 하나의 AgentExecutor에 등록하여, LLM이 자연어 질문을 분석하고 스스로 어떤 도구를 호출할지 판단하도록 합니다.

```mermaid
flowchart LR
    A["사용자 입력"] --> B["AgentExecutor"]
    B -- "DB 조회" --> C["MCP Tools\n(FastAPI)"]
    B -- "문서 검색" --> D["RAG Tool\n(ChromaDB)"]
    C --> E["응답 합성"]
    D --> E
    E --> F["최종 출력\n+ 메트릭"]
```

*그림 9-2: 통합 파이프라인 구성 — AgentExecutor가 MCP Tools와 RAG Tool을 자율 선택*

이 구조에서 **라우터(Router)** 는 별도 모듈이 아닙니다. ReAct 패턴의 에이전트 자체가 "어떤 도구를 쓸까"를 추론하는 과정이 곧 라우팅입니다. LLM이 질문을 보고 `Thought → Action → Observation` 루프를 반복하면서 필요한 도구를 순서대로 호출하고 결과를 취합해 최종 답변을 생성합니다.

> **참고: ReAct 패턴이란?**
> ReAct는 Reasoning(추론)과 Acting(행동)을 번갈아 수행하는 에이전트 패턴입니다. LLM이 먼저 `Thought`로 다음 행동을 계획하고, `Action`으로 도구를 호출하며, `Observation`으로 결과를 확인한 뒤 다시 추론하는 과정을 반복합니다. 이 사이클이 끝나면 `Final Answer`를 출력합니다.

### 1.2 실습 준비

실습을 시작하기 전에 전제 조건을 확인하십시오. 9장 실습은 CH04 FastAPI 서버와 CH07 ChromaDB가 이미 구동 중이어야 합니다.

**1단계: CH04 인프라 구동 확인**

```bash
cd rag-infra
docker-compose up -d
docker-compose ps
```

`fastapi_app`과 `postgres` 컨테이너가 모두 `Up` 상태인지 확인하십시오.

**2단계: CH07 ChromaDB 구축 확인**

```bash
cd CH07_RAG_QA엔진구현
python src/main.py  # 이미 실행했다면 건너뜁니다.
```

**3단계: 9장 예제 코드 Clone**

```bash
git clone https://github.com/{repo}/ch09-langchain-agent
cd ch09-langchain-agent
```

**4단계: 환경 변수 설정**

```bash
cp .env.example .env
```

`.env` 파일을 열어 아래 항목을 환경에 맞게 수정하십시오.

```env
# LLM Provider 설정 (ollama 또는 openai)
LLM_PROVIDER=ollama

# LLM 모델명
LLM_MODEL_NAME=deepseek-r1:1.5b

# Ollama 서버 URL
OLLAMA_BASE_URL=http://localhost:11434

# CH04 FastAPI 서버 URL
FASTAPI_BASE_URL=http://localhost:8000

# CH07 ChromaDB 경로
CHROMA_PERSIST_DIR=../CH07_RAG_QA엔진구현/data/chroma_db
COLLECTION_NAME=rag_docs
EMBED_MODEL=nomic-embed-text

# 운영 설정
LLM_TIMEOUT=60
MAX_RETRIES=2
ENABLE_CACHE=true
LOG_LEVEL=INFO
```

> **주의: CHROMA_PERSIST_DIR 경로**
> `CHROMA_PERSIST_DIR` 경로는 CH07 예제 코드의 ChromaDB 저장 경로와 일치해야 합니다. 경로가 다를 경우 ChromaDB 연결 오류가 발생합니다. CH07 실행 시 생성된 경로를 절대 경로로 입력하면 더 안전합니다.

**5단계: 패키지 설치 및 실행**

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 실행
PYTHONPATH=. python src/main.py
```

```bash
# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

set PYTHONPATH=.
python src/main.py
```

> **팁: PYTHONPATH 설정 이유**
> `PYTHONPATH=.` 는 프로젝트 루트 디렉토리를 Python 모듈 검색 경로에 추가합니다. `src/agent.py` 에서 `from src.config import ...` 같이 패키지를 임포트할 때 이 설정이 없으면 `ModuleNotFoundError` 가 발생합니다.

### 1.3 AgentExecutor 구성 코드 해설

에이전트의 핵심은 `src/agent.py`의 `build_agent()` 함수입니다. 전체 코드는 GitHub 레포를 참고하십시오. 여기서는 핵심 구성 부분만 발췌합니다.

```python
# src/agent.py (발췌)

def build_agent(config: AppConfig) -> AgentExecutor:
    """LangChain AgentExecutor를 구성하여 반환합니다."""

    # --- Input ---
    llm_config = config.llm

    # --- Process ---
    # 1. OllamaLLM 초기화 (timeout, max_retries 적용)
    llm = OllamaLLM(
        model=llm_config.model,
        base_url=llm_config.base_url,
        temperature=llm_config.temperature,
        timeout=llm_config.timeout,
        num_predict=1024,
    )

    # 2. Tool 목록: MCP_TOOLS(3종) + RAG_TOOL(1종)
    tools: list[BaseTool] = list(MCP_TOOLS) + [RAG_TOOL]

    # 3. ReAct 프롬프트 및 에이전트 생성
    prompt = PromptTemplate.from_template(_REACT_PROMPT_TEMPLATE)
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

    # 4. AgentExecutor 구성
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        max_iterations=5,
        verbose=True,
        handle_parsing_errors="에이전트가 올바른 형식으로 응답하지 못했습니다. 다시 시도합니다.",
        return_intermediate_steps=True,
    )

    # --- Output ---
    return agent_executor
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: `AppConfig` 객체 — LLM 설정(모델명, URL, timeout), 캐시 설정 포함
2. **처리(Process)**: OllamaLLM 초기화 → MCP Tool 3종 + RAG Tool 1종 목록 구성 → ReAct 프롬프트로 `create_react_agent()` 생성 → `AgentExecutor` 래핑 (최대 5회 반복, 중간 단계 반환 포함)
3. **출력(Output)**: 실행 준비 완료된 `AgentExecutor` 인스턴스

`max_iterations=5` 는 에이전트가 최대 5회의 Thought-Action-Observation 루프를 수행할 수 있다는 의미입니다. 복합 질의에서 도구를 2~3회 순차 호출하더라도 충분한 여유를 갖습니다. `return_intermediate_steps=True` 는 각 도구 호출 기록을 결과에 포함하여 어떤 도구가 어떤 순서로 호출되었는지 확인할 수 있도록 합니다.

---

## 2. MCP Tool 설계

### 2.1 LangChain Tool 규격으로 구현하는 이유

8장에서는 FastMCP 서버를 별도 프로세스로 실행하고 `MCPToolWrapper` 를 통해 비동기 함수를 동기식으로 변환하는 복잡한 브릿지 구조를 사용했습니다. 9장에서는 이를 단순화하여 **LangChain `@tool` 데코레이터** 를 직접 사용합니다.

LangChain Tool로 구현하면 두 가지 이점이 있습니다. 첫째, 별도 서버 프로세스 없이 동일 Python 프로세스 내에서 실행되어 구조가 단순해집니다. 둘째, `AgentExecutor` 가 Tool의 `name` 과 `description` 을 읽어 어떤 상황에서 이 도구를 써야 하는지 자동으로 판단할 수 있습니다. 도구 설명이 곧 라우팅 규칙이 됩니다.

<!-- [IMAGE PLACEHOLDER: 09_tool-routing — LangChain Agent가 Tool description을 읽어 자동 선택하는 흐름 다이어그램] -->
*그림 9-3: Tool description 기반 자동 도구 선택 흐름*

### 2.2 MCP Tools 구현 해설

`src/mcp_tools.py` 에는 CH04 FastAPI 서버를 호출하는 Tool 3종이 구현되어 있습니다. 전체 코드는 GitHub 레포를 참고하십시오. 핵심 패턴을 발췌합니다.

```python
# src/mcp_tools.py (발췌)

@tool
def get_leave_balance(employee_name: str) -> str:
    """직원의 잔여 연차를 조회합니다.

    CH04 FastAPI 서버의 GET /employees/{id}/leave-balance 엔드포인트를 호출합니다.
    이름으로 직원을 먼저 검색한 후 해당 직원의 연차 잔여 일수를 조회합니다.

    Args:
        employee_name: 조회할 직원의 이름 (예: "김철수").
    Returns:
        str: 잔여 연차 정보 문자열.
    """
    # --- Input ---
    # --- Process ---
    # 1단계: 이름으로 직원 ID 조회
    search_result = _get("/employees", params={"name": employee_name})
    if "error" in search_result:
        return search_result["error"]

    employees = search_result if isinstance(search_result, list) else \
                search_result.get("employees", [])
    employee = employees[0]
    employee_id = employee.get("id") or employee.get("employee_id")

    # 2단계: 연차 잔여 조회
    leave_result = _get(f"/employees/{employee_id}/leave-balance")
    remaining = leave_result.get("remaining_days", "알 수 없음")
    total = leave_result.get("total_days", "알 수 없음")
    used = leave_result.get("used_days", "알 수 없음")

    # --- Output ---
    return f"{employee_name} 님의 잔여 연차: {remaining}일 (총 {total}일 중 {used}일 사용)"
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: `employee_name` — 조회할 직원 이름 문자열 (예: "김철수")
2. **처리(Process)**: `/employees?name=김철수` 로 직원 ID 검색 → 검색 결과에서 첫 번째 직원 ID 추출 → `/employees/{id}/leave-balance` 로 연차 잔여 조회 → 포맷팅
3. **출력(Output)**: "김철수 님의 잔여 연차: 5일 (총 15일 중 10일 사용)" 형태의 문자열

나머지 두 도구도 같은 패턴을 따릅니다. `get_sales_summary()` 는 `/sales/summary` 엔드포인트를, `get_employee_info()` 는 `/employees` 엔드포인트를 호출합니다.

도구 함수의 **docstring** 이 특히 중요합니다. `@tool` 데코레이터는 함수 이름과 docstring을 읽어 LangChain Tool의 `name` 과 `description` 을 자동 생성합니다. 에이전트 LLM은 이 description을 보고 "연차를 조회해야 할 때는 `get_leave_balance` 를 쓰면 된다"고 판단합니다. 따라서 docstring을 명확하고 구체적으로 작성하는 것이 도구 선택 정확도를 높이는 핵심입니다.

### 2.3 RAG Tool 래핑

7장에서 구축한 ChromaDB 검색 기능은 `src/rag_tool.py` 에서 LangChain Tool 형태로 래핑됩니다.

```python
# src/rag_tool.py (발췌)

@tool
def search_company_documents(query: str) -> str:
    """사내 문서(규정, 가이드, 정책)를 검색하여 관련 내용을 반환합니다.

    CH07 ChromaDB에 저장된 사내 문서를 Ollama 임베딩 기반 유사도 검색으로 조회합니다.
    상위 3개 결과를 출처와 함께 반환합니다.

    Args:
        query: 검색할 내용 (예: "연차 신청 기한", "재택근무 정책").
    Returns:
        str: 관련 문서 내용과 출처 정보.
    """
    # --- Input ---
    k = 3

    # --- Process ---
    vectorstore = _build_retriever(k=k)
    docs = vectorstore.similarity_search(query, k=k)

    if not docs:
        return "관련 문서를 찾지 못했습니다."

    result_parts: list[str] = []
    for i, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source", "출처 미상")
        content = doc.page_content.strip()
        result_parts.append(f"[{i}] 출처: {source}\n내용: {content}")

    # --- Output ---
    return "\n\n".join(result_parts)
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: `query` — 검색할 자연어 질문 문자열 (예: "연차 신청 기한")
2. **처리(Process)**: `_build_retriever()` 로 ChromaDB 인스턴스 초기화 → `similarity_search(query, k=3)` 으로 상위 3개 유사 문서 검색 → 출처(`source`) 메타데이터와 본문을 포맷팅
3. **출력(Output)**: "[1] 출처: HR_취업규칙_v1.0.pdf\n내용: ..." 형태의 문자열

`_build_retriever()` 는 지연 임포트(lazy import) 패턴을 사용합니다. `chromadb` 와 `langchain_chroma` 를 모듈 로딩 시점이 아닌 실제 도구 호출 시점에 임포트합니다. Python 3.13 이상 환경에서 `chromadb` 의 pydantic v1 호환성 문제가 발생할 수 있는데, 지연 임포트를 통해 이 오류가 전체 애플리케이션 로딩을 방해하지 않도록 격리합니다.

> **팁: Python 버전 권장 사항**
> `chromadb` 라이브러리는 Python 3.9~3.12 환경에서 가장 안정적으로 동작합니다. Python 3.13 이상 환경에서는 pydantic v1 호환성 문제가 발생할 수 있습니다. `pyenv` 또는 `conda` 로 Python 3.11 환경을 별도 생성하여 실습하십시오.

---

## 3. 운영 설정 (Timeout, Retry, 로깅, 캐싱)

### 3.1 운영 설정이 필요한 이유

개발 환경에서는 응답이 느려도, 가끔 오류가 나도, 로그가 없어도 크게 문제가 되지 않습니다. 그러나 실제 업무 환경에서 사용되는 시스템에는 다음 상황이 반드시 발생합니다.

- **로컬 LLM 응답 시간 가변성**: DeepSeek R1은 질문의 복잡도와 하드웨어 상태에 따라 응답 시간이 2초에서 120초까지 크게 달라집니다. 적절한 Timeout 없이는 사용자가 무한히 기다리게 됩니다.
- **일시적 DB 연결 실패**: PostgreSQL이나 ChromaDB는 순간적인 연결 실패가 발생할 수 있습니다. 자동 Retry 없이는 사용자가 매번 재시도해야 합니다.
- **디버깅 기록 부재**: 오류 발생 시 어떤 도구가 어떤 입력으로 호출되었는지 로그 없이는 원인 파악이 불가능합니다.
- **반복 질의 비용**: 동일 질문을 반복할 때마다 LLM을 재실행하면 처리 시간이 낭비됩니다. 캐시로 즉시 반환할 수 있습니다.

### 3.2 설정 모듈 구조

`src/config.py` 는 이 모든 운영 설정을 **데이터클래스(dataclass)** 로 관리합니다.

```python
# src/config.py (발췌)

@dataclass
class LLMConfig:
    """LLM 연결 및 동작 설정을 담는 데이터 클래스입니다."""
    model: str
    provider: str
    base_url: str
    temperature: float = 0.1
    timeout: int = 60        # LLM 응답 대기 타임아웃 (초)
    max_retries: int = 2     # 실패 시 최대 재시도 횟수

@dataclass
class AppConfig:
    """애플리케이션 전체 설정을 담는 데이터 클래스입니다."""
    llm: LLMConfig
    log_level: str = "INFO"
    log_file: str = "./outputs/logs/app.log"
    enable_cache: bool = True
    cache_dir: str = "./outputs/cache"
    fastapi_base_url: str = "http://localhost:8000"
    chroma_persist_dir: str = "../CH07_RAG_QA엔진구현/data/chroma_db"
    collection_name: str = "rag_docs"
    embed_model: str = "nomic-embed-text"
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: `AppConfig` 와 `LLMConfig` 데이터클래스 정의 — 각 필드는 기본값을 가짐
2. **처리(Process)**: `load_config()` 함수가 `.env` 파일에서 환경 변수를 읽어 두 데이터클래스를 채운 뒤 캐시/로그 디렉토리를 자동 생성
3. **출력(Output)**: 모든 설정이 채워진 `AppConfig` 인스턴스

### 3.3 로깅 설정 — 콘솔 + 파일 동시 출력

`setup_logging()` 은 콘솔과 파일에 동시 출력하는 **듀얼 핸들러** 로거를 구성합니다.

```python
# src/config.py (발췌) — setup_logging()

def setup_logging(config: AppConfig) -> logging.Logger:
    """파일과 콘솔에 동시 출력하는 듀얼 핸들러 로거를 설정합니다."""

    # --- Input ---
    log_format = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
    level = getattr(logging, config.log_level, logging.INFO)

    # --- Process ---
    logger = logging.getLogger("ch09")
    logger.setLevel(level)

    formatter = logging.Formatter(fmt=log_format, datefmt="%Y-%m-%d %H:%M:%S")

    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 파일 핸들러
    file_handler = logging.FileHandler(config.log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # --- Output ---
    return logger
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: `AppConfig` — `log_level` (INFO/DEBUG/WARNING) 과 `log_file` 경로 포함
2. **처리(Process)**: `ch09` 이름의 루트 로거 생성 → 콘솔 핸들러(실시간 확인) + 파일 핸들러(영구 기록) 동시 등록 → 동일 포맷 적용
3. **출력(Output)**: 설정 완료된 `logging.Logger` 인스턴스 — `logger.info()`, `logger.error()` 등 사용 가능

`outputs/logs/app.log` 에 기록된 로그를 통해 어떤 도구가 어떤 순서로 호출되었는지, 응답 시간이 얼마나 걸렸는지 추적할 수 있습니다.

### 3.4 캐시 설정 — SQLiteCache

`setup_cache()` 는 LangChain의 **SQLiteCache** 를 전역 LLM 캐시로 등록합니다.

```python
# src/config.py (발췌) — setup_cache()

def setup_cache(config: AppConfig) -> None:
    """LangChain SQLiteCache를 전역 LLM 캐시로 등록합니다."""

    # --- Input ---
    if not config.enable_cache:
        return

    # --- Process ---
    from langchain_community.cache import SQLiteCache
    import langchain

    cache_path = os.path.join(config.cache_dir, "langchain_cache.db")
    cache = SQLiteCache(database_path=cache_path)
    langchain.llm_cache = cache
    print(f"[Config] LangChain SQLiteCache 활성화 — {cache_path}")

    # --- Output ---
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: `AppConfig.enable_cache` (True/False) 와 `cache_dir` 경로
2. **처리(Process)**: `SQLiteCache` 인스턴스를 `cache_dir/langchain_cache.db` 에 생성 → `langchain.llm_cache` 에 전역 등록
3. **출력(Output)**: `None` — 사이드 이펙트로 이후 모든 LLM 호출에 캐시가 자동 적용됨

캐시가 활성화되면 동일한 프롬프트로 LLM을 재호출할 때 실제 LLM 추론을 건너뛰고 SQLite 데이터베이스에서 이전 응답을 즉시 반환합니다. 응답 시간이 수십 초에서 0.01초로 줄어드는 효과를 직접 확인할 수 있습니다.

> **참고: LangChain 캐시의 키(Key) 전략**
> LangChain SQLiteCache는 프롬프트 문자열 전체를 해시 키로 사용합니다. 질문이 한 글자라도 다르면 캐시 MISS로 처리됩니다. "김철수 남은 연차" 와 "김철수 잔여 연차" 는 서로 다른 캐시 키입니다. 반복 질의가 많은 FAQ 시나리오에서 가장 효과적입니다.

---

## 4. 비용 관리 및 토큰 모니터링

### 4.1 로컬 LLM에서도 모니터링이 필요한 이유

클라우드 API를 사용하지 않는 로컬 LLM 환경에서는 금전적 비용이 없으므로 모니터링이 불필요하다고 생각하기 쉽습니다. 그러나 로컬 환경에서도 다음 자원은 유한합니다.

- **GPU 메모리(VRAM)**: DeepSeek R1 모델 구동에 최소 4~8GB VRAM이 필요합니다. 컨텍스트가 너무 길면 메모리가 부족해 응답이 지연되거나 실패합니다.
- **처리 시간(Latency)**: 로컬 LLM은 CPU/GPU 성능에 따라 응답 시간 편차가 큽니다. 어떤 질문 유형에서 느려지는지 파악해야 시스템을 개선할 수 있습니다.
- **캐시 효율**: 캐시 히트율이 낮다면 불필요한 LLM 재실행이 많다는 의미입니다. 질문 패턴을 분석해 캐시 전략을 개선할 수 있습니다.

### 4.2 MetricsCollector 구현

`src/monitor.py` 의 `MetricsCollector` 클래스는 각 요청에 대한 측정값을 수집하고 세션 종료 시 요약 통계를 출력합니다.

```python
# src/monitor.py (발췌)

@dataclass
class RequestMetrics:
    """단일 요청에 대한 측정값을 담는 데이터 클래스입니다."""
    question: str
    response_time_ms: int       # 에이전트 실행 전체 소요 시간 (밀리초)
    tool_calls: list[str]       # 호출된 Tool 이름 목록
    cached: bool                # LangChain 캐시에서 응답이 반환된 경우 True


class MetricsCollector:
    """요청 메트릭을 수집하고 요약 통계를 제공합니다."""

    def __init__(self) -> None:
        self._records: list[RequestMetrics] = []

    def record(self, metrics: RequestMetrics) -> None:
        """단일 요청 메트릭을 수집 목록에 추가합니다."""
        self._records.append(metrics)

    def summary(self) -> dict:
        """수집된 메트릭 전체에 대한 요약 통계를 반환합니다."""
        # --- Input ---
        total = len(self._records)
        if total == 0:
            return {"total_requests": 0, "avg_response_ms": 0.0,
                    "cache_hit_rate": 0.0, "tool_usage": {}}

        # --- Process ---
        avg_ms = sum(r.response_time_ms for r in self._records) / total
        cache_hits = sum(1 for r in self._records if r.cached)
        cache_hit_rate = cache_hits / total

        tool_usage: dict[str, int] = {}
        for record in self._records:
            for tool_name in record.tool_calls:
                tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1

        # --- Output ---
        return {
            "total_requests": total,
            "avg_response_ms": round(avg_ms, 2),
            "cache_hit_rate": round(cache_hit_rate, 4),
            "tool_usage": tool_usage,
        }
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 각 요청 완료 시 `RequestMetrics` 객체 — 질문, 응답 시간(ms), 호출된 Tool 목록, 캐시 히트 여부
2. **처리(Process)**: `_records` 목록에 누적 → `summary()` 호출 시 전체 평균 응답 시간 계산, 캐시 히트 수/전체 요청 수로 히트율 계산, Tool별 호출 횟수 집계
3. **출력(Output)**: `{"total_requests": N, "avg_response_ms": X.X, "cache_hit_rate": 0.XX, "tool_usage": {...}}` 딕셔너리

### 4.3 에이전트 실행과 메트릭 수집 통합

`src/agent.py` 의 `run_with_metrics()` 함수는 에이전트 실행과 메트릭 수집을 하나의 함수로 통합합니다.

```python
# src/agent.py (발췌) — run_with_metrics()

def run_with_metrics(
    agent: AgentExecutor,
    question: str,
    collector: MetricsCollector,
    session_id: str = "default",
) -> str:
    """메트릭을 수집하며 에이전트를 실행하고 최종 답변을 반환합니다."""

    # --- Input ---
    start_time = time.time()
    tool_calls: list[str] = []

    # --- Process ---
    result: dict = agent.invoke({"input": question})
    answer: str = result.get("output", "답변을 생성하지 못했습니다.")

    # 중간 실행 단계에서 호출된 Tool 이름 수집
    intermediate_steps = result.get("intermediate_steps", [])
    for action, _observation in intermediate_steps:
        tool_name = getattr(action, "tool", None)
        if tool_name and tool_name not in tool_calls:
            tool_calls.append(tool_name)

    elapsed_ms = int((time.time() - start_time) * 1000)

    # 응답 시간이 0.5초 미만이면 캐시 히트로 판단
    cached = elapsed_ms < 500

    collector.record(RequestMetrics(
        question=question,
        response_time_ms=elapsed_ms,
        tool_calls=tool_calls,
        cached=cached,
    ))

    cache_label = "HIT" if cached else "MISS"
    print(f"\n응답 시간: {elapsed_ms / 1000:.1f}초 | 캐시: {cache_label}")
    if tool_calls:
        print(f"호출된 도구: {', '.join(tool_calls)}")

    # --- Output ---
    return answer
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: `AgentExecutor` 인스턴스, 사용자 질문 문자열, `MetricsCollector` 인스턴스
2. **처리(Process)**: `time.time()` 으로 시작 시간 기록 → `agent.invoke()` 실행 → `intermediate_steps` 에서 호출된 Tool 이름 추출 → 경과 시간 계산 (0.5초 미만이면 캐시 HIT 판정) → `MetricsCollector.record()` 에 측정값 기록
3. **출력(Output)**: 최종 답변 문자열 (오류 발생 시 한국어 오류 안내 메시지 반환)

### 4.4 대화 루프와 세션 통계

`src/main.py` 는 대화 루프의 진입점입니다. 사용자가 `exit` 또는 `quit` 을 입력하면 세션 통계가 출력됩니다.

```python
# src/main.py (발췌)

def main() -> None:
    """AI 업무 비서 v2 메인 진입점입니다."""

    # --- Input ---
    config = load_config()

    # --- Process ---
    setup_cache(config)         # SQLiteCache 초기화
    print_header(config)        # 설정 정보 헤더 출력
    run_conversation_loop(config)  # 대화 루프 실행

    # --- Output ---
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: `.env` 파일 — 모든 설정값의 원천
2. **처리(Process)**: `load_config()` 로 설정 로드 → `setup_cache()` 로 SQLiteCache 초기화 → `print_header()` 로 시작 화면 출력 → `run_conversation_loop()` 로 반복 질의 응답
3. **출력(Output)**: 종료 시 `MetricsCollector.print_summary()` 로 세션 통계 콘솔 출력

### 4.5 실행 결과 확인

`PYTHONPATH=. python src/main.py` 실행 시 아래와 같은 출력이 나타납니다.

```
==================================================
  AI 업무 비서 v2 (LangChain Agent)
==================================================
  설정: deepseek-r1:1.5b | Timeout 60s | 캐시 ON
  도구: 연차 조회 / 매출 조회 / 직원 정보 / 사내 문서 검색
  종료: 'exit' 또는 'quit' 입력
==================================================
[Config] LangChain SQLiteCache 활성화 — ./outputs/cache/langchain_cache.db

준비 완료. 질문을 입력하십시오.

질문: 김철수 남은 연차와 연차 규정 알려줘

> Entering new AgentExecutor chain...
Thought: 두 가지 정보가 필요합니다. 잔여 연차는 get_leave_balance 도구로,
         연차 규정은 search_company_documents 도구로 조회합니다.
Action: get_leave_balance
Action Input: 김철수
Observation: 김철수 님의 잔여 연차: 5일 (총 15일 중 10일 사용)
Thought: 이제 연차 규정 문서를 검색합니다.
Action: search_company_documents
Action Input: 연차 신청 규정
Observation: [1] 출처: HR_취업규칙_v1.0.pdf
내용: 연차는 발생일로부터 1년 이내에 사용하여야 합니다. 미사용 연차는 연차수당으로 지급됩니다.
Thought: 이제 최종 답변을 작성할 수 있습니다.
Final Answer: 김철수 님의 잔여 연차는 5일입니다 (총 15일 중 10일 사용).
연차 규정에 따르면 연차는 발생일로부터 1년 이내에 사용하셔야 합니다.
미사용 연차는 연차수당으로 지급됩니다.

> Finished chain.

응답 시간: 4.2초 | 캐시: MISS
호출된 도구: get_leave_balance, search_company_documents

답변: 김철수 님의 잔여 연차는 5일입니다 (총 15일 중 10일 사용).
연차 규정에 따르면 연차는 발생일로부터 1년 이내에 사용하셔야 합니다.
미사용 연차는 연차수당으로 지급됩니다.
```

<!-- [CAPTURE NEEDED: 09_agent-run — PYTHONPATH=. python src/main.py 실행 후 터미널 전체 화면 — AgentExecutor 헤더, ReAct Thought/Action/Observation 루프, 최종 답변, 응답 시간 및 캐시 MISS 표시] -->
*그림 9-4: AI 업무 비서 v2 실행 결과 — ReAct 루프에서 두 도구를 순차 호출*

이제 동일한 질문을 다시 입력하면 캐시 HIT 효과를 확인할 수 있습니다.

```
질문: 김철수 남은 연차와 연차 규정 알려줘

답변: 김철수 님의 잔여 연차는 5일입니다 (총 15일 중 10일 사용). ...

응답 시간: 0.0초 | 캐시: HIT
```

4.2초 걸리던 응답이 캐시 HIT 후에는 0.0초로 즉시 반환됩니다. SQLiteCache가 프롬프트를 키로 이전 응답을 저장해 두었기 때문입니다.

`exit` 을 입력하면 세션 통계가 출력됩니다.

```
==================================================
  세션 통계 요약
==================================================
  총 요청 수     : 2회
  평균 응답 시간 : 2100.0ms
  캐시 히트율    : 50.0%
  도구별 호출 횟수:
    - get_leave_balance: 1회
    - search_company_documents: 1회
==================================================
```

이 통계를 통해 어떤 도구가 가장 많이 호출되는지, 캐시 히트율이 충분한지 확인하고 개선 방향을 결정할 수 있습니다.

### 4.6 자주 발생하는 오류와 해결법

실습 중 발생할 수 있는 주요 오류와 해결 방법을 정리합니다.

| 오류 메시지 | 원인 | 해결법 |
|------------|------|--------|
| `ConnectionRefusedError: [Errno 111]` | Ollama 서버 미실행 | `ollama serve` 실행 후 재시도 |
| `FastAPI 서버에 연결할 수 없습니다` | CH04 docker-compose 미실행 | `cd rag-infra && docker-compose up -d` |
| `ChromaDB 연결에 실패했습니다` | CH07 ChromaDB 미구축 또는 경로 불일치 | `.env` 의 `CHROMA_PERSIST_DIR` 절대 경로 확인 |
| `ModuleNotFoundError: No module named 'src'` | PYTHONPATH 미설정 | `PYTHONPATH=. python src/main.py` 로 실행 |
| `pydantic v1 호환성 오류` | Python 3.13 환경 | Python 3.11 환경으로 전환 |
| `AgentExecutor: max_iterations reached` | 에이전트가 5회 반복 내 답변 생성 실패 | 질문을 더 명확하게 재입력, 또는 LLM 모델 확인 |

> **주의: 에이전트가 답변을 생성하지 못하는 경우**
> 로컬 LLM은 복잡한 ReAct 형식 준수에 어려움을 겪을 수 있습니다. `handle_parsing_errors` 파라미터가 파싱 오류를 자동으로 처리하지만, 반복적으로 실패한다면 더 큰 모델(`deepseek-r1:8b` 이상)로 전환하거나 프롬프트를 단순화하십시오.

---

## 5. 정리하며

이 장에서는 지금까지 구축한 모든 구성 요소를 하나의 통합 파이프라인으로 완성했습니다.

- **LangChain Tool 표준화**: FastAPI REST API 호출(MCP Tool 3종)과 ChromaDB 검색(RAG Tool 1종)을 `@tool` 데코레이터로 LangChain 표준 인터페이스로 통일했습니다. AgentExecutor는 Tool의 docstring을 읽어 적절한 도구를 자동 선택합니다. docstring의 품질이 곧 라우팅 정확도입니다.

- **ReAct 에이전트 자율 라우팅**: `create_react_agent()` 와 `AgentExecutor` 를 조합하여 별도의 라우터 모듈 없이 LLM 자체가 `Thought → Action → Observation` 루프를 통해 복수 도구를 순서대로 호출하고 응답을 합성합니다. "김철수의 남은 연차와 연차 규정" 같은 복합 질의도 단일 입력으로 처리됩니다.

- **SQLiteCache 캐싱**: 동일 프롬프트 재질의 시 LLM 추론을 건너뛰고 SQLite에서 즉시 반환합니다. 4초 응답이 0.01초로 단축되는 효과를 직접 확인했습니다. 로컬 LLM 환경에서도 반복 질의가 많은 FAQ 시나리오에서 매우 효과적입니다.

- **MetricsCollector 모니터링**: 응답 시간, 도구 호출 횟수, 캐시 히트율을 세션 단위로 수집하고 세션 종료 시 요약 통계를 출력합니다. 어떤 도구가 병목인지, 캐시 전략이 효과적인지 데이터 기반으로 판단할 수 있습니다.

- **운영 설정 데이터클래스 분리**: `AppConfig` 와 `LLMConfig` 를 통해 모든 운영 설정을 `.env` 파일 하나로 관리합니다. 로컬 LLM을 클라우드 API로 전환할 때도 `LLM_PROVIDER=openai` 환경 변수 하나만 변경하면 됩니다.

이 장으로 AI 업무 비서의 핵심 파이프라인이 완성되었습니다. 다음 10장에서는 이 파이프라인의 성능을 정량적으로 측정하고 개선하는 방법을 학습합니다. Retrieval 정확도, Hallucination Rate, 청크 크기 최적화, ReRanker 적용 등 튜닝 기법을 통해 AI 업무 비서를 더 정확하고 빠르게 만들 수 있습니다.



---

# 10. RAG 시스템 튜닝

이 장에서는 9장까지 완성한 RAG 파이프라인의 성능을 측정하고, 구체적인 증상에 따라 어떻게 개선하는지를 학습합니다. "성능이 안 좋다"는 막연한 진단에서 벗어나 증상별 원인 진단 → 튜닝 적용 → 정량 평가의 체계적 접근 방식을 익힙니다.

9장에서 LangChain LCEL로 통합된 파이프라인이 완성되었습니다. 하지만 완성된 파이프라인이 곧 "잘 동작하는 파이프라인"을 의미하지는 않습니다. RAG 시스템에는 청크 크기, 검색 개수, 프롬프트 전략, 검색 방식 등 수십 개의 조정 가능한 변수가 있으며, 이 변수들의 조합이 최종 응답 품질을 결정합니다. 이 장에서는 다섯 가지 튜닝 영역을 순서대로 다루고, 마지막으로 정량 평가 체계를 구축하여 개선 효과를 수치로 확인합니다.

<!-- [IMAGE PLACEHOLDER: 10_chapter-overview — 10장 전체 구조: 증상 진단 → 청크·리트리버 튜닝 → 고급 검색(ReRanker/Hybrid) → 프롬프트 튜닝 → OCR → 평가 리포트 흐름도] -->
*그림 10-1: 10장 튜닝 파이프라인 전체 흐름*

---

## 1. 증상별 튜닝 가이드

RAG 시스템 튜닝의 출발점은 증상 관찰입니다. "정확도가 낮다"는 결론보다 "어떤 질문에서 어떤 방식으로 실패하는가"를 먼저 파악해야 올바른 처방을 내릴 수 있습니다. 병원에서 "몸이 안 좋다"는 말로는 어떤 약도 처방받을 수 없는 것과 같습니다.

### 1.1 증상-원인-해결 매트릭스

아래 표는 RAG 시스템에서 흔히 관찰되는 증상과 그 원인, 그리고 이 장에서 다루는 해결책을 정리한 것입니다.

| 증상 | 원인 추정 | 진단 방법 | 해결책 |
|------|---------|---------|------|
| 응답에 문서와 다른 내용 포함 | 환각(Hallucination) | Hallucination Rate 측정 | 프롬프트 튜닝(근거 우선 / 무지 인정) |
| "잘 모르겠다"는 답변이 자주 나옴 | 검색 문서와 질문 불일치 | Retrieval Accuracy 측정 | Chunk 크기 조정, k값 증가, Hybrid Search |
| 엉뚱한 부서 문서가 검색됨 | 메타데이터 필터 미적용 | 검색 결과 수동 확인 | Metadata Filtering 적용 |
| 맥락이 잘리는 답변 | 청크 크기가 너무 작음 | 청크 평균 길이 측정 | 청크 크기 증가, Parent Document Retriever |
| 핵심 키워드가 검색되지 않음 | 벡터 유사도 약점 | BM25 단독 검색 비교 | Hybrid Search(BM25 + 벡터) |
| 1차 검색 결과는 맞지만 최종 답이 틀림 | LLM 컨텍스트 활용 실패 | 컨텍스트 직접 주입 테스트 | ReRanker로 품질 높은 문서 상위 배치 |
| 스캔 PDF에서 텍스트 추출 실패 | 이미지 기반 PDF | pdfplumber 출력 확인 | EasyOCR + LLaVA 하이브리드 OCR |
| 응답 생성이 10초 이상 걸림 | k값이 너무 크거나 모델 부하 | 응답 시간 로그 측정 | k값 축소, 캐싱, 모델 크기 조정 |

> **참고: 진단 우선, 튜닝 나중**
> 위 표의 "진단 방법"을 먼저 적용하십시오. 원인을 확인하지 않은 상태에서 무분별하게 설정을 변경하면 오히려 성능이 하락할 수 있습니다.

### 1.2 체크포인트별 빠른 진단

증상을 파악했다면 아래 3단계 순서로 빠르게 진단하십시오.

**1단계: Retrieval 확인**
검색된 문서가 질문과 관련 있는지 수동으로 확인합니다. `retriever.invoke("질문")` 결과를 직접 출력하여 반환 문서 내용을 살펴보십시오. 이 단계에서 문제가 발견되면 청크 / 리트리버 튜닝(2절)이 필요합니다.

**2단계: 프롬프트 확인**
검색 문서는 맞지만 최종 답변이 틀린 경우, 프롬프트 튜닝(4절)이 필요합니다. 같은 컨텍스트를 직접 붙여넣어 질문했을 때 올바른 답이 나오는지 확인합니다.

**3단계: 정량 평가**
수동 확인 이후에는 6절의 평가 체계로 개선 전후의 수치를 비교하십시오. 감각이 아닌 수치로 검증하는 것이 재발 방지의 핵심입니다.

---

## 2. Chunk / Retriever 튜닝

### 2.1 실습 준비

이 장의 예제 코드를 클론합니다.

```bash
git clone https://github.com/{repo}/ch10-rag-tuning
cd ch10-rag-tuning
```

환경 변수 파일을 복사하고 값을 입력합니다.

```bash
cp .env.example .env
```

`.env` 파일을 열어 Ollama 모델명과 ChromaDB 경로를 설정합니다. 9장의 ChromaDB를 재사용하는 경우 `CHROMA_PERSIST_DIR`을 CH09 레포의 경로로 변경하십시오.

```ini
# .env 핵심 설정
LLM_MODEL_NAME=deepseek-r1:1.5b
OLLAMA_BASE_URL=http://localhost:11434
EMBED_MODEL=nomic-embed-text
CHROMA_PERSIST_DIR=./data/chroma_db
RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
```

패키지를 설치합니다.

```bash
pip install -r requirements.txt
```

`requirements.txt`에는 기존 LangChain, ChromaDB 외에 세 개의 패키지가 추가되었습니다. `sentence-transformers`는 CrossEncoder ReRanker에 필요하고, `rank-bm25`는 Hybrid Search의 BM25 키워드 검색에, `easyocr`과 `pymupdf`는 스캔 PDF 처리에 사용합니다.

### 2.2 청킹 전략 비교 실험

6장에서 청킹의 기본 개념을 학습했습니다. 이 절에서는 청크 설정이 실제 검색 정확도에 어떤 영향을 미치는지 실험으로 확인합니다.

`src/tuning/chunker_tuning.py`는 5가지 실험 설정을 순차 실행하고 각 설정의 **Precision@K** (상위 k개 결과 중 정답 포함 비율)와 응답 시간을 측정합니다.

```python
# src/tuning/chunker_tuning.py — 실험 설정 정의

@dataclass
class ChunkExperiment:
    chunk_size: int   # 각 청크의 최대 문자 수
    overlap: int      # 인접 청크 간 중복 문자 수
    k: int            # 검색 시 반환할 상위 문서 수
    strategy: str     # "fixed" | "semantic"

EXPERIMENTS: list[ChunkExperiment] = [
    ChunkExperiment(chunk_size=200, overlap=20,  k=3, strategy="fixed"),
    ChunkExperiment(chunk_size=500, overlap=50,  k=3, strategy="fixed"),   # 기본값
    ChunkExperiment(chunk_size=800, overlap=100, k=3, strategy="fixed"),
    ChunkExperiment(chunk_size=500, overlap=50,  k=5, strategy="fixed"),
    ChunkExperiment(chunk_size=500, overlap=50,  k=3, strategy="semantic"),
]
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: `ChunkExperiment` 설정 5가지 — chunk_size, overlap, k값, 전략 조합
2. **처리(Process)**: 각 설정으로 ChromaDB를 재구축한 뒤, 샘플 질문 5개로 검색을 실행하여 정답 문서 포함 여부를 비교
3. **출력(Output)**: 설정별 Precision@K와 평균 응답 시간(ms) — `outputs/tuning_logs/chunk_tuning_{타임스탬프}.json`

`strategy="semantic"` 설정은 단순히 글자 수로 자르는 것이 아니라 문장 경계(`.`)를 기준으로 의미 단위를 유지하며 청크를 구성합니다. 사내 규정처럼 단문이 많은 문서에서는 이 방식이 문맥을 온전히 보존하여 검색 정밀도를 높입니다.

튜닝 실험을 실행합니다.

```bash
python src/main.py --mode tune
```

출력 예시는 아래와 같습니다.

```
============================================================
청크 튜닝 실험 시작
============================================================

[실험] chunk_size=200, overlap=20, k=3, strategy=fixed
  Precision@3: 60.0%  |  평균 응답: 142.3ms

[실험] chunk_size=500, overlap=50, k=3, strategy=fixed
  Precision@3: 80.0%  |  평균 응답: 148.7ms

[실험] chunk_size=800, overlap=100, k=3, strategy=fixed
  Precision@3: 80.0%  |  평균 응답: 152.1ms

[실험] chunk_size=500, overlap=50, k=5, strategy=fixed
  Precision@5: 100.0%  |  평균 응답: 156.4ms

[실험] chunk_size=500, overlap=50, k=3, strategy=semantic
  Precision@3: 100.0%  |  평균 응답: 144.8ms

============================================================
실험 결과 요약
============================================================
최고 설정: chunk_size=500, overlap=50, k=5, strategy=fixed
Precision@K: 100.0%
결과 저장: outputs/tuning_logs/chunk_tuning_20260226_120000.json
```

<!-- [CAPTURE NEEDED: 10_chunk-tuning — python src/main.py --mode tune 실행 후 터미널 전체 화면 (실험 결과 요약 포함)] -->
*그림 10-2: 청크 튜닝 실험 결과 출력 화면*

### 2.3 실험 결과 해석

| chunk_size | overlap | k | strategy | Precision@K | 평균 응답(ms) |
|-----------|---------|---|----------|------------|-------------|
| 200 | 20 | 3 | fixed | 60.0% | 142 |
| 500 | 50 | 3 | fixed | 80.0% | 149 |
| 800 | 100 | 3 | fixed | 80.0% | 152 |
| 500 | 50 | 5 | fixed | 100.0% | 156 |
| 500 | 50 | 3 | semantic | 100.0% | 145 |

실험 결과에서 세 가지 패턴이 나타납니다.

**chunk_size=200이 가장 나쁜 이유**: 청크가 너무 작으면 단일 규정 문장이 두 청크로 분리됩니다. "연차 신청은 / 전월 말일까지 팀장에게 제출해야 합니다"처럼 의미가 잘리면 벡터 임베딩이 부분 문장의 의미만 포착하여 검색 정밀도가 하락합니다.

**k=5가 k=3보다 유리한 경우**: 검색 범위를 넓히면 정답 문서가 포함될 가능성이 높아집니다. 단, k가 커질수록 프롬프트에 주입되는 컨텍스트 길이가 늘어나 응답 시간이 증가합니다. 문서 수가 많을수록 k=3에서 k=5로의 전환 효과가 큽니다.

**semantic 청킹의 장점**: 동일한 chunk_size=500이지만 문장 경계를 보존하는 semantic 방식이 fixed 방식 대비 동등하거나 더 나은 정밀도를 보입니다. 사내 규정처럼 단문 중심 문서에 특히 효과적입니다.

> **팁: 최적 설정 선택 기준**
> 정확도와 응답 속도 사이의 트레이드오프를 고려하십시오. 실시간 서비스에서는 응답 시간이 중요하므로 k=3, semantic 전략이 합리적입니다. 야간 배치 처리라면 k=5로 설정하여 정확도를 최대화하십시오.

### 2.4 Metadata Filtering 적용

부서별로 문서를 구분하여 저장한 경우(6장 ChromaDB 메타데이터), 검색 시 필터를 적용하면 정밀도를 크게 높일 수 있습니다.

```python
# 부서 필터 적용 검색 예시
retriever = vectorstore.as_retriever(
    search_kwargs={
        "k": 3,
        "filter": {"department": "hr"}  # HR 부서 문서만 검색
    }
)
```

"연차 규정은?"이라는 질문에 HR 필터를 적용하면 영업팀, IT팀 문서가 검색 결과에 포함되는 것을 차단하여 관련도 높은 문서만 반환합니다. 이 방식은 별도 코드 없이 ChromaDB의 메타데이터 필드만으로 구현 가능합니다.

---

## 3. 고급 기술: ReRanker와 Hybrid Search

1차 벡터 검색으로도 정확도를 높이는 데 한계가 있는 두 가지 상황이 있습니다.

첫 번째는 **의미는 비슷하지만 내용이 다른 문서**가 상위에 오는 경우입니다. 예를 들어 "병가 절차는?"이라는 질문에 "연차 절차"와 "병가 절차" 문서가 모두 높은 벡터 유사도를 가질 수 있습니다. 이 경우 ReRanker가 쌍별 점수를 계산하여 더 관련 있는 문서를 상위로 끌어올립니다.

두 번째는 **고유명사나 코드번호처럼 정확한 키워드 매칭이 중요한 경우**입니다. 벡터 검색은 "HR-2025-012"와 "HR-2025-015"를 의미적으로 거의 동일하게 취급하지만, BM25는 정확한 문자열 일치 여부로 구분합니다.

### 3.1 ReRanker 구현

**ReRanker(재순위화기)** 는 1차 검색 결과를 다시 평가하여 가장 관련도 높은 문서를 상위에 배치하는 모델입니다. 도서관에서 "비슷한 주제의 책" 목록(1차 검색)을 받은 뒤, 사서가 목록을 다시 검토하여 실제로 필요한 책을 골라내는(재순위화) 과정과 같습니다.

```python
# src/tuning/reranker.py — CrossEncoder ReRanker 핵심 로직

def rerank_with_cross_encoder(
    query: str,
    documents: list[str],
    top_k: int = 3,
) -> list[dict[str, Any]]:
    """CrossEncoder로 1차 검색 결과를 재순위화합니다."""

    # --- Input ---
    # query: 사용자 검색 질의
    # documents: 1차 검색에서 반환된 문서 텍스트 리스트 (k=10 권장)

    # --- Process ---
    from sentence_transformers import CrossEncoder
    model = CrossEncoder(RERANKER_MODEL)  # cross-encoder/ms-marco-MiniLM-L-6-v2

    pairs = [(query, doc) for doc in documents]
    scores: list[float] = model.predict(pairs).tolist()

    scored_docs = [
        {"text": doc, "score": float(score)}
        for doc, score in zip(documents, scores)
    ]
    scored_docs.sort(key=lambda x: x["score"], reverse=True)

    # --- Output ---
    return scored_docs[:top_k]
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 사용자 질의 문자열, 1차 검색 문서 10개 리스트 (`k=10`)
2. **처리(Process)**: CrossEncoder가 `(질의, 문서)` 쌍별 관련도 점수를 계산하고 내림차순 정렬
3. **출력(Output)**: 재순위화된 상위 3개 문서 (`{"text": str, "score": float}` 리스트)

> **참고: BiEncoder vs CrossEncoder**
> 기존 벡터 검색은 **BiEncoder** 방식입니다. 질의와 문서를 각각 독립적으로 임베딩하여 유사도를 계산하므로 속도가 빠릅니다. **CrossEncoder** 는 질의-문서 쌍을 동시에 입력하여 더 정밀한 관련도를 계산하지만, 모든 후보 문서에 대해 계산을 반복해야 하므로 속도가 느립니다. 이 때문에 1차 검색에서 후보를 좁히고(k=10), 2차 ReRanker로 최종 선별(top-3)하는 2단계 파이프라인을 사용합니다.

### 3.2 Hybrid Search 구현

**Hybrid Search(하이브리드 검색)** 는 벡터 유사도 검색과 BM25 키워드 검색의 결과를 가중 합산하여 두 방식의 약점을 보완합니다.

```python
# src/tuning/reranker.py — Hybrid Search 핵심 로직

def hybrid_search(
    query: str,
    collection: chromadb.Collection,
    k: int = 3,
    alpha: float = 0.5,  # 벡터 비중 (1-alpha = BM25 비중)
) -> list[dict[str, Any]]:
    """벡터 유사도 + BM25 키워드 검색을 결합합니다."""

    # --- Input ---
    # alpha=1.0: 순수 벡터 검색 / alpha=0.0: 순수 BM25 검색

    # --- Process ---
    # 1. 벡터 검색 (ChromaDB)
    vector_results = collection.query(query_texts=[query], n_results=fetch_k)
    vector_scores = [1.0 / (1.0 + d) for d in vector_distances]  # 거리 → 유사도 변환
    norm_vector_scores = _normalize_scores(vector_scores)

    # 2. BM25 키워드 검색
    bm25 = BM25Okapi([doc.split() for doc in vector_docs])
    bm25_raw_scores = bm25.get_scores(query.split()).tolist()
    norm_bm25_scores = _normalize_scores(bm25_raw_scores)

    # 3. 가중 합산
    for i, doc in enumerate(vector_docs):
        combined_score = alpha * norm_vector_scores[i] + (1.0 - alpha) * norm_bm25_scores[i]

    # --- Output ---
    return combined[:k]  # 가중 합산 점수 상위 k개
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 검색 질의, ChromaDB 컬렉션 객체, 반환 수 k, 벡터 가중치 alpha
2. **처리(Process)**: 벡터 검색과 BM25 검색 결과를 각각 0~1로 정규화한 뒤 `alpha` 비율로 가중 합산
3. **출력(Output)**: 가중 합산 점수 내림차순 상위 k개 문서 (`{"text": str, "metadata": dict, "score": float}`)

> **팁: alpha 값 조정 기준**
> - `alpha=0.7` (벡터 우선): 의미 중심 질문에 적합. "연차 사용 방법은?" 같은 개념 질문
> - `alpha=0.3` (BM25 우선): 키워드 정확도가 중요한 경우. "HR-2025-012 문서 내용은?" 같은 식별자 기반 질문
> - `alpha=0.5` (균등): 탐색 초기 기본값으로 적합

### 3.3 ReRanker와 Hybrid Search 결합 흐름

```mermaid
flowchart TD
    A["사용자 질의"] --> B["1차 검색 k=10"]
    B -- "벡터 검색" --> C["ChromaDB"]
    B -- "키워드 검색" --> D["BM25"]
    C --> E["Hybrid 가중 합산"]
    D --> E
    E -- "후보 문서 10개" --> F["ReRanker"]
    F -- "재순위 top-3" --> G["LLM 프롬프트 구성"]
```

*그림 10-3: Hybrid Search + ReRanker 2단계 검색 파이프라인*

두 기술을 결합하는 이유는 역할이 다르기 때문입니다. Hybrid Search는 1차 검색 단계에서 다양한 후보 문서를 수집하는 역할을 하고, ReRanker는 수집된 후보 중에서 최종적으로 가장 관련도 높은 문서를 선별하는 역할을 합니다.

### 3.4 Parent Document Retriever 전략

청크 크기를 작게 설정하면 검색 정밀도는 높아지지만 컨텍스트가 부족해집니다. 반대로 크게 설정하면 컨텍스트는 풍부하지만 정밀도가 낮아집니다.

**Parent Document Retriever(부모 문서 리트리버)** 는 이 딜레마를 해결합니다. 작은 청크로 검색하여 정밀도를 확보하되, 검색 결과 반환 시에는 해당 청크가 속한 상위(부모) 문서를 함께 반환하여 충분한 컨텍스트를 제공합니다.

```python
# LangChain Parent Document Retriever 사용 예시 (개념)
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore

# 작은 청크(200자)로 검색 → 부모 문서(1000자) 반환
retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=InMemoryStore(),
    child_splitter=RecursiveCharacterTextSplitter(chunk_size=200),
    parent_splitter=RecursiveCharacterTextSplitter(chunk_size=1000),
)
```

전체 코드는 GitHub 레포의 `src/tuning/` 디렉토리를 참고하십시오.

---

## 4. 프롬프트 튜닝

검색 품질을 충분히 개선했음에도 LLM 응답 품질이 기대에 못 미치는 경우가 있습니다. 이때는 시스템 프롬프트의 지시 방식을 변경하는 프롬프트 튜닝이 효과적입니다.

### 4.1 세 가지 프롬프트 전략

`src/tuning/prompts.py`에는 동일 질문에 대해 세 가지 프롬프트 변형을 각각 실행하고 응답을 비교하는 도구가 구현되어 있습니다.

```python
# src/tuning/prompts.py — 프롬프트 변형 정의

PROMPT_VARIANTS: dict[str, str] = {
    # 전략 1: 기본형 — 문서를 참고하여 답하도록 지시
    "baseline": (
        "당신은 AI 비서입니다. 주어진 문서를 참고하여 답하십시오.\n\n"
        "참고 문서:\n{context}\n\n"
        "질문: {question}\n\n"
        "답변:"
    ),

    # 전략 2: 근거 우선형 — 반드시 문서에서 인용 후 답변
    "evidence_first": (
        "당신은 문서 기반 QA 시스템입니다. 반드시 아래 문서에서 근거를 찾아 인용한 뒤 답하십시오.\n\n"
        "참고 문서:\n{context}\n\n"
        "질문: {question}\n\n"
        "지시사항:\n"
        "1. 먼저 관련 문서 구절을 인용하십시오 (따옴표 사용).\n"
        "2. 인용 근거를 바탕으로 최종 답변을 작성하십시오.\n\n"
        "인용:\n답변:"
    ),

    # 전략 3: 무지 인정형 — 모를 때 추측 금지, 명확히 모른다고 답변
    "admit_ignorance": (
        "당신은 신뢰도 높은 AI 비서입니다. 아래 문서에서 답을 찾을 수 없으면 "
        "'해당 정보를 문서에서 찾을 수 없습니다'라고 명확히 밝히십시오. "
        "절대 추측으로 답하지 마십시오.\n\n"
        "참고 문서:\n{context}\n\n"
        "질문: {question}\n\n"
        "답변:"
    ),
}
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 사용자 질문 문자열, 검색된 컨텍스트 문자열
2. **처리(Process)**: `PROMPT_VARIANTS`의 세 가지 템플릿에 질문과 컨텍스트를 각각 삽입한 뒤 Ollama API 호출
3. **출력(Output)**: 변형명을 키로 하는 응답 딕셔너리 `{"baseline": str, "evidence_first": str, "admit_ignorance": str}`

### 4.2 프롬프트 변형 실험 실행

```python
# 프롬프트 비교 실험 실행 예시
from src.tuning.prompts import compare_prompts

result = compare_prompts(
    question="연차 신청은 며칠 전에 해야 합니까?",
    context="연차 신청은 전월 말일까지 팀장에게 제출해야 합니다. 긴급한 경우 3일 전 구두 보고 후 사후 제출이 가능합니다."
)

for variant, response in result.items():
    print(f"[{variant}]\n{response}\n")
```

### 4.3 전략별 Hallucination Rate 비교

아래는 30개 테스트 케이스로 측정한 전략별 Hallucination Rate 예시입니다.

| 프롬프트 전략 | Hallucination Rate | 특징 |
|------------|------------------|------|
| baseline | ~13% | 지시가 느슨하여 추측성 답변 발생 |
| evidence_first | ~7% | 인용 지시로 문서 근거 강제 |
| admit_ignorance | ~4% | 불확실할 때 모른다고 답하여 오답 최소화 |

**근거 우선형(`evidence_first`)** 은 LLM이 응답을 생성하기 전에 반드시 문서를 인용하도록 강제합니다. 이 지시가 없으면 LLM은 학습 데이터에서 유사한 패턴을 찾아 추측으로 답변할 수 있습니다.

**무지 인정형(`admit_ignorance`)** 은 문서에 답이 없는 질문에서 특히 효과적입니다. 사내 문서에 없는 정보를 질문받았을 때 "일반적으로 ~입니다"라고 답하는 대신 "해당 정보를 문서에서 찾을 수 없습니다"라고 답하도록 유도합니다.

> **주의: 프롬프트 과도한 제약**
> `admit_ignorance` 전략을 지나치게 엄격하게 적용하면 문서에 충분한 근거가 있어도 "찾을 수 없다"고 답하는 경우가 생깁니다. 정량 평가(6절)로 Answer Accuracy와 Hallucination Rate 두 지표를 동시에 확인하십시오.

---

## 5. PDF 이미지 처리: LLaVA + EasyOCR 하이브리드

사내 문서 중에는 스캔(scan)된 PDF가 포함되어 있는 경우가 많습니다. 스캔 PDF는 내부적으로 텍스트 데이터가 없고 이미지만 포함되어 있기 때문에 6장에서 사용한 `pdfplumber`로 텍스트를 추출할 수 없습니다.

이 절에서는 두 가지 도구를 결합하여 스캔 PDF를 처리합니다. **EasyOCR** 은 이미지 내 텍스트를 인식하고, **LLaVA** 는 텍스트 인식을 넘어 이미지 내 도표, 그래프, 표의 내용까지 설명합니다. 두 도구의 역할을 분담함으로써 텍스트와 시각 정보를 모두 추출합니다.

<!-- [IMAGE PLACEHOLDER: 10_ocr-pipeline — 스캔 PDF → 페이지 이미지 변환 → EasyOCR(텍스트) + LLaVA(이미지 설명) → 통합 텍스트 흐름도] -->
*그림 10-4: LLaVA + EasyOCR 하이브리드 OCR 파이프라인*

### 5.1 하이브리드 OCR 구현

```python
# src/ocr_hybrid.py — process_scanned_pdf() 핵심 흐름

def process_scanned_pdf(pdf_path: str) -> list[dict]:
    """스캔 PDF를 페이지별 이미지로 변환 후 OCR + LLaVA 처리합니다."""

    # --- Input ---
    pdf_doc = fitz.open(pdf_path)   # PyMuPDF로 PDF 열기

    for page_idx in range(len(pdf_doc)):
        # --- Process ---
        # 1단계: PDF 페이지 → PNG 이미지 변환 (150 DPI)
        image_path = _pdf_page_to_image(pdf_doc, page_idx, output_dir)

        # 2단계: EasyOCR — 이미지 내 텍스트 인식 (한국어 + 영어)
        ocr_text = extract_with_ocr(image_path)

        # 3단계: LLaVA — 이미지 전체 내용 설명 생성
        llava_desc = describe_image_with_llava(image_path)

        # 4단계: OCR 텍스트 + LLaVA 설명 결합
        combined_text = f"[OCR 추출 텍스트]\n{ocr_text}\n\n[이미지 설명]\n{llava_desc}"

    # --- Output ---
    return results  # [{"page": int, "ocr_text": str, "llava_description": str, "combined_text": str}]
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 스캔 PDF 파일 경로
2. **처리(Process)**: 페이지별로 (1) PyMuPDF로 PNG 이미지 생성 → (2) EasyOCR로 텍스트 추출 → (3) LLaVA로 이미지 설명 생성 → (4) 두 결과 결합
3. **출력(Output)**: 페이지별 결과 딕셔너리 리스트 (`outputs/ocr_pages/` 디렉토리에 이미지 저장)

### 5.2 LLaVA 모델 설치

OCR 실습을 위해 Ollama에 LLaVA 모델을 설치합니다.

```bash
ollama pull llava:7b
```

> **주의: LLaVA 모델 용량**
> `llava:7b` 모델은 약 4.7GB의 디스크 공간이 필요합니다. 메모리가 충분하지 않은 경우 OCR 모드만 건너뛰고 나머지 실습을 진행하여도 학습 목표를 달성할 수 있습니다.

### 5.3 OCR 실습 실행

스캔 PDF 파일을 `data/scanned_sample.pdf` 경로에 배치합니다.

```bash
python src/main.py --mode ocr --pdf data/scanned_sample.pdf
```

출력 예시는 아래와 같습니다.

```
[스캔 PDF 처리] scanned_sample.pdf (5페이지)
============================================================

  [페이지 1/5] 처리 중...
    이미지 변환 완료: page_0001.png
    OCR 완료: 324자 추출
    LLaVA 설명 완료: 512자

  [페이지 2/5] 처리 중...
    이미지 변환 완료: page_0002.png
    OCR 완료: 218자 추출
    LLaVA 설명 완료: 487자

처리 완료: 5/5 페이지 성공
이미지 저장 경로: outputs/ocr_pages/scanned_sample
```

<!-- [CAPTURE NEEDED: 10_ocr-result — python src/main.py --mode ocr --pdf data/scanned_sample.pdf 실행 후 터미널 전체 화면 (페이지별 처리 결과 포함)] -->
*그림 10-5: 스캔 PDF OCR 처리 결과 출력 화면*

### 5.4 역할 분담 설계 원칙

EasyOCR은 이미지 내 텍스트를 문자 단위로 인식하는 데 특화되어 있습니다. 반면 LLaVA는 이미지 전체를 이해하고 자연어로 설명하는 데 강점이 있습니다.

이 분업 구조가 중요한 이유는 다음과 같습니다. 사내 문서에는 텍스트와 도표가 함께 포함된 경우가 많습니다. 표 형태의 데이터를 EasyOCR로만 처리하면 열과 행의 구조가 사라지고 텍스트가 혼합됩니다. LLaVA는 표 전체를 보고 "이 표는 직급별 연차 일수를 나타내며..."처럼 구조적으로 설명합니다. 두 결과를 결합하면 벡터 검색에서 텍스트와 시각 정보 모두를 활용할 수 있습니다.

---

## 6. 평가 체계 구축

튜닝의 효과를 판단하려면 수치가 필요합니다. "이전보다 나아진 것 같다"는 주관적 판단으로는 어느 설정이 얼마나 개선되었는지 알 수 없습니다. 이 절에서는 30개의 테스트 케이스를 기반으로 RAG 시스템의 세 가지 지표를 정량 측정하는 평가 체계를 구축합니다.

### 6.1 세 가지 평가 지표

**Retrieval Accuracy(검색 정확도)**: 질문에 대해 정답이 포함된 문서가 검색 결과에 반환된 비율입니다. 검색 단계의 품질을 측정합니다.

**Keyword Accuracy(키워드 포함률)**: 최종 답변에 정답 키워드가 포함된 비율입니다. LLM 응답 생성 단계의 품질을 측정합니다.

**Hallucination Rate(환각 발생률)**: 전체 응답 중 추측성 표현("아마도", "~일 것입니다" 등)이 포함된 비율입니다. 낮을수록 좋습니다.

### 6.2 테스트셋 설계

`data/testset.json`은 30개의 질문-정답 쌍으로 구성됩니다.

```json
[
  {
    "question": "연차 신청은 며칠 전에 해야 합니까?",
    "expected_answer_keywords": ["전월 말일", "팀장"],
    "expected_source_file": "hr_policy.pdf"
  },
  {
    "question": "성과 평가는 몇 등급으로 나뉩니까?",
    "expected_answer_keywords": ["5등급", "S", "A", "B"],
    "expected_source_file": "hr_policy.pdf"
  }
]
```

총 30개 케이스는 정형 데이터 질의 10개, 비정형 문서 질의 15개, 복합 질의 5개로 구성됩니다. 정형 질의는 PostgreSQL DB 조회가 필요한 질문이고, 비정형 질의는 사내 문서 검색이 필요한 질문입니다.

테스트셋을 직접 작성할 때는 실제 사용자가 묻는 질문 유형을 수집하여 구성하십시오. 개발자가 임의로 만든 질문은 실제 사용 패턴과 달라 평가 결과의 신뢰도가 낮아집니다.

### 6.3 평가 모듈 구현

```python
# src/evaluator.py — run_evaluation() 핵심 흐름

def run_evaluation(
    testset: list[TestCase],
    chain: Any,
    retriever: Any,
) -> dict[str, Any]:
    """전체 테스트셋을 평가하고 집계 결과를 반환합니다."""

    # --- Input ---
    # testset: 30개 TestCase 객체 리스트
    # chain: LangChain RetrievalQA 체인
    # retriever: ChromaDB 기반 리트리버

    for test_case in testset:
        # --- Process ---
        # 1단계: 문서 검색
        docs = retriever.invoke(test_case.question)

        # 2단계: 답변 생성
        result = chain.invoke({"query": test_case.question})

        # 3단계: 평가 판정
        retrieval_correct = _check_retrieval_correct(docs, test_case.expected_source_file)
        answer_contains_keywords = all(kw in answer for kw in test_case.expected_answer_keywords)
        hallucination_detected = _detect_hallucination(generated_answer)

    # --- Output ---
    return {
        "retrieval_accuracy": retrieval_correct_count / total,
        "keyword_accuracy": keyword_correct_count / total,
        "hallucination_rate": hallucination_count / total,
        "details": details,
    }
```

#### 코드 워크플로우 (Code Workflow)

1. **입력(Input)**: 30개 `TestCase` 객체 리스트, LangChain QA 체인, 리트리버
2. **처리(Process)**: 각 케이스에 대해 (1) 문서 검색 → (2) 답변 생성 → (3) 정답 문서 포함 여부, 키워드 포함 여부, 환각 표현 탐지 판정
3. **출력(Output)**: 집계 지표 딕셔너리와 케이스별 상세 결과 — `outputs/eval_results/eval_report_{타임스탬프}.json`

### 6.4 평가 실행 및 결과 해석

```bash
python src/main.py --mode eval
```

출력 예시는 아래와 같습니다.

```
============================================================
RAG 시스템 평가 시작
총 30개 테스트 케이스
============================================================

[01/30] 연차 신청은 며칠 전에 해야 합니까?...
       검색:O  키워드:O  할루시네이션:-

[02/30] 재택근무 신청 절차는 무엇입니까?...
       검색:O  키워드:X  할루시네이션:-

...

============================================================
평가 결과 요약
============================================================
  검색 정확도(Retrieval Accuracy): 86.7%
  키워드 포함률(Keyword Accuracy): 80.0%
  할루시네이션 발생률:              6.7%

평가 보고서 저장 완료: outputs/eval_results/eval_report_20260226_120000.json
```

<!-- [CAPTURE NEEDED: 10_eval-result — python src/main.py --mode eval 실행 후 터미널 전체 화면 (평가 결과 요약 포함)] -->
*그림 10-6: RAG 시스템 평가 결과 출력 화면*

### 6.5 지표별 해석과 개선 방향

| 지표 | 목표값 | 현재 결과 | 해석 |
|------|------|---------|------|
| Retrieval Accuracy | 90% 이상 | 86.7% | 검색 실패 4건 → Hybrid Search 또는 k값 증가 시도 |
| Keyword Accuracy | 80% 이상 | 80.0% | 목표 달성. `evidence_first` 전략으로 추가 개선 가능 |
| Hallucination Rate | 10% 이하 | 6.7% | 목표 달성. `admit_ignorance` 전략 적용으로 더 낮출 수 있음 |

**Retrieval Accuracy가 낮은 경우**: 2절의 청크 튜닝이나 Hybrid Search(3절)를 적용하십시오. 검색 단계에서 정답 문서를 찾지 못하면 이후의 어떤 튜닝도 효과가 없습니다.

**Keyword Accuracy가 낮은 경우**: 검색은 올바르게 됐지만 LLM이 핵심 키워드를 포함하여 답변하지 않는 상황입니다. 4절의 `evidence_first` 프롬프트 전략을 적용하십시오.

**Hallucination Rate가 높은 경우**: 4절의 `admit_ignorance` 프롬프트 전략을 적용하십시오. 테스트셋에 정답이 없는 질문(out-of-domain question)이 포함되어 있는지도 확인하십시오.

> **팁: 튜닝 전후 비교 방법**
> 모든 튜닝 적용 후 동일한 30개 테스트셋으로 재평가하여 지표 변화를 확인하십시오. 보고서는 타임스탬프가 포함된 파일명으로 저장되므로 `outputs/eval_results/` 디렉토리에서 이전 결과와 비교할 수 있습니다.

---

## 7. 정리하며

이 장에서는 완성된 RAG 파이프라인을 체계적으로 개선하는 방법을 학습했습니다. 증상 진단에서 출발하여 청크 / 리트리버 튜닝, 고급 검색 기술, 프롬프트 최적화, OCR 확장, 정량 평가의 순서로 전체 튜닝 흐름을 따라왔습니다.

- **증상별 진단이 튜닝의 출발점입니다**: "성능이 안 좋다"는 막연한 문장 대신 "어떤 질문에서 어떤 방식으로 실패하는가"를 먼저 파악해야 올바른 튜닝 방향을 설정할 수 있습니다. 1절의 증상-원인-해결 매트릭스가 첫 번째 체크포인트입니다.

- **Retrieval은 모든 튜닝의 기반입니다**: 검색 단계에서 정답 문서를 찾지 못하면 이후의 ReRanker, 프롬프트 튜닝도 효과를 낼 수 없습니다. Retrieval Accuracy를 90% 이상으로 높이는 것이 우선 과제입니다.

- **ReRanker와 Hybrid Search는 상호 보완적입니다**: Hybrid Search는 벡터와 BM25의 약점을 서로 보완하여 다양한 질문 유형을 포괄하고, ReRanker는 수집된 후보에서 최종 문서를 정밀 선별합니다. 두 기술을 2단계로 결합할 때 최대 효과를 얻습니다.

- **프롬프트 전략은 Hallucination Rate에 직접 영향을 줍니다**: `evidence_first`(인용 우선)와 `admit_ignorance`(무지 인정) 전략을 적용하면 LLM이 문서 근거 없이 추측하는 것을 억제합니다. 단, 두 전략 모두 Answer Accuracy와 Hallucination Rate를 함께 측정하여 부작용을 확인해야 합니다.

- **정량 평가 체계가 없으면 튜닝의 완성이 없습니다**: 테스트셋 30개로 Retrieval Accuracy, Keyword Accuracy, Hallucination Rate를 측정하는 평가 파이프라인은 튜닝의 결과를 수치로 검증하고, 향후 변경사항이 시스템에 미치는 영향을 사전에 감지하는 안전망 역할을 합니다.

---

### 전체 프로젝트 회고

1장에서 "사내 문서(PDF)와 DB(PostgreSQL)를 LLM과 연결하여 질의응답하는 AI 업무 비서를 로컬에서 구축한다"는 목표를 세웠습니다. 10개 챕터를 거쳐 이 목표가 어떻게 구체화되었는지 되돌아보겠습니다.

```mermaid
flowchart LR
    A["CH01-02 비전+환경"] -- "기반 구축" --> B["CH03-05 데이터 이해"]
    B -- "지식 확보" --> C["CH06-07 RAG 엔진"]
    C -- "시스템 확장" --> D["CH08-09 에이전트 통합"]
    D -- "품질 검증" --> E["CH10 튜닝+평가"]
```

*그림 10-7: 10개 챕터의 학습 여정*

**1~2장**에서는 전체 아키텍처를 이해하고 Ollama, Docker, Python 가상환경을 갖추었습니다. **3~5장**에서는 LLM의 한계를 직접 체험하고, 사내 DB와 문서 표준화 기준을 수립하여 RAG에 입력할 데이터를 준비했습니다. **6~7장**에서는 PDF → 청킹 → ChromaDB 저장 → FastAPI 서비스의 전체 RAG 파이프라인을 구축했습니다. **8~9장**에서는 MCP 프로토콜로 PostgreSQL DB 조회를 연결하고 LangChain으로 모든 구성 요소를 통합했습니다. **10장**에서는 완성된 시스템을 정량 평가하고 개선 방향을 적용했습니다.

이 책에서 구현한 시스템은 완성된 제품이 아닌 기초 골격입니다. 실제 운영 환경에서는 아래 확장 방향을 검토하십시오.

### 향후 확장 방향

**Graph RAG**: 문서 간 관계를 그래프로 표현하여 단순 유사도 검색을 넘어 "A 문서에서 참조하는 B 문서의 내용은?"처럼 관계 기반 검색을 지원합니다. Microsoft의 GraphRAG 또는 LlamaIndex의 Knowledge Graph 모듈이 출발점이 됩니다.

**멀티에이전트 오케스트레이션**: 9장의 단일 에이전트 구조를 확장하여 검색 전문 에이전트, DB 조회 전문 에이전트, 응답 합성 에이전트를 분리하고 오케스트레이터가 조율하는 구조를 구현할 수 있습니다. LangGraph가 이 패턴의 구현을 지원합니다.

**클라우드 배포**: 현재 모든 서비스가 로컬에서 동작합니다. 팀 공유를 위해 Ollama 서버를 GPU 인스턴스에 배포하고, FastAPI는 Docker 컨테이너로 포장하여 Kubernetes나 AWS ECS에 배포할 수 있습니다.

**실시간 문서 동기화**: 현재는 파이프라인을 수동으로 실행해야 새 문서가 ChromaDB에 반영됩니다. 파일 시스템 감시(watchdog)나 문서 관리 시스템의 웹훅(Webhook)을 연결하여 문서 변경 시 자동으로 재인덱싱하는 구조를 추가할 수 있습니다.

**평가 파이프라인 고도화**: 이 장의 평가 체계는 규칙 기반(키워드 포함 여부)으로 동작합니다. RAGAS(RAG Assessment)와 같은 프레임워크를 도입하면 LLM 기반 평가(Faithfulness, Answer Relevancy, Context Precision)로 더 정밀한 측정이 가능합니다.

이 책을 통해 구축한 RAG + MCP 파이프라인이 여러분의 실무에서 좋은 출발점이 되기를 바랍니다.