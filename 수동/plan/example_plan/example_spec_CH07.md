# CH07 예제 코드 명세 — RAG Q&A 엔진 구현

## 1. 프로젝트 유형
AI 코드 챕터. 독립 레포 구조. ChromaDB(CH06) 위에 LangChain RAG Chain + 멀티턴 대화 엔진 구축.

## 2. 디렉토리 구조

```
CH07_RAG_QA엔진구현/
├── README.md
├── requirements.txt
├── .env.example
├── src/
│   ├── __init__.py
│   ├── main.py           ← 터미널 대화 루프 진입점
│   ├── rag_chain.py      ← LCEL 기반 RAG Chain 구성
│   ├── retriever.py      ← ChromaDB Retriever 설정
│   ├── citation.py       ← 출처 표시 포맷터
│   └── memory.py         ← 멀티턴 대화 히스토리 관리
├── data/
│   └── chroma_db/        ← CH06에서 생성한 ChromaDB (또는 샘플 제공)
└── outputs/
    └── .gitkeep
```

## 3. 파일별 함수 명세

### `src/retriever.py`

```python
def get_chroma_client(persist_dir: str) -> chromadb.Client:
    """ChromaDB 영속 클라이언트 반환."""

def get_retriever(
    persist_dir: str = "./data/chroma_db",
    collection_name: str = "rag_docs",
    k: int = 3,
    filter_dept: str | None = None
) -> VectorStoreRetriever:
    """
    LangChain VectorStoreRetriever 반환.
    Input : ChromaDB 경로, 컬렉션명, 반환 문서 수 k, 부서 필터
    Process: Chroma(langchain) 래퍼 생성 → as_retriever() 호출
    Output : LangChain VectorStoreRetriever
    """
```

### `src/citation.py`

```python
def format_with_sources(
    answer: str,
    source_documents: list
) -> str:
    """
    답변에 출처 정보를 자동 첨부.
    Input : LLM 생성 답변, Retriever가 반환한 Document 목록
    Process: 각 Document의 metadata에서 source_file, page 추출
    Output : 포맷된 문자열
    예시:
      "연차는 15일입니다.

       [출처]
       - HR규정_v2.1.pdf (3페이지)
       - HR규정_v2.1.pdf (4페이지)"
    """

def extract_source_info(document) -> dict:
    """Document 메타데이터에서 출처 정보 추출. {source_file, page, department}"""
```

### `src/memory.py`

```python
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """
    세션 ID별 ChatMessageHistory 반환 (세션 없으면 새로 생성).
    Input : 세션 식별자 문자열
    Output : InMemoryChatMessageHistory 인스턴스
    Note  : 프로세스 종료 시 히스토리 소멸 (In-Memory 방식)
    """

# 모듈 레벨 세션 저장소
_session_store: dict[str, InMemoryChatMessageHistory] = {}
```

### `src/rag_chain.py`

```python
def build_rag_chain(retriever: VectorStoreRetriever) -> Runnable:
    """
    LCEL 기반 RAG Chain 구성.
    Input : Retriever
    Process:
      1. 프롬프트 템플릿 정의
         system: "당신은 사내 AI 비서입니다. 아래 문서를 참고하여 질문에 답하십시오..."
         human : "{context}\n\n질문: {question}"
      2. LCEL 파이프라인:
         {"context": retriever | format_docs, "question": RunnablePassthrough()}
         | prompt
         | llm (OllamaLLM)
         | StrOutputParser()
    Output : LCEL Runnable (단발 질의용)
    """

def build_multiturn_rag_chain(retriever: VectorStoreRetriever) -> Runnable:
    """
    멀티턴 대화 RAG Chain (RunnableWithMessageHistory 래핑).
    Input : Retriever
    Process:
      1. build_rag_chain() 으로 베이스 체인 생성
      2. RunnableWithMessageHistory 래핑:
         - input_messages_key="question"
         - history_messages_key="chat_history"
         - get_session_history 함수 주입
    Output : RunnableWithMessageHistory
    """

def format_docs(documents: list) -> str:
    """Document 목록을 컨텍스트 문자열로 변환."""
```

### `src/main.py` (chat.py 통합)

```python
def chat_loop(session_id: str = "default") -> None:
    """
    터미널 기반 멀티턴 대화 루프.
    Input : 세션 ID (기본값 "default")
    Process:
      1. Retriever, Chain 초기화
      2. 무한 루프:
         - 사용자 입력 받기 (exit 입력 시 종료)
         - chain.invoke({"question": user_input}, config={"session_id": session_id})
         - format_with_sources()로 출처 포맷
         - 응답 출력
    Output : 콘솔 대화 인터페이스

    종료 명령: "exit", "quit", "종료"
    """

def main() -> None:
    """
    진입점. 환경 변수 로딩 후 chat_loop() 호출.
    실행 전 ChromaDB 존재 여부 확인. 없으면 CH06 먼저 실행 안내.
    """
```

## 4. 실행 시나리오

```bash
cp .env.example .env
pip install -r requirements.txt

# CH06 ChromaDB를 data/chroma_db에 복사하거나 샘플 사용
python src/main.py

# 기대 출력:
# === AI 업무 비서 (RAG Q&A) ===
# ChromaDB 연결 완료 (42개 문서)
# 질문을 입력하세요 ('exit'로 종료):
#
# > 연차 신청은 며칠 전에 해야 하나요?
# 연차 신청은 사용 전월 말일까지 팀장에게 제출하여야 합니다...
#
# [출처]
# - HR규정_v2.1.pdf (3페이지)
#
# > 아까 물어본 연차, 3일 이상이면 어떻게 되나요?  ← 멀티턴 테스트
# 3일 이상 연속 연차 사용 시 팀장의 사전 승인이 필요합니다...
```

## 5. 의존성

```
langchain>=0.3.0
langchain-community>=0.3.0
langchain-ollama>=0.2.0
chromadb>=0.5.0
python-dotenv>=1.0.0
```

## 6. .env.example

```
# LLM Provider 설정 (ollama 또는 openai)
LLM_PROVIDER=ollama

# LLM 모델명 설정
# Ollama 예시: deepseek-r1:1.5b, deepseek-r1:8b, llama3, mistral
# OpenAI 예시: gpt-4o, gpt-4o-mini
LLM_MODEL_NAME=deepseek-r1:1.5b

# Ollama 설정 (PROVIDER가 ollama인 경우 필요)
OLLAMA_BASE_URL=http://localhost:11434

# OpenAI 설정 (PROVIDER가 openai인 경우 필요)
# OPENAI_API_KEY=sk-proj-...

# 임베딩 모델
EMBED_MODEL=nomic-embed-text

# ChromaDB 설정
CHROMA_PERSIST_DIR=./data/chroma_db
COLLECTION_NAME=rag_docs
RETRIEVER_K=3
```

## 7. CH06과의 연결
`data/chroma_db/`는 CH06 `outputs/chroma_db/`의 복사본. README에 다음 안내 포함:
```
# CH06 완료 후 ChromaDB 복사
cp -r ../CH06_벡터DB구축/outputs/chroma_db ./data/chroma_db
```
또는 샘플 ChromaDB를 레포에 포함하여 CH06 없이도 실습 가능.
