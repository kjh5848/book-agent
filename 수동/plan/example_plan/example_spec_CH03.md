# CH03 예제 코드 명세 — LLM의 한계와 RAG의 필요성

## 1. 프로젝트 유형
인프라·설명 챕터. 4개의 독립 실행 스크립트. 인메모리 ChromaDB 사용 (영속화 없음).

## 2. 디렉토리 구조

```
CH03_LLM한계와RAG필요성/
├── README.md
├── requirements.txt
├── .env.example
├── src/
│   ├── __init__.py
│   ├── 01_llm_only.py          ← [실패] LLM 단독 → 환각
│   ├── 02_context_injection.py ← [한계] Context Injection + 토큰 경고
│   ├── 03_rag_preview.py       ← [성공] 인메모리 RAG, 단순 질의
│   └── 04_rag_reasoning.py     ← [심화] RAG + DeepSeek R1 추론
└── data/
    └── sample_hr_policy.txt    ← 가상 사내 HR 규정 (1500자 이상, 02에서 사용)
```

## 3. 파일별 함수 명세

### `src/01_llm_only.py`

```python
def ask_llm(question: str) -> str:
    """
    Ollama DeepSeek R1 단독 호출.
    Input : 사내 정보를 묻는 질문
    Process: langchain_ollama ChatOllama.invoke()
    Output : LLM 응답 문자열
    """

def main() -> None:
    """환각을 유발하는 3가지 질문 순서대로 실행. 각 질문 후 주의 메시지 출력."""

QUESTIONS = [
    "우리 회사(테크컴퍼니)의 신입사원 연차 발생 규정이 어떻게 돼?",
    "2024년 4분기 마케팅팀 매출 목표는 얼마야?",
    "사내 보안 USB 정책이 어떻게 돼?",
]
```

### `src/02_context_injection.py`

```python
def load_document(file_path: str) -> str:
    """data/sample_hr_policy.txt 읽기."""

def build_prompt(question: str, context: str) -> str:
    """질문 + 문서 전체를 하나의 프롬프트로 조합."""

def count_tokens(text: str) -> int:
    """대략적인 토큰 수 추정 (len(text) // 4)."""

def ask_with_context(question: str, context: str) -> dict:
    """
    Input : 질문, 컨텍스트 문서
    Output: {"response": str, "token_estimate": int, "over_limit": bool}
             (토큰 추정치 4000 초과 시 over_limit=True + 경고 출력)
    """

def main() -> None:
    """01과 동일한 질문 3개로 Context Injection 비교 실행. 응답 개선 확인 + 토큰 경고."""
```

### `src/03_rag_preview.py`

```python
# 인메모리 ChromaDB + LCEL 기반 RAG
# langchain_classic / RetrievalQA 사용 금지 → LCEL(|) 사용
#
# ── Part A: 청킹 없이 ──────────────────────────────────────
#   긴 HR 규정 문서 전체를 단일 Document로 저장
#   → 질문과 관련 없는 내용까지 함께 검색됨 → 낮은 정밀도
#
# ── Part B: 청킹 있을 때 ──────────────────────────────────
#   동일 문서를 ~200자 청크로 분리하여 저장
#   → 질문에 정확히 관련된 청크만 반환 → 높은 정밀도
#
# 두 결과를 나란히 출력하여 청킹 효과를 직접 비교

LONG_DOC = """
[테크컴퍼니 취업규칙]

제1조 (연차 규정)
신입사원은 입사 후 3년간 법정 연차가 발생하지 않는다.
대신 매월 1회 유급 리프레시 데이를 사용할 수 있다.
3일 이상 연속 사용 시 팀장 사전 승인이 필요하다.

제2조 (보안 USB 정책)
모든 임직원은 회사가 지급한 보안 인증 USB만 사용해야 한다.
개인 USB 및 외부 저장매체 사용은 엄격히 금지된다.
위반 시 보안 규정 위반으로 처리될 수 있다.

제3조 (식대 지원)
점심 식대는 무제한 법인카드로 지원한다.
저녁 식사는 오후 9시 이후 야근 시에만 사용 가능하다.
주말 및 공휴일 식대는 별도 신청 양식을 사용한다.
"""  # 약 500자, 3개 섹션

QUERY = "신입사원 리프레시 데이 규정 알려줘."

def chunk_text(text: str, chunk_size: int = 200, overlap: int = 20) -> list[str]:
    """
    텍스트를 chunk_size 단위로 분할. overlap만큼 이전 청크와 겹침.
    Input : 텍스트, 청크 크기(자), 오버랩(자)
    Output: 청크 문자열 목록
    """

def build_vectorstore_no_chunk(doc: str) -> VectorStore:
    """문서 전체를 단일 Document로 인메모리 Chroma에 저장."""

def build_vectorstore_with_chunk(doc: str) -> VectorStore:
    """chunk_text()로 분할 후 각 청크를 별도 Document로 저장."""

def build_rag_chain(vectorstore: VectorStore, k: int = 2) -> Runnable:
    """
    LCEL RAG Chain.
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt | ChatOllama(...) | StrOutputParser()
    )
    """

def format_docs(docs: list) -> str:
    """Document 목록 → 컨텍스트 문자열 (청크 번호 + 내용)."""

def run_comparison(query: str) -> None:
    """
    Part A / Part B를 순서대로 실행하고 결과 비교 출력.

    출력 형식:
    ══ Part A: 청킹 없이 ══════════════════════
    검색된 문서 수: 1  (전체 문서 1개)
    검색 내용: [전체 규정 전체 텍스트...]
    답변: ...

    ══ Part B: 청킹 있을 때 ═══════════════════
    검색된 문서 수: 2  (관련 청크 2개)
    검색 내용: [제1조 연차 규정 내용만...]
    답변: ...

    ── 비교 결과 ──────────────────────────────
    청킹 없음: 검색 정밀도 낮음 (관련 없는 내용 포함)
    청킹 있음: 관련 청크만 반환 → 더 정확한 답변
    """

def main() -> None:
    """run_comparison(QUERY) 호출."""
```

### `src/04_rag_reasoning.py`

```python
# 03_rag_preview.py와 동일한 구조. 질문만 추론·계산이 필요한 것으로 교체.
# 별도 파일로 분리하여 "단순 검색" vs "추론 포함" 대비를 명확히 함.

def main() -> None:
    """
    동일한 RAG Chain으로 추론 질문 실행.
    질문: "입사 6개월차 신입인데 리프레시 데이 2번 썼어. 몇 번 남았는지 규정 기반으로 계산해줘."
    → [인사규정] 검색 → DeepSeek R1이 6 - 2 = 4번 계산 후 답변.
    검색 근거 문서 + 최종 답변 출력.
    """
```

### `data/sample_hr_policy.txt`
가상 사내 HR 규정 문서:
- 연차 규정 (신입 3년간 연차 없음, 매월 리프레시 데이 1회)
- 보안 USB 정책, 복지 규정
- 매출 목표 내용 없음 (의도적 부재 → 01에서 환각 유도)
- 최소 1500자 이상 (02에서 토큰 한계 체감용)

## 4. 실행 시나리오

```bash
cp .env.example .env
pip install -r requirements.txt
ollama pull nomic-embed-text  # 03, 04에서 임베딩 모델 필요

python src/01_llm_only.py       # ❌ 환각 체험
python src/02_context_injection.py  # △ 개선 + 토큰 경고
python src/03_rag_preview.py    # ✅ RAG 성공
python src/04_rag_reasoning.py  # ✅ RAG + 추론
```

**단계별 기대 출력:**

| 스크립트 | 질문 | 결과 |
|---------|------|------|
| 01 | "신입사원 연차 규정?" | ❌ 근로기준법 일반론 or 회피 |
| 02 | 동일 (문서 포함) | △ 정확하지만 토큰 경고 |
| 03 | 동일 (RAG) | ✅ 정확 + [인사규정] 출처 표시 |
| 04 | "리프레시 데이 몇 번 남았어?" | ✅ 6-2=4 계산 포함 답변 |

## 5. 의존성

```
langchain>=0.3.0
langchain-community>=0.3.0
langchain-ollama>=0.2.0
langchain-chroma>=0.1.0
chromadb>=0.5.0
python-dotenv>=1.0.0
```

> `langchain_classic` **사용 금지** — deprecated.
> `RetrievalQA` 대신 LCEL 파이프라인 사용.

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
```

## 7. CH06과의 차별점 (README에 명시)

| | CH03 (미리보기) | CH06 (실전 구현) |
|--|----------------|----------------|
| 데이터 | 하드코딩 3개 문서 | 실제 PDF 파일 |
| 청킹 | 없음 | fixed-size / semantic |
| ChromaDB | 인메모리 (재실행 시 초기화) | 영속화 (디스크 저장) |
| 목적 | "RAG가 이런 거다" 체험 | 실제 사내 문서 검색 시스템 구축 |

## 8. 레거시 참조
`legacy/02_basic_rag/step3_rag.py`, `step4_rag.py` 기반.
`langchain_classic.chains.RetrievalQA` → LCEL로 완전 교체.
