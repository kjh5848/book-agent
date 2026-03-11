# CH08 MCP Q&A 에이전트

> RAG 기반 사내 AI 비서 구축 — 8장 실습 코드

## 목적 및 학습 목표

- MCP(Model Context Protocol) 서버를 FastMCP로 구현하는 방법을 이해합니다.
- LangChain ReAct 에이전트가 MCP 도구를 호출하는 자율 실행 흐름을 학습합니다.
- PostgreSQL DB 조회 도구를 MCP로 노출하고 에이전트가 SQL 없이 자연어로 조회하는 패턴을 습득합니다.
- ChromaDB 기반 RAG 검색과 MCP Agent 모드를 하나의 FastAPI 서버에 통합합니다.

## 프로젝트 구조

```
CH08_MCP_QA에이전트/
├── README.md
├── requirements.txt
├── .env.example
├── docker-compose.yml           ← PostgreSQL 컨테이너
├── app/
│   ├── __init__.py
│   ├── main.py                  ← FastAPI 앱 진입점
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py        ← PostgreSQL 연결 (psycopg2 + SQLAlchemy)
│   │   ├── crud.py              ← DB CRUD 함수 (직원/휴가/매출)
│   │   └── init_db.py           ← 샘플 데이터 초기화 스크립트
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── ui.py                ← HTML 페이지 라우터
│   │   └── qa.py                ← REST API 라우터
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py       ← LLM 초기화 및 프롬프트 렌더링
│   │   ├── vector_service.py    ← ChromaDB 벡터 검색
│   │   ├── qa_service.py        ← RAG Q&A 파이프라인
│   │   └── mcp_agent_service.py ← MCP Client + LangChain ReAct Agent
│   ├── prompts/
│   │   ├── router_prompt.j2     ← 인텐트 라우팅 프롬프트
│   │   └── answer_prompt.j2     ← 최종 답변 생성 프롬프트
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── qa.html
│   │   └── agent.html
│   └── static/
│       ├── css/
│       │   └── qa.css
│       └── js/
│           ├── qa.js
│           └── agent.js
├── mcp/
│   └── mcp_server.py            ← FastMCP 서버 (DB 도구 9개)
├── scripts/
│   └── ingest.py                ← PDF → ChromaDB 저장
└── data/
    ├── docs/                    ← PDF 파일 저장 위치
    └── chroma_db/               ← ingest.py 실행 후 자동 생성
```

## 실행 환경

- Python 3.11+
- Docker (PostgreSQL 컨테이너 구동용)
- Ollama + DeepSeek R1 / LLaVA 모델

## 사전 준비

### Ollama 모델 설치

```bash
ollama pull deepseek-r1:1.5b
ollama pull nomic-embed-text
ollama pull llava
```

### PDF 문서 준비

`data/docs/` 폴더에 PDF 문서를 복사하십시오.
파일명 형식: `{부서}_{문서명}_{버전}.pdf` (예: `HR_취업규칙_v1.0.pdf`)

## 설치 및 실행

저장소를 클론합니다.

```bash
git clone https://github.com/{repo}/ch08-mcp-qa-agent
```

ch08-mcp-qa-agent 폴더로 이동합니다.

환경 변수를 설정합니다.

```bash
cp .env.example .env
# .env 파일을 열어 필요한 값을 입력합니다.
```

### macOS

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 실행 방법

### 1단계 — PostgreSQL 컨테이너 실행

```bash
docker-compose up -d
```

### 2단계 — DB 초기화 (최초 1회)

```bash
python -m app.database.init_db
```

### 3단계 — PDF 인제스트 (최초 1회)

```bash
python scripts/ingest.py
```

### 4단계 — FastAPI 서버 실행

```bash
python -m app.main
```

### 5단계 — 브라우저 접속

<!-- [캡처 사진 삽입 위치: 브라우저에서 http://127.0.0.1:8000 접속 후 대시보드 화면 전체] -->

```
http://127.0.0.1:8000
```

## 사용 방법

| 화면 | URL | 설명 |
|------|-----|------|
| 대시보드 | /admin/dashboard | ChromaDB 문서 수, DB 직원 수, 매출 합계 |
| RAG Q&A | /admin/qa | 사내 문서 기반 질문 답변 |
| MCP Agent | /admin/agent | PostgreSQL 자율 조회 에이전트 |

### MCP Agent 질문 예시

```
홍길동의 남은 연차가 며칠이고, 연차 신청 기한이 어떻게 되나요?
영업팀의 이번 달 매출 합계는 얼마인가요?
전체 직원 수와 부서별 인원을 알려주세요.
```

## 환경 변수

| 변수명 | 기본값 | 설명 |
|--------|--------|------|
| LLM_PROVIDER | ollama | LLM 제공자 (ollama 또는 openai) |
| LLM_MODEL_NAME | deepseek-r1:1.5b | LLM 모델명 |
| OLLAMA_BASE_URL | http://localhost:11434 | Ollama 서버 주소 |
| VISION_MODEL | llava | PDF 파싱용 Vision 모델 |
| EMBED_MODEL | nomic-embed-text | 임베딩 모델명 |
| CHROMA_PERSIST_DIR | ./data/chroma_db | ChromaDB 저장 경로 |
| COLLECTION_NAME | rag_docs | ChromaDB 컬렉션 이름 |
| DATABASE_URL | postgresql://company:company1234@localhost:5432/company_db | PostgreSQL 연결 URL |

## 아키텍처

```mermaid
flowchart LR
    U["사용자"] -- "질문" --> F["FastAPI"]
    F -- "RAG 모드" --> V["ChromaDB"]
    F -- "Agent 모드" --> A["ReAct Agent"]
    A -- "MCP 도구 호출" --> M["FastMCP 서버"]
    M -- "SQL 조회" --> P["PostgreSQL"]
    V -- "검색 결과" --> L["LLM"]
    L -- "답변" --> U
```
