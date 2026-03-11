# 🤖 사내 문서 기반 AI 업무 비서 프로젝트 계획서

본 문서는 사내의 정형 데이터(SQL)와 비정형 데이터(문서)를 통합하여 지능형 답변을 제공하는 AI 비서 시스템의 구축 로드맵을 담고 있습니다.

## 1. 프로젝트 개요

- **목표**: 사내 데이터를 기반으로 한 하이브리드 RAG 시스템 구축
- **핵심 기술**: FastAPI, PostgreSQL, ChromaDB, Ollama (DeepSeek-R1), LangChain
- **주요 기능**: 데이터 인스턴트(Ingest), 하이브리드 검색(SQL + Vector), 지능형 라우팅

## 2. 개발 로드맵

### 🚀 Phase 1: 기본 인프라 및 프로토타입 (Base System)

- [x] FastAPI 백엔드 기본 구조 설계
- [x] 데이터베이스 스키마 설계 및 초기화 (SQLite → PostgreSQL 마이그레이션 완료)
- [x] 기본 CRUD API 구현 (직원, 휴가, 매출 데이터)

### 🧠 Phase 2: 지식화 및 벡터 검색 (Knowledge Digitalization)

- [x] 문서 업로드 및 관리 인터페이스 (`ingest.html`)
- [x] 비정형 문서 → Markdown 변환 엔진 구축 (pdfplumber, easyocr 활용)
- [x] 벡터 데이터베이스(ChromaDB) 연동 및 임베딩 처리
- [x] 비정형 데이터 검색 서비스 구현 (`vector_service.py`)

### ⚡ Phase 3: 하이브리드 RAG 및 지능형 라우팅 (Hybrid RAG)

- [x] 질문 의도 분석 엔진 (Router Prompt) 및 로직 구현
- [x] SQL과 벡터 검색을 조합한 하이브리드 검색 서비스 (`qa_service.py`)
- [x] Gemini 스타일의 채팅 UI 구현 (`qa.html`)
- [x] LLM 기반 최종 답변 생성 엔진 구축

### ⚙️ Phase 4: RAG 튜닝 및 최적화 (Optimization) - **진행 예정**

- [ ] 검색 성능 최적화 (Top-k 조절, 리랭킹 적용)
- [ ] 프롬프트 고도화 및 답변 정확도 개선
- [ ] 대화 컨텍스트 유지 (Conversation Memory) 기능 추가
- [ ] 에러 처리 및 예외 상황 대응 고도화

## 3. 기술 스택 요약

- **Backend**: Python, FastAPI, SQLAlchemy
- **DB**: PostgreSQL (정형), ChromaDB (벡터)
- **AI/LLM**: Ollama (로컬), LangChain
- **Frontend**: Vanilla JS, Jinja2, CSS (Gemini Aesthetic)

---

_최종 업데이트: 2026-02-09_
