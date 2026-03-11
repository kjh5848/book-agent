# [마스터 플랜] 사내 문서 기반 AI 업무 비서 만들기

## 1. 가상의 대상 독자 (Persona)
- **주 대상**: 사내 데이터(RDB)와 문서(PDF 등)를 연동하여 실무에 적용 가능한 AI 시스템을 직접 구축해보고 싶은 1~3년 차 주니어/미들 개발자.
- **학습 목표**: 단순 API 호출을 넘어, 정형(DB)과 비정형(문서) 데이터를 AI가 능동적으로 판단하고 라우팅(Routing)하는 RAG+MCP 통합 아키텍처를 설계하고 구현할 수 있다.

## 2. 필수 환경 명세
- **OS**: macOS / Linux (Windows는 WSL2 환경 권장)
- **언어 및 런타임**: Python 3.10+
- **주요 라이브러리 및 프레임워크**: FastAPI, LangChain, ChromaDB
- **LLM / 인프라**: Ollama (로컬 구동용: DeepSeek R1, LLaVA 등), PostgreSQL (사내 RDB 모사)

## 3. 분량 및 챕터 구성 계획 (총 100페이지 내외)

| 챕터 | 비중 | 예상 페이지 | 핵심 내용 |
|---|---|---|---|
| **CH01. 비전 및 기초 다지기** | 15% | 15p | 왜 RAG+MCP인가? 기초 RAG 실습 (로컬 구동 및 한계 체감) |
| **CH02. 벡터 DB 및 검색 엔진 셋업** | 30% | 30p | 사내 문서(PDF) 텍스트 및 **표(Table)** 파싱, Chunking, 임베딩 및 LangChain RAG 구축 |
| **CH03. 지능형 브레인 설계 (MCP 통합)** | 40% | 40p | RDB 연동 기초, MCP 기반 정형/비정형 라우팅 에이전트 설계 및 채팅 UI 연동 |
| **CH04. 시스템 튜닝 및 완성** | 15% | 15p | **비전 AI(LLaVA) 차트 해석**, Hybrid Search, ReRanker 등 RAG 고도화 |

## 4. 챕터별 플랜 문서 경로

| 챕터 | 집필 플랜 | 예제 코드 플랜 |
|---|---|---|
| CH01 | `plan/ch01/chapter_plan.md` | `plan/ch01/example_plan.md` |
| CH02 | `plan/ch02/chapter_plan.md` | `plan/ch02/example_plan.md` |
| CH03 | `plan/ch03/chapter_plan.md` | `plan/ch03/example_plan.md` |
| CH04 | `plan/ch04/chapter_plan.md` | `plan/ch04/example_plan.md` |
