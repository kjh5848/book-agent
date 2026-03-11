# 도서 기획안 초안 (Draft)

대상 도서의 핵심 키워드 및 목차 초안을 아래 양식에 맞게 작성해주세요.

## 핵심 키워드
- 사내 문서 기반 AI 업무 비서
- RAG (검색 증강 생성) 및 Vector Database (ChromaDB)
- MCP (Model Context Protocol) 
- 로컬 LLM (Ollama, DeepSeek R1, LLaVA)
- 파이썬(Python) 기반 오케스트레이션 (FastAPI, LangChain)

## 대상 독자
- **주 대상**: 사내 데이터(RDB)와 문서(PDF 등)를 연동하여 실용적인 사내 AI 시스템을 직접 구축해보고 싶은 1~3년 차 주니어/미들 개발자.
- **특징**: 단순 코드 복제나 API 호출을 넘어, 정형(DB)과 비정형(문서) 데이터를 AI가 어떻게 이해하고 판단(라우팅)하는지 전 과정을 체계적으로 실습하길 원하는 실무자.

## 1단계 목차 초안
### [Phase 1] 비전 및 기초 다지기
- 1장: 이 책의 목표 (왜 RAG+MCP 인가? 최종 완성본 데모)
- 2장: 기초 RAG 실습 (DeepSeek-R1 로컬 구동 및 한계 체감)

### [Phase 2] 시스템 인프라 및 표준화
- 3장: 개발 환경 설정 (Ollama, PostgreSQL, Python 가상환경 등)
- 4장: 베이스 시스템 (사내 DB 및 기초 사이트 연동)
- 5장: 문서 표준화 (사내 문서 수집 및 전처리 가이드라인)

### [Phase 3] 지식 검색 엔진 (VectorDB & RAG)
- 6장: 벡터 DB 구축 (문서 파싱, Chunking, 배딩 및 ChromaDB 연동)
- 7장: Q&A 엔진 (LangChain 활용 RAG 파이프라인 및 출처 표기)

### [Phase 4] 지능형 에이전트와 완벽한 튜닝
- 8장: 에이전트 설계 (정형 MCP와 비정형 RAG를 인지/라우팅하는 브레인)
- 9장: 최종 연결 (AI 채팅 UI 연동 및 시스템 통합)
- 10장: 시스템 튜닝 (Hybrid Search, ReRanker, 이미지 처리 등 품질 고도화)
