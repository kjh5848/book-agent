# RAG기술서 v3 — 초안 (draft)

## 기본 정보

- **제목**: 사내 문서 기반 AI 업무 비서 (RAG + MCP)
- **대상 독자**: 초급~중급 (Python 기본 문법 아는 수준)
- **핵심 기술 스택**: Python 3.10+, FastAPI, PostgreSQL, ChromaDB, LangChain, Ollama + DeepSeek R1, MCP
- **챕터 수**: 10개 + 부록
- **최소 요구사항**: RAM 16GB

## 컨셉

하나의 프로젝트("커넥트HR AI 비서")를 처음부터 끝까지 만들어가는 구조.
독자는 git clone으로 기본 시스템을 받고, 챕터를 따라가며 RAG + MCP 기능을 점진적으로 추가한다.

## 챕터 구성

### PART 0 → CH01: 이 책의 목표와 최종 완성본 미리보기
- **성격**: 이론 (코드 없음)
- **목적**: "무엇을 만들 수 있는지" 먼저 보여주고 동기 부여
- 0.1 이 책이 다루는 범위 (Fine-tuning이 아니라 RAG + MCP)
- 0.2 최종 결과물 데모 시나리오 (정형/비정형/복합 질문 예시)
- 0.3 아키텍처 한 장 요약
- 0.4 사용 기술 스택 (메모리 요구사항 포함)
- 0.5 이 책을 마치면 할 수 있는 것

### PART 0.5 → CH02: 개발 환경 설정
- **성격**: 설정 (환경 검증 코드 있음)
- **목적**: 독자가 막힘 없이 따라할 수 있도록 환경 구축
- 0.5.1 필수 요구사항 (Python 3.10+, RAM 16GB+, 저장공간 20GB+)
- 0.5.2 Ollama + DeepSeek R1 설치 및 테스트
- 0.5.3 Python 가상환경 및 의존성
- 0.5.4 PostgreSQL 설치 (Docker 권장)
- 0.5.5 프로젝트 클론 및 초기 설정
- 0.5.6 주요 의존성 목록
- **예제**: 환경 검증 스크립트 (ollama, python, docker 확인)

### 기초 → CH03: LLM의 한계와 RAG의 필요성
- **성격**: 이론 + 체험 실습
- **목적**: "왜 RAG가 필요한지" 실패→성공 4단계 비교로 직접 체감
- 3.1 [실패] LLM 단독 질의 — DeepSeek R1에 사내 정보 질문, 환각 체험
- 3.2 왜 LLM은 환각을 일으키는가 — 학습 데이터 컷오프, 사내 비공개 정보 부재
- 3.3 [임시 해결] Context Injection 맛보기 — 프롬프트에 문서 직접 붙여넣기, 토큰 한계 체감
- 3.4 [성공] RAG 미리보기 — 인메모리 ChromaDB로 검색+답변, 청킹 유무 비교
- 3.5 [심화] DeepSeek R1 추론 능력 확인 — RAG + 계산/추론 질문
- 3.6 정리: 4단계 비교 요약 + 다음 장 예고
- **예제**: 4개 스크립트 (01_llm_only.py, 02_context_injection.py, 03_rag_preview.py, 04_rag_reasoning.py)
- **data**: 인메모리 전용 (영속화 없음), 샘플 텍스트 파일 내장
- **legacy 참조**: v1 CH03 (동일 구조)

### PART 1 → CH04: FastAPI로 "초간단 사내 시스템" 만들기
- **성격**: 실습 (git clone 기반)
- **목적**: git clone으로 바로 시작할 수 있는 기본 시스템 구축
- 4.1 프로젝트 구성 (폴더 구조, .env, 실행 방법)
- 4.2 데이터 모델 설계 (3테이블: employee, leave_balance, sales)
- 4.3 CRUD API 구현 (직원/휴가/매출)
- 4.4 관리자 Admin UI (Jinja2 템플릿)
- **예제**: FastAPI + PostgreSQL + Jinja2 CRUD 사이트
- **legacy 참조**: 없음 (새로 만들기, 단 ex02/ex03의 DB 스키마 참고)

### PART 2 → CH05: 사내 문서 수집 전략과 문서 표준 만들기
- **성격**: 이론 + 경량 실습
- **목적**: "RAG는 문서 품질과 구조가 반"을 체감
- 5.1 어떤 문서를 넣을 것인가 (교재용 추천 세트)
- 5.2 문서 형식 지원 범위 (MD/PDF/DOCX/XLSX/HWP)
- 5.3 문서 표준 규칙 (파일명 규칙, 메타데이터, 섹션 헤더)
- 5.4 문서 수집 파이프라인 (docs/ 폴더 구조)
- **예제**: 문서 수집/분류 스크립트, 표준화 검증 도구
- **data**: legacy/ex01-1/data/docs/ 의 실무 문서 활용 (PDF, DOCX, XLSX)

### PART 3 → CH06: VectorDB 구축 — 문서를 "검색 가능한 지식"으로 바꾸기
- **성격**: 실습 (핵심)
- **목적**: 문서 → 청크 → 임베딩 → VectorDB 구축의 정석
- 6.1 텍스트 추출 전략 (형식별: PDF/DOCX/XLSX)
- 6.2 Chunk 설계 (fixed-size 500~1000자 + overlap 10~20%)
- 6.3 메타데이터 설계 (doc_id, title, section, version, date, department, source_path)
- 6.4 임베딩 모델 선택 (로컬: sentence-transformers, 한국어: ko-sroberta-multitask)
- 6.5 VectorDB 선택 (Chroma 기준, Pinecone/Weaviate 참고)
- 6.6 인덱싱 실행 & 검증 (테스트 쿼리, 품질 검토)
- **예제**: 문서 파싱 → 청킹 → 임베딩 → ChromaDB 저장 → 검색 테스트
- **legacy 참조**: ex01-1 (스크립트 01~06)
- **data**: 실무 문서 (PDF, DOCX, XLSX) — CH05에서 표준화한 문서 사용

### PART 4 → CH07: RAG로 Q&A 엔진 만들기
- **성격**: 실습 (핵심)
- **목적**: "일단 되는 RAG"를 빨리 만들기
- 7.1 RAG 최소 동작 구현 (질문→Retriever→Prompt→LLM→답변)
- 7.2 RAG 프롬프트 기본 템플릿 (출처 강제, 모르면 "확인되지 않음")
- 7.3 "출처 표시" 응답 포맷 (answer + sources JSON)
- 7.4 ChatGPT 스타일 UI 연결 (FastAPI /api/chat + Jinja2 + JS)
- **예제**: LCEL RAG 체인 + 웹 채팅 UI
- **legacy 참조**: 없음 (v2 CH07을 웹 UI 버전으로 업그레이드)

### PART 5 → CH08: 정형 MCP + 비정형 RAG — 통합 에이전트 설계
- **성격**: 실습 (핵심)
- **목적**: LLM이 "검색/DB조회"를 판단해서 조합하는 구조
- 8.1 정형/비정형 분리 원칙 (MCP+SQL vs VectorDB+RAG vs 복합)
- 8.2 질문 라우팅 전략 (규칙 기반 → 스키마 기반 → LLM 판단)
- 8.3 통합 응답 전략 (질문분석 → 데이터수집 → 통합컨텍스트 → 답변생성)
- 8.4 대표 질문 시나리오 10개 (정형 4, 비정형 4, 복합 2)
- **예제**: QueryRouter + ReAct Agent + MCP Tools + RAG
- **legacy 참조**: ex02 (하이브리드 RAG + MCP + 웹 UI)

### PART 6 → CH09: LangChain으로 연결 전략 세팅
- **성격**: 실습 (심화)
- **목적**: "어떤 체인/구성으로 묶을지" 표준 제시
- 9.1 기본 구성 3종 세트 (Router/Agent + RAG Chain + MCP Tools)
- 9.2 Router 전략 (문서검색 판단 → DB조회 판단 → 실행순서 → 응답)
- 9.3 MCP Tool 설계 (@tool 4개: leave_balance, sales_sum, list_employees, search_documents)
- 9.4 운영 설정 (Timeout/Retry, 로깅, 캐싱, 비용 관리)
- **예제**: LangChain Agent + 4 MCP Tools + 모니터링
- **legacy 참조**: ex03 (Router/Agent + Tools + 운영설정)

### PART 7 → CH10: RAG 튜닝 — "되는 수준"에서 "쓸만한 수준"으로
- **성격**: 실습 (하이라이트)
- **목적**: 실전 문제를 해결하는 순서대로 구성. 책의 하이라이트.
- 10.1 증상으로 시작하는 튜닝 (문제→처방 테이블)
- 10.2 Chunk 튜닝 (fixed→semantic, overlap 조정)
- 10.3 Retriever 튜닝 (k값 실험, threshold, metadata filtering)
- 10.4 ReRanker (Cross-Encoder, Cohere, BGE — top_k=20→ReRanker→top_k=5)
- 10.5 Hybrid Search (BM25 + Vector, Ensemble Retriever)
- 10.6 고급 Retriever (Parent Document, Self-Query, Contextual Compression)
- 10.7 Query Rewrite / Multi-Query (HyDE, 약어/동의어)
- 10.8 프롬프트 튜닝 (근거 우선, "모르면 모른다", 포맷 고정)
- 10.9 PDF 이미지 처리 (LLaVA + EasyOCR 하이브리드)
- 10.10 평가 체계 (테스트 질문 30개+, Retrieval/Answer 정확도, Hallucination Rate)
- 10.11 튜닝 우선순위 가이드 (1~6순위)
- **예제**: 튜닝 실험 프레임워크 (before/after 비교)
- **legacy 참조**: 없음 (신규)

## 부록

- A. 예제 문서 세트 (휴가 규정, 온보딩 가이드, 보안 정책 샘플)
- B. 테스트 질문 30선 (정형 10 + 비정형 10 + 복합 10)
- C. 코드 전체 구조
- D. 참고 자료 (LangChain, Chroma, Ollama 공식 문서)

## 챕터별 예제 유형

| 챕터 | 제목 | 예제 유형 | 코드 | data 필요 |
|------|------|---------|------|---------|
| CH01 | 목표와 미리보기 | 이론 | ❌ | ❌ |
| CH02 | 개발 환경 설정 | 환경 검증 | ✅ (검증 스크립트) | ❌ |
| CH03 | LLM한계와 RAG필요성 | 기초 체험 | ✅ (4개 스크립트) | 인메모리 샘플 |
| CH04 | FastAPI 기본 시스템 | git clone 기반 | ✅ (FastAPI CRUD) | schema.sql + seed |
| CH05 | 문서 수집/표준화 | 이론 + 경량 실습 | ✅ (경량) | legacy 실무 문서 |
| CH06 | VectorDB 구축 | 핵심 실습 | ✅ (핵심) | CH05 문서 계승 |
| CH07 | RAG Q&A + 웹 UI | 핵심 실습 | ✅ (핵심) | CH06 벡터DB 계승 |
| CH08 | 통합 에이전트 | 핵심 실습 | ✅ (핵심) | CH04 DB + CH06 벡터 |
| CH09 | LangChain 연결 | 심화 실습 | ✅ (심화) | CH08 기반 확장 |
| CH10 | RAG 튜닝 | 하이라이트 | ✅ (하이라이트) | CH06 벡터DB + 테스트셋 |

## PART-챕터 매핑 & legacy 참조

| PART | CH (v3) | CH (v2) | CH (v1) | legacy |
|------|---------|---------|---------|--------|
| PART 0 | CH01 | CH01 | CH01 | - |
| PART 0.5 | CH02 | CH03 | CH02 | - |
| 기초 | CH03 | CH02 | CH03 | - |
| PART 1 | CH04 | CH04 | CH04 | - |
| PART 2 | CH05 | CH05 | CH05 | - |
| PART 3 | CH06 | CH06 | CH06 | ex01-1 |
| PART 4 | CH07 | CH07 | CH07 | - |
| PART 5 | CH08 | CH08 | CH08 | ex02 |
| PART 6 | CH09 | CH09 | CH09 | ex03 |
| PART 7 | CH10 | CH10 | CH10 | - (신규 보강) |

## v2 대비 주요 변경점

1. **CH01 코드 제거**: 이론 전용 (데모 없음)
2. **CH03 기초 레그 유지**: LLM한계와 RAG필요성 (v1 CH03 구조 계승, 4단계 체험)
3. **CH04 신규**: FastAPI CRUD 사이트 (git clone 기반)
4. **CH05 신규**: 문서 수집/표준화 (legacy 실무 문서 활용)
5. **CH06 = v2 CH06**: VectorDB 구축 (동일 위치)
6. **CH07 = v2 CH07**: RAG Q&A (웹 UI 추가)
7. **CH08 = v2 CH08**: 통합 에이전트 (10개 시나리오)
8. **CH09 = v2 CH09**: LangChain 연결
9. **CH10 보강**: RAG 튜닝 (v2 CH10의 3/10 → 11/11 풀커버)
10. **data 독립성**: 각 챕터가 이전 챕터 output을 data/로 계승 (명시적)

## 기술 스택

| 영역 | 기술 | 용도 | 메모리 |
|------|------|------|------|
| 텍스트 LLM | Ollama + DeepSeek R1 | 질의응답 (런타임) | 8-16GB |
| Vision LLM | Ollama + LLaVA / Qwen2-VL | 이미지 캡션 (인덱싱) | 4-8GB |
| OCR | EasyOCR | 이미지 텍스트 추출 | 1-2GB |
| Backend | FastAPI + Jinja2 | 웹 서버 + 템플릿 | 1GB |
| 정형 DB | PostgreSQL | 직원/휴가/매출 | 1GB |
| 벡터 DB | ChromaDB | 문서 임베딩 저장 | 1GB |
| 오케스트레이션 | LangChain | RAG + Agent | 1GB |
| 도구 연동 | MCP | LLM ↔ DB 연결 | - |
| 임베딩 | ko-sroberta-multitask | 텍스트 벡터화 | 1GB |
| 문서 파싱 | pypdf, python-docx, openpyxl | PDF/DOCX/XLSX → 텍스트 | - |
