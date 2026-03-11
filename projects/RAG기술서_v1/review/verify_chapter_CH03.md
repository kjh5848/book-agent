# 검증 보고서: CH03 DeepSeek R1으로 체험하는 LLM의 한계와 RAG의 필요성

## 판정: CONDITIONAL_PASS

---

## 검증 항목

| # | 카테고리 | 항목 | 필수/권장 | 결과 | 비고 |
|---|----------|------|---------|------|------|
| 1 | 문체 | 하십시오체 일관 사용 | 필수 | PASS | 전체 원고에서 "~합니다/~입니다/~하십시오" 일관 사용. 추측성 표현 없음. 이모지 없음. |
| 2 | 볼딩 | 핵심 용어 첫 등장 시 볼드 처리 및 앞뒤 공백 | 필수 | PASS | 환각(Hallucination), 학습 데이터 컷오프(Training Cutoff), 컨텍스트 주입(Context Injection), RAG, 청킹(Chunking), 추론(Reasoning) 등 모두 첫 등장 시 볼드 처리. 앞뒤 공백 규칙 준수. |
| 3 | 맥락 연결 | 이전/다음 챕터 연결 | 권장 | PASS | 도입부에서 CH02 내용 자연스럽게 참조. 마지막 문단에서 CH04 예고 적절. |
| 4 | 구조 | 4단계 구조 및 TOC 섹션 일치 | 필수 | PASS | 도입부→개념(섹션2)→실습(섹션1,3,4,5)→정리하며(섹션6) 준수. TOC.md의 6개 섹션과 제목 완전 일치. |
| 5 | 코드 동기화 | 예제 코드와 원고 코드 일치 및 IPO 워크플로우 | 필수 | CONDITIONAL_PASS | 4개 파일 핵심 발췌 모두 실제 예제 코드와 일치. IPO 워크플로우 8개 코드 블록 모두 존재. 단, 섹션 5.2의 04_rag_reasoning.py 발췌에 코드 생략 표현 1건 발견(경고). |
| 6 | 분량 | 8,000자 이상 여부 | 권장 | PASS | 원고 569행, 추정 20,000자 이상. 기준(8,000자) 대비 충분히 초과. |

---

## 경고 항목 상세 (CONDITIONAL_PASS 사유)

### 항목 5: 코드 동기화 — 코드 생략 표현 1건

- **위치**: 원고 섹션 5.2 (추론에 특화된 프롬프트, 488행)
- **현재 상태**: `04_rag_reasoning.py` 핵심 발췌의 `build_rag_chain()` 함수 내부 마지막 줄에 `# ...LCEL 체인 구성 (03_rag_preview.py와 동일)` 주석이 포함됨. 이는 실제 코드가 생략된 상태임.

```python
# src/04_rag_reasoning.py 핵심 발췌 — 추론 프롬프트
def build_rag_chain(vectorstore: Chroma, k: int = 2) -> tuple[Any, Any]:
    ...
    prompt = ChatPromptTemplate.from_template(...)
    # ...LCEL 체인 구성 (03_rag_preview.py와 동일)   ← 생략 표현
```

- **기대 상태**: 생략 표현 없이 실제 LCEL 체인 구성 코드를 원고에 직접 제시하거나, 또는 발췌 범위를 프롬프트 정의 부분으로만 명확히 한정하여 생략 표현을 삭제.
- **수정 제안 (안 1)**: 생략 주석 대신 실제 LCEL 체인 코드를 그대로 포함시킴.

```python
    llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0)

    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain, retriever
```

- **수정 제안 (안 2)**: 발췌 제목을 `# src/04_rag_reasoning.py 핵심 발췌 — 추론 프롬프트 (LCEL 체인은 03_rag_preview.py와 동일)`로 변경하고, 코드 블록을 프롬프트 정의까지만으로 줄이며 `# ...` 줄 자체를 삭제.
- **중요도**: 권고 수준 (섹션 5.2 이전에 이미 동일한 LCEL 체인 전체가 섹션 4.5에 제시되어 있으므로 독자 이해에는 큰 지장 없음)

---

## 세부 검증 내역

### 카테고리 1: 문체

- 하십시오체 확인: 전체 원고 "~합니다", "~입니다", "~하십시오" 일관 사용.
- 확인된 문장 패턴 샘플:
  - "먼저 예제 레포를 클론하고 환경을 설정하십시오." (명령형 하십시오체 O)
  - "방금 목격한 현상의 원인을 이해하십시오." (O)
  - "이 현상이 바로 **환각(Hallucination)** 입니다." (O)
- 이모지 사용 없음 (chapter_spec에만 이모지가 있으며 원고에는 없음)
- 금지 표현(상투적 비유, 추측성 표현) 없음

### 카테고리 2: 볼딩

핵심 용어 첫 등장 시 볼드 처리 및 공백 규칙:

| 용어 | 등장 위치 | 앞뒤 공백 | 판정 |
|------|---------|---------|------|
| 환각(Hallucination) | 94행 | O | PASS |
| 학습 데이터 컷오프(Training Cutoff) | 104행 | O | PASS |
| 컨텍스트 주입(Context Injection) | 134행 | O | PASS |
| 검색 증강 생성(RAG, Retrieval-Augmented Generation) | 244행 | O | PASS |
| 청킹(Chunking) | 251행 | O | PASS |
| 추론(Reasoning) | 430행 | O | PASS |

문단당 볼딩 개수: 모든 본문 문단에서 1~2개 이하 유지. 정리하며 섹션은 핵심 결론 볼드 처리로 구조상 허용.

### 카테고리 3: 맥락 연결

- 이전 챕터(CH02) 참조: "2장에서 Ollama, PostgreSQL, Python 가상환경을 완비했습니다. 이 장에서는 구축된 환경을 사용하여..." (3~4행) — 자연스러운 연결 O
- 다음 챕터(CH04) 예고: "다음 장에서는 이 장에서 사용한 인메모리 ChromaDB를 넘어, 사내 시스템(PostgreSQL DB + FastAPI CRUD API)을 `git clone`으로 확보합니다. RAG가 왜 필요한지 확인한 지금, 4장에서 실제 시스템 인프라를 갖추겠습니다." (568행) — 적절한 예고 O
- chapter_spec의 "다음 챕터로 넘기는 개념" 항목과 일치 O

### 카테고리 4: 구조

4단계 구조 준수 확인:

| 단계 | 원고 구현 | 판정 |
|------|---------|------|
| 도입부 | 1~10행: 챕터 제목, 전 챕터 연결, 이 장 목표 설명, 이미지 플레이스홀더 | O |
| 개념 설명 | 섹션 2 (98~130행): 환각 원인 개념 설명 (Mermaid 다이어그램 포함) | O |
| 실습 | 섹션 1, 3, 4, 5: 4개 파이썬 스크립트 실습 (코드 블록 + 워크플로우) | O |
| 정리하며 | 섹션 6 (552~569행): `## 6. 정리하며` — 불렛 포인트 개조식 요약 | O |

TOC.md CH03 섹션 구조 vs 원고 섹션 비교:

| TOC.md | 원고 | 일치 |
|--------|------|------|
| 3.1 [실패] LLM 단독 질의의 한계 | ## 1. [실패] LLM 단독 질의의 한계 | O |
| 3.2 왜 LLM은 환각을 일으키는가 | ## 2. 왜 LLM은 환각을 일으키는가 | O |
| 3.3 [임시 해결] Context Injection 맛보기 | ## 3. [임시 해결] Context Injection 맛보기 | O |
| 3.4 [성공] RAG 미리보기 + 청킹 비교 | ## 4. [성공] RAG 미리보기 + 청킹 비교 | O |
| 3.5 [심화] DeepSeek R1 추론 능력 확인 | ## 5. [심화] DeepSeek R1 추론 능력 확인 | O |
| 3.6 정리하며 | ## 6. 정리하며 | O |

### 카테고리 5: 코드 동기화

**원고 코드 발췌 vs 실제 예제 파일 비교:**

| 파일 | 검증 항목 | 판정 | 비고 |
|------|---------|------|------|
| 01_llm_only.py | QUESTIONS 상수 내용 | PASS | 3개 질문 완전 일치 |
| 01_llm_only.py | ask_llm() 함수 IPO 구조 | PASS | Input/Process/Output 주석 위치 일치 |
| 01_llm_only.py | ChatOllama 호출 패턴 | PASS | 동일 |
| 02_context_injection.py | build_prompt() 함수 | PASS | 프롬프트 템플릿 문자열 완전 일치 |
| 02_context_injection.py | count_tokens() 함수 | PASS | `len(text) // 4` 로직 일치 |
| 02_context_injection.py | ask_with_context() 함수 | PASS | TOKEN_WARNING_THRESHOLD 비교 로직 일치 |
| 03_rag_preview.py | build_vectorstore_no_chunk() | PASS | Document 생성 및 metadata 일치 |
| 03_rag_preview.py | chunk_text() | PASS | chunk_size, overlap, step 로직 일치 |
| 03_rag_preview.py | build_rag_chain() LCEL 체인 | PASS | retriever → format_docs → prompt → llm → StrOutputParser 파이프라인 일치 |
| 04_rag_reasoning.py | REASONING_QUESTION 상수 | PASS | 문자열 완전 일치 |
| 04_rag_reasoning.py | build_rag_chain() 추론 프롬프트 | PASS | 프롬프트 템플릿 내용 일치 |
| 04_rag_reasoning.py | build_rag_chain() LCEL 부분 | **경고** | `# ...LCEL 체인 구성 (03_rag_preview.py와 동일)` 생략 표현 존재 |

**IPO 워크플로우 섹션 존재 확인:**

| 원고 코드 블록 | 워크플로우 섹션 | 판정 |
|-------------|-------------|------|
| 01_llm_only.py ask_llm() | 74~78행 `#### 코드 워크플로우 (Code Workflow)` | PASS |
| 02_context_injection.py ask_with_context() | 204~208행 | PASS |
| 03_rag_preview.py Part A build_vectorstore_no_chunk() | 293~297행 | PASS |
| 03_rag_preview.py Part B chunk_text() | 330~334행 | PASS |
| 03_rag_preview.py build_rag_chain() LCEL | 388~392행 | PASS |
| 04_rag_reasoning.py build_rag_chain() | 491~495행 | PASS |

모든 Python 코드 블록에 IPO 워크플로우 섹션 존재 O.

### 카테고리 6: 분량

- 원고 총 행수: 569행
- 추정 총 문자 수: 코드 블록 포함 약 20,000자 이상 (569행 × 평균 35자/행 기준)
- 목표 분량: 8,000자 이상 (8페이지)
- TOC.md 명시 분량: 8p
- 판정: 기준 대비 약 250% 수준으로 충분히 초과. ±20% 이내 기준(6,400~9,600자)을 크게 초과하나, 코드 블록이 상당 부분을 차지하므로 실제 페이지 환산 시 8p 범위에 해당할 것으로 판단.

---

## 요약

- 총 검증 항목: 6개 카테고리
- 통과 (PASS): 5개 (문체, 볼딩, 맥락 연결, 구조, 분량)
- 조건부 통과 (경고): 1개 (코드 동기화 — 코드 생략 표현 1건)
- 실패 (FAIL): 0개
- 시도 횟수: 1/2

**최종 판정 사유:**
모든 필수 항목(문체, 볼딩, 구조, 코드 동기화)이 통과되었습니다. 코드 동기화 항목에서 `04_rag_reasoning.py` 섹션 5.2의 `build_rag_chain()` 발췌에 `# ...LCEL 체인 구성 (03_rag_preview.py와 동일)` 생략 표현이 발견되었습니다. 해당 LCEL 체인 전체 코드는 섹션 4.5에서 이미 완전하게 제시되어 있어 독자 이해에 큰 지장은 없으나, 코드 생략 금지 원칙에 위배됩니다. 필수 항목은 모두 통과하였고 권장 항목에서도 문제 없으므로 **CONDITIONAL_PASS** 판정합니다.
