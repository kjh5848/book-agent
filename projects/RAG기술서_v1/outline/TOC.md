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
