# 초안: AI 업무 비서 구축 — RAG + MCP 실전 가이드

## 기본 정보

- **책 제목**: AI 업무 비서 구축 — RAG + MCP 실전 가이드
- **부제**: 사내 문서와 DB를 LLM과 연결하는 지식 엔진 설계 전 과정
- **대상 독자**: Python 기초는 알지만 LLM/RAG는 처음인 초급 개발자
- **예상 분량**: 100페이지 이하
- **이론 vs 실습 비율**: 이론 30% / 실습 70%

## 핵심 기술 스택

| 역할 | 기술 | 버전 |
|------|------|------|
| LLM 추론 | Ollama + DeepSeek R1 | 최신 |
| 이미지 LLM | LLaVA | 최신 |
| OCR | EasyOCR | 최신 |
| 파이프라인 | LangChain | 0.3+ |
| 벡터 DB | ChromaDB | 최신 |
| 관계형 DB | PostgreSQL | 16 |
| API 서버 | FastAPI | 0.110+ |
| Python | Python | 3.11 |

## 집필 목표

독자가 단순히 코드를 따라 하는 수준을 넘어, 사내에 흩어진 데이터(DB)와 문서(PDF)를 AI가 이해하는 지식으로 변환하고, 정형·비정형 데이터를 통합적으로 질의응답하는 AI 업무 비서를 실전 배포하는 전 과정을 체계적으로 습득합니다.

## 전체 로드맵

책의 전개는 [비전 제시] → [기초 다지기] → [시스템 구축] → [에이전트 고도화] 4단계로 구성됩니다.

| 단계 | 범위 | 핵심 활동 |
|------|------|---------|
| Stage 1. 비전 및 기초 | 1~2장 | 목표 확인 + 기초 RAG 실습 |
| Stage 2. 인프라 및 표준화 | 3~5장 | 환경 구축 + 사내 시스템 확보 + 문서 표준화 |
| Stage 3. 지식 검색 엔진 | 6~7장 | 벡터 DB + RAG Q&A 파이프라인 |
| Stage 4. 지능형 에이전트 | 8~10장 | MCP+RAG 통합 에이전트 + 튜닝 |

## 챕터별 구성

### 1장. 이 책의 목표와 최종 완성본 미리보기 (프롤로그)

- 1.1 이 책이 다루는 범위 (Fine-tuning이 아닌 RAG 파이프라인)
- 1.2 최종 결과물 데모 시나리오 (정형+비정형 복합 질의응답)
- 1.3 전체 아키텍처 한 장 요약
- 1.4 사용 기술 스택 상세
- 1.5 이 책을 마치면 할 수 있는 것

### 2장. DeepSeek-R1으로 시작하는 기초 RAG 정복

- 2.1 [실패] LLM 단독 질의의 한계 (환각 체감)
- 2.2 [반쪽 성공] 프롬프트 직접 주입 (Context Injection)
- 2.3 [성공] VectorDB와 RAG의 시작 (ChromaDB + 검색)
- 2.4 [심화] DeepSeek-R1 추론(Reasoning) 활용

### 3장. 개발 환경 구축

- 3.1 Ollama 설치 및 DeepSeek R1 모델 다운로드
- 3.2 PostgreSQL 설치 및 초기 설정
- 3.3 Python 3.11 가상환경 및 패키지 설치
- 3.4 환경 변수(.env) 구성 및 LLM Provider 스위칭 설계

### 4장. 베이스 시스템 확보

- 4.1 사내 시스템(직원·휴가·매출 DB) git clone으로 확보
- 4.2 데이터베이스 스키마 분석
- 4.3 CRUD API 구조 이해
- 4.4 MCP(Model Context Protocol) 개념 소개

### 5장. 사내 문서 표준화

- 5.1 RAG 검색 품질을 결정하는 문서 기준
- 5.2 PDF, Word, Markdown 수집 전략
- 5.3 문서 전처리 및 정규화 가이드라인
- 5.4 문서 버전 관리 및 메타데이터 설계

### 6장. 벡터 DB 구축

- 6.1 텍스트 추출 (PyMuPDF, pdfplumber)
- 6.2 청킹(Chunking) 전략 — Fixed-size vs Semantic
- 6.3 임베딩 모델 선택 및 적용
- 6.4 ChromaDB에 저장 및 컬렉션 관리

### 7장. RAG Q&A 엔진 구현

- 7.1 LangChain RAG 파이프라인 설계
- 7.2 유사도 검색 및 컨텍스트 구성
- 7.3 출처 표시(Source Citation) 시스템
- 7.4 기본 채팅 인터페이스 연결

### 8장. 통합 에이전트 설계 (MCP + RAG)

- 8.1 정형/비정형 분리 원칙
- 8.2 질문 라우팅 전략 (규칙 기반 → LLM 판단)
- 8.3 통합 응답 전략 (DB 조회 + 문서 검색 + LLM 합성)
- 8.4 대표 질문 시나리오 10개 실습

### 9장. LangChain 최종 연결

- 9.1 Router / Agent / RAG Chain / MCP Tool 구성
- 9.2 MCP Tool 설계 (get_leave_balance, get_sales_sum 등)
- 9.3 운영 설정 (Timeout, Retry, 로깅, 캐싱)
- 9.4 비용 관리 및 토큰 모니터링

### 10장. RAG 시스템 튜닝

- 10.1 증상별 튜닝 가이드 (환각, 근거 부족, 엉뚱한 문서)
- 10.2 Chunk/Retriever 튜닝 (Semantic Chunk, k값, Metadata Filtering)
- 10.3 고급 기술 (ReRanker, Hybrid Search, Parent Document Retriever)
- 10.4 프롬프트 튜닝 (근거 우선, 모르면 모른다)
- 10.5 PDF 이미지 처리 (LLaVA + EasyOCR 하이브리드)
- 10.6 평가 체계 구축 (테스트셋 30개, Retrieval 정확도, Hallucination Rate)

## 문체 가이드

- **문체**: 하십시오체 (합니다, 입니다)
- **어조**: 신뢰 기반 실천적 + 친절한 사수 시점
- **용어**: 한국어 우선, 영문 병기 (예: 검색 증강 생성(RAG))
- **표현 금지**: 추측성 표현 ("~인 것 같습니다"), 이모지(본문)

## 실습 방식 (핵심 설계 원칙)

### AI 코드 실습 — GitHub Clone 후 실행

모든 챕터의 예제 코드는 GitHub 저장소에 완성본으로 준비합니다.
독자는 코드를 타이핑하거나 복사·붙여넣기하지 않고, `git clone` 후 즉시 실행합니다.

```
git clone https://github.com/{repo}/CH06_vector-db
cd CH06_vector-db
cp .env.example .env   # API 키 등 환경 변수만 직접 입력
pip install -r requirements.txt
python src/main.py
```

- **독자 역할**: 코드를 읽고 이해하는 것에 집중. 환경 변수 설정 오류만 직접 해결.
- **저자 역할**: 챕터별 완성 코드를 GitHub에 유지. 코드 주석으로 흐름 설명.
- **책의 역할**: 코드가 왜 이렇게 설계되었는지 Why를 설명하는 해설서.

### 인프라 구성 — Docker Compose (GitHub Clone)

PostgreSQL, FastAPI CRUD 서버, 샘플 데이터 등 인프라는 별도 인프라 레포를 제공합니다.
독자는 `docker-compose up -d` 한 번으로 전체 백엔드 환경을 자동 구성합니다.

```
git clone https://github.com/{repo}/rag-infra
cd rag-infra
docker-compose up -d
# 자동 실행: PostgreSQL + 샘플 데이터 + FastAPI CRUD 서버
```

- Docker 설치만 전제 조건으로 요구 (PostgreSQL 직접 설치 불필요)
- 샘플 데이터(직원·휴가·매출 DB)는 Docker 이미지에 포함

### GitHub 저장소 구조 (예상)

| 레포 | 내용 |
|------|------|
| `rag-infra` | docker-compose.yml, PostgreSQL 초기화 SQL, FastAPI CRUD 서버 |
| `CH02_basic-rag` | 2장 기초 RAG 실습 코드 |
| `CH06_vector-db` | 6장 벡터 DB 구축 코드 |
| `CH07_qa-engine` | 7장 Q&A 엔진 코드 |
| `CH08_agent` | 8장 통합 에이전트 코드 |
| `CH09_langchain` | 9장 최종 연결 코드 |
| `CH10_tuning` | 10장 튜닝 코드 |

> 1~5장은 인프라 clone + 구조 분석 중심이므로 별도 AI 코드 레포 없음.

## 명시적 제외 범위

- **프로덕션 배포**: Docker, Kubernetes, 클라우드 배포 등 운영 환경 배포 내용은 이 책의 범위에서 제외합니다. 로컬 환경 구축 및 실습 완성까지를 목표로 합니다.

## LLM 구성

이 책은 **로컬 LLM 전용**입니다. 클라우드 API(OpenAI 등)를 사용하지 않습니다.

| 항목 | 값 |
|------|---|
| 추론 엔진 | Ollama |
| 기본 모델 | DeepSeek R1 |
| 환경 변수 | `OLLAMA_MODEL=deepseek-r1`, `OLLAMA_BASE_URL=http://localhost:11434` |
