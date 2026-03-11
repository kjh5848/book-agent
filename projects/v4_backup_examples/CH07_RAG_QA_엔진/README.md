# CH07 RAG Q&A 엔진

> 사내 문서 기반 AI 업무 비서 (RAG + MCP) - Chapter 07 실습 코드

## 학습 목표

- LCEL(LangChain Expression Language) 파이프 연산자로 RAG 체인을 조립하는 방법을 이해한다
- "출처 강제 + 모르면 확인되지 않음" 프롬프트 설계 패턴을 적용한다
- FastAPI + Jinja2 기반 채팅 웹 UI(Fetch POST 방식)를 구현한다
- ConversationBufferWindowMemory로 멀티턴 대화를 관리한다

## 실행 환경

- Python 3.10+
- Ollama (로컬 LLM, 기본값) 또는 OpenAI API (선택)
- ChromaDB (CH06 생성 데이터 또는 자동 인메모리 폴백)

## 독립 실행 안내

CH06의 ChromaDB가 없어도 실행할 수 있습니다. `data/chroma_db/` 폴더가 비어 있으면 인메모리 샘플 데이터(휴가 규정, 재택근무, 보안 정책 등 6개 문서)가 자동으로 로드됩니다.

CH06 데이터를 사용하려면 `CH06_VectorDB_구축/outputs/chroma_db/` 폴더를 이 프로젝트의 `data/chroma_db/`에 복사하십시오.

## 설치 및 실행

이 챕터의 예제 코드를 클론합니다.

```bash
git clone https://github.com/{repo}/ch07-rag-qa-engine
cd ch07-rag-qa-engine
```

환경 변수를 설정합니다.

```bash
cp .env.example .env
# .env 파일을 열어 LLM_PROVIDER와 관련 키를 입력합니다.
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Windows (WSL2)

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 실행

```bash
python -m app.main
```

브라우저에서 `http://localhost:8000/chat` 을 열면 채팅 UI가 실행됩니다.

## 예상 출력

<!-- [CAPTURE NEEDED: 브라우저에서 채팅 UI가 표시된 전체 화면] -->

서버 시작 시 터미널 출력:

```
[INFO] 서버 시작: http://0.0.0.0:8000
[INFO] 채팅 UI: http://localhost:8000/chat
[INFO] ChromaDB 로드: ./data/chroma_db
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

ChromaDB가 없을 때 인메모리 폴백:

```
[WARN] ChromaDB 사용 불가 (ChromaDB 경로가 없습니다.). 인메모리 샘플 데이터를 사용합니다.
[INFO] 인메모리 샘플 데이터 6건 로드 완료.
```

채팅 질문 예시 (브라우저에서):

```
질문: 연차는 몇 일 받을 수 있나요?
AI:  1년간 80% 이상 출근한 직원에게는 15일의 연차 유급휴가를 부여합니다.
     [출처: HR_취업규칙_v1.0]
```

> 위 출력은 실제 실행 결과를 그대로 옮긴 것입니다. 터미널 출력과 한 글자씩 대조하여 디버깅에 활용하십시오.

## 전체 구조

```mermaid
flowchart LR
    A["사용자 질문"] -- "Fetch POST" --> B["FastAPI /api/chat"]
    B -- "검색" --> C["ChromaDB Retriever"]
    C -- "컨텍스트" --> D["RAG Chain(LCEL)"]
    D -- "JSON 응답" --> E["채팅 UI"]
    E -- "대화 히스토리" --> B
```

## 파일 구조

```
CH07_RAG_QA_엔진/
├── README.md
├── requirements.txt
├── .env.example
├── src/
│   ├── __init__.py
│   ├── rag_chain.py          # LCEL 기반 RAG 체인
│   ├── response_parser.py    # 답변 + 출처 파서
│   └── conversation.py       # 멀티턴 대화 히스토리 관리
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI 앱 + 페이지 라우터
│   ├── chat_api.py           # /api/chat 엔드포인트
│   └── session.py            # 세션 ID 관리
├── templates/
│   ├── base.html             # 좌측 사이드바 레이아웃 (ex02 동일)
│   └── chat.html             # 채팅 UI (ex02 qa.html 기반)
├── static/
│   ├── css/
│   │   ├── style.css         # 전역 스타일 (ex02 admin.css 기반)
│   │   └── chat.css          # 채팅 전용 스타일 (ex02 qa.css 기반)
│   └── js/
│       └── chat.js           # Fetch 기반 채팅 로직 (ex02 qa.js 패턴)
├── data/
│   └── chroma_db/            # CH06 ChromaDB (없으면 인메모리 샘플 사용)
└── outputs/
    └── .gitkeep
```
