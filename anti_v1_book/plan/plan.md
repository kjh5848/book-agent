# 사내 문서 기반 AI 업무 비서(RAG + MCP) 집필 기획서 (Blueprint)

## 1. 가상의 대상 독자 (Persona)
- **주 대상**: 사내 데이터(RDB)와 문서(PDF 등)를 연동하여 실무에 바로 투입 가능한 AI 시스템을 직접 구축해보고 싶은 1~3년 차 주니어/미들 백엔드 또는 AI 엔지니어.
- **사전 지식 수준**: Python 기본 문법 숙지, REST API(FastAPI 등)에 대한 기초적 이해. LLM이나 딥러닝 이론에 대해서는 깊게 알지 못해도 괜찮음.
- **학습 후 목표**: 단순 API 호출(프롬프트 엔지니어링)을 넘어, 정형(DB)과 비정형(사내 문서) 데이터를 통합적으로 AI가 인지하고 라우팅하는 '에이전트(Agent)' 기반의 구조적인 RAG 파이프라인을 구축하고 로컬 환경에서 구동할 수 있다.

## 2. 필수 환경 명세 (Environment)
- **OS**: Windows (WSL2 권장), macOS, Linux
- **하드웨어 요구사항**: 시스템 RAM 16GB 이상 (로컬 LLM 구동 시 필수)
- **프로그래밍 언어**: Python 3.10 이상
- **주요 라이브러리 및 도구**:
  - LLM 구동: Ollama (DeepSeek R1, LLaVA)
  - 파이프라인/오케스트레이션: LangChain, LangGraph (필요 시)
  - 웹/API 서버: FastAPI, Jinja2
  - 데이터베이스 (RDB/VectorDB): PostgreSQL, ChromaDB
  - 기타 도구: EasyOCR, PyMuPDF (문서 파싱용)
- **실습 진행 방식 (Learning Style)**:
  - **Clone & Modify 방식**: 이 책은 방대한 RAG 인프라를 바닥부터 모두 타이핑하기에는 지면이 부족합니다. 따라서 독자에게 제공되는 **공식 깃허브 저장소(GitHub Repository)를 Clone** 받은 뒤, 책의 지시에 따라 특정 폴더 경로 내의 뼈대 코드를 열고 **핵심 로직만 복사/붙여넣기 및 수정**하며 빠른 성취감을 얻는 방식을 취합니다.
- **인프라 구성 방식 (Docker)**:
  - **도커(Docker) 기반 인프라**: 베이스 시스템인 PostgreSQL 데이터베이스나 외부 연동 시뮬레이션 환경은 **Docker Compose**를 통해 명령어 한 줄로 띄워서 사용합니다. (Chapter 3 환경 세팅 및 Chapter 4 DB 연동 파트에서 적용)
  - 파이썬 실행 환경은 `venv` 가상환경을 기준으로 합니다.

## 3. 학습 목표 (Learning Objectives)
1. **로컬 무과금 AI 인프라 구축**: Ollama를 이용해 비용 0원으로 온프레미스(로컬) AI 환경을 구축하는 방법을 익힙니다. (보안과 비용 문제 동시 해결)
2. **멀티 데이터 소스 통합**: 기존 사내의 정형 테이블(PostgreSQL 등)과 비정형 사내 규정 문서(PDF, Hwp 등)를 하나로 묶어 AI에게 이해시킵니다.
3. **지능형 에이전트 라우팅 경험**: 단순 RAG가 아닌, 사용자 질문의 의도에 따라 정형 데이터(MCP)를 탐색할지, 비정형 문서(VectorDB)를 탐색할지 AI가 스스로 판단하게 만드는 구조화된 에이전트를 설계합니다.

## 4. 목차 초안 및 분량 산정 (총 100페이지 내외 목표)

이 책은 안티그래비티 100페이지 IT 도서 분량 규칙(4 파트 체제)을 따릅니다. 굵고 짧게 끝내는 실습서 형태로, 이론은 최소화하고 독자가 직접 코드를 치며 원리를 깨닫도록 유도합니다.

### 📍 PART 1. 비전 및 기초 다지기 (개념 도입, 약 15쪽 / 15%)
- **Chapter 1. 이 책의 목표 탈탈 털기**
  - 왜 RAG와 MCP를 결합해야 하는가?
  - 완성될 최종 결과물 미리보기 (시나리오 및 데모)
- **Chapter 2. 기초 RAG로 몸 풀기**
  - Ollama와 DeepSeek R1 로컬 설치 및 한계점(할루시네이션) 직접 겪어보기
  - 이를 해결하기 위한 RAG 파이프라인 맛보기

### 📍 PART 2. 베이스 시스템 인프라 구축 (기본 실습, 약 30쪽 / 30%)
- **Chapter 3. 개발/로컬 환경 세팅**
  - Python 가상환경, PostgreSQL DB 세팅
- **Chapter 4. 베이스 사내 시스템 연동**
  - 사내 직원 관리, 휴가, 매출 등이 담긴 임시 DB(RDB) 확보 및 FastAPI 연동 실습 (CRUD)
- **Chapter 5. 사내 문서 표준화 및 준비**
  - 파편화된 사내 문서(사내 규정, 프로세스 등) 수집하기

### 📍 PART 3. 지식 검색 엔진 설계: VectorDB & RAG (심화 실습, 약 40쪽 / 40%)
- **Chapter 6. 사내 문서 전처리와 Vector DB 적재 (`ex01` 기반)**
  - 어려운 문서를 AI가 읽기 좋게 전처리하기 (PDF/Excel 파싱 및 Chunking)
  - 임베딩(Embedding) 거쳐 로컬 ChromaDB에 영구 저장하기 (`create_vector_db.py`)
- **Chapter 7. 심화 RAG Q&A 엔진 만들기 (`ex02` 기반)**
  - Vector DB에서 유사도 검색 수행하기 (`retrieval_test.py`)
  - LangChain LCEL 기반 완벽한 RAG 파이프라인 조립 (`rag_pipeline.py`)

### 📍 PART 4. 지능형 에이전트로 최종 진화 (배포 및 마무리, 약 15쪽 / 15%)
- **Chapter 8. 에이전트 라우팅 설계: MCP + RAG (`ex03` 기반)**
  - 사용자의 질문을 분석해 DB(MCP 도구)로 갈지, 사내 문서(VectorDB)로 갈지 스스로 판단하는 라우팅 에이전트 구현 (`agent_router.py`)
- **Chapter 9. AI 채팅 UI 통합 시스템 구축**
  - FastAPI 템플릿과 챗 엔진 연결
- **Chapter 10. 끝판왕 튜닝 가이드**
  - 이미지 처리(LLaVA/OCR), Hybrid Search 도입 등 퀄리티를 폭발시키는 핵심 꿀팁
