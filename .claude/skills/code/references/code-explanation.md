# Code Explanation Pattern (코드 설명 패턴)

## 1. 구조: 목적 → 번호 주석 → 실행 결과

모든 로직 코드 블록은 아래 3단 구조로 설명한다.

```markdown
**다음 코드는 {무엇을 하는지 한 줄 목적 설명}.**

```python
raw_text = load_file(path)                         # ①
cleaned = clean_text(raw_text)                     # ②
chunks = split_into_chunks(cleaned, chunk_size=500) # ③
collection.add(documents=chunks)                    # ④
```

> ① PDF 파일에서 원본 텍스트를 추출합니다.
> ② 불필요한 공백, 머리글/바닥글을 제거합니다.
> ③ 500자 단위로 청크를 나눕니다 (10% 오버랩).
> ④ ChromaDB 컬렉션에 벡터로 저장합니다.

**실행 결과:**
```
✅ 127 chunks indexed from 3 documents (4.2s)
```
```

## 2. 3단 구조 상세

### A. 코드 위: 목적 한 줄 (필수)

- 코드 블록 바로 위에 **볼드체**로 "이 코드가 하는 일"을 한 문장으로 적는다.
- "다음 코드는 ~합니다." 또는 "~를 구현합니다." 형식.

### B. 코드 내: 번호 주석 (필수)

- 핵심 라인에 `# ①`, `# ②`, `# ③` ... 번호를 매긴다.
- 모든 라인이 아닌 **독자가 이해해야 할 핵심 라인만** 표시한다 (3~6개 권장).
- 코드 블록 바로 아래에 `> ① 설명` 형식으로 각 번호에 대한 설명을 적는다.

### C. 코드 아래: 실행 결과 (권장)

- 코드 실행 시 터미널에 출력되는 결과 또는 생성되는 파일을 보여준다.
- 실행 결과가 없는 코드(클래스 정의, 설정 등)는 생략 가능.

## 3. 전체 예시

```markdown
**다음 코드는 사용자 질문을 받아 ChromaDB에서 관련 문서를 검색하고 LLM으로 답변을 생성합니다.**

```python
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})  # ①
prompt = ChatPromptTemplate.from_template(RAG_TEMPLATE)        # ②
chain = retriever | prompt | llm | StrOutputParser()           # ③
answer = chain.invoke({"question": user_query})                # ④
```

> ① ChromaDB에서 관련도 상위 5개 문서를 검색하는 Retriever를 생성합니다.
> ② 출처 강제, "모르면 모른다" 규칙이 포함된 프롬프트 템플릿입니다.
> ③ LCEL 파이프 연산자로 검색→프롬프트→LLM→파싱을 하나의 체인으로 연결합니다.
> ④ 체인을 실행하여 최종 답변을 생성합니다.

**실행 결과:**
```
Q: 연차 사용 규정이 어떻게 되나요?
A: 취업규칙 제15조에 따르면, 1년 이상 근속 시 15일의 연차가 부여됩니다.
   [출처: HR_취업규칙_v1.0.md, 섹션 3.2]
```
```

## 4. 적용 규칙

- 로직 코드 블록에 **목적 한 줄 + 번호 주석**이 없으면 검증 시 FAIL.
- 번호 주석은 핵심 라인 **3~6개**에만 붙인다 (모든 라인에 붙이지 않는다).
- 실행 결과는 **권장**이며, 실행 불가능한 코드(클래스 정의 등)는 생략 가능.

## 5. 예외 — 설명 불필요

| 코드 유형 | 예시 | 사유 |
|----------|------|------|
| 쉘 명령어 | `pip install`, `python main.py` | 실행 명령어, 로직 없음 |
| 환경 설정 | `export API_KEY=...`, `cp .env.example .env` | 설정 단계 |
| Git 명령어 | `git clone`, `git pull` | 버전 관리 |
| 패키지 관리 | `npm install`, `brew install` | 의존성 설치 |

> **규칙**: 코드 블록의 언어 태그가 `bash`, `sh`, `zsh`, `shell`이면 설명 불필요. `python`, `javascript` 등 로직 코드에만 적용.

## 6. 코드 워크플로우 스타일 (Code Workflow Style)

코드 블록의 번호 주석 설명 아래에 **동작 요약**을 배치한다.
`plan.md`의 `code_workflow_style` 값에 따라 두 가지 스타일 중 하나를 선택한다.

### 스타일 A: `narrative` (서술형) — 기본값

코드의 입력·처리·출력을 하나의 자연어 문단으로 서술한다.

```markdown
> **동작 요약:** 이 코드는 `.env` 파일에서 `LLM_PROVIDER` 값을 읽어
> 해당 Provider의 클라이언트 객체를 생성합니다.
> 호출자는 `BaseLLMClient` 인터페이스만 사용하므로
> 내부 구현을 몰라도 됩니다.
```

### 스타일 B: `flow` (화살표 흐름)

입력→처리→출력을 화살표(`→`)로 연결하여 한 줄로 표현한다.

```markdown
> **흐름:** `.env` → `get_llm_client()` → Ollama/OpenAI/vLLM 분기 → `BaseLLMClient` 인스턴스 반환
```

### 선택 기준

| 스타일 | 적합한 경우 |
|--------|-----------|
| `narrative` | 맥락 설명이 필요한 복잡한 로직, 교육용 도서 |
| `flow` | 파이프라인·데이터 흐름이 명확한 코드, 레퍼런스형 도서 |
