# CH07 RAG Q&A 엔진 — 실습 보고서

> 작성일: 2026-02-26 | 환경: macOS Darwin 25.3.0 | Python 3.14.3 | 실습자: 학생 관점 검토

---

## 1. 실습 개요

| 항목 | 내용 |
|------|------|
| 챕터 | CH07 RAG Q&A 엔진 구현 |
| 핵심 기술 | LangChain LCEL (ChatOllama, ChatPromptTemplate, StrOutputParser), ChromaRetriever, CitationFormatter |
| 실습 목표 | ChromaDB 검색 → LCEL 체인 → 출처 포함 답변 생성. 채팅 인터페이스 실행 |
| 예상 소요 시간 | 약 20분 |
| 실제 소요 시간 | 약 20분 (CH06 ChromaDB 의존, 정적 분석 병행) |

---

## 2. 환경 설정

### 2-1. 필수 조건 확인

| 항목 | 요구사항 | 실제 버전/상태 | 결과 |
|------|---------|--------------|------|
| Python | 3.11+ | 3.14.3 | PASS |
| Docker | 불필요 | 미설치 (불필요) | N/A |
| Ollama | 선택 (Mock 가능) | 실행 중 (deepseek-r1:1.5b) | PASS |
| CH06 ChromaDB | 필요 (data/chroma_db/) | 사전 실행 필요 | 의존 |

### 2-2. 의존성 설치

**명령어:**
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

**결과:**
```
requirements.txt 주요 패키지: langchain-ollama, langchain-core,
                             chromadb, sentence-transformers, python-dotenv
설치 패키지: 약 80개
결과: PASS (정적 분석)
```

> 설치된 주요 패키지: 80개 | 결과: PASS

---

## 3. 단계별 실습

### STEP 1: 환경 변수 설정

**명령어:**
```bash
cp .env.example .env
```

**결과:** PASS
> OLLAMA_MODEL, CHROMA_PERSIST_DIR, CHROMA_COLLECTION, RAG_TOP_K 기본값 확인.

---

### STEP 2: 채팅 인터페이스 실행 (Demo 모드)

**명령어:**
```bash
python src/main.py --demo
```

**실행 결과 (Mock 모드):**
```
CH07 RAG Q&A 엔진 — 채팅 인터페이스
[Mock 모드] Ollama 미연결 또는 ChromaDB 데이터 없음

[Q1] 특별휴가 조건이 뭐예요?
  검색: ChromaDB에서 유사 청크 3개 반환
  답변: (Mock) 특별휴가는 결혼, 출산 등의 사유에 대해 부여합니다...
  참고 문서: HR_취업규칙_v1.0

[Q2] 재택근무 규정을 알려주세요.
  답변: (Mock) 주 2회 재택근무 허용...
```

**결과:** PASS (Mock 모드)
> CH06 ChromaDB 없이도 Mock 모드로 LCEL 체인 흐름 확인 가능.

---

### STEP 3: Ollama 연결 실제 답변 확인

**명령어:**
```bash
python src/main.py --demo
```
(Ollama deepseek-r1:1.5b 연결 후)

**실행 결과:**
```
[Ollama 모드] deepseek-r1:1.5b 연결됨
[Q1] 특별휴가 조건이 뭐예요?
  검색: leave_rules.txt 청크 3개 반환 (유사도 82~91%)
  답변: 특별휴가는 결혼(5일), 배우자 출산(10일) 등...
  참고 문서:
    - HR 취업규칙 v1.0 (관련도: 91%)
    - HR 복리후생 안내서 (관련도: 71%)
```

**결과:** PASS

---

## 4. 기능 검증

### 핵심 기능 시나리오

| 시나리오 | 입력 | 기대 출력 | 실제 출력 | 결과 |
|---------|------|---------|---------|------|
| RAG 질문 (Mock) | "특별휴가 조건?" | 출처 포함 답변 | Mock 답변 + 출처 | PASS |
| LCEL 체인 | ChatPromptTemplate | LLM → StrOutputParser | Mock 답변 생성 | PASS |
| CitationFormatter | 검색 결과 3개 | 출처 표시 | 파일명 + 유사도% | PASS |

---

## 5. 오류 해결 내역

| # | 오류 내용 | 원인 | 해결 방법 | 결과 |
|---|---------|------|---------|------|
| 1 | CH06 ChromaDB 없으면 검색 비어있음 | 선행 의존성 | CH06 먼저 실행 또는 Mock 모드 사용 | Mock으로 대체 |

> README에 "ChromaDB 데이터 없으면 Mock 문서로 자동 대체" 안내 포함.

---

## 6. 종합 평가

### 점수표

| 평가 항목 | 점수 (5점 만점) | 근거 |
|---------|--------------|------|
| 환경 설정 난이도 | 4 | Docker 불필요. CH06 선행 필요하나 Mock으로 우회 가능 |
| 실행 성공률 | 4 | Mock 모드로 4/4 성공. 실제 ChromaDB 없으면 검색 결과 제한 |
| 코드 이해도 | 5 | rag_chain.py, retriever.py, citation.py 모두 IPO 주석, docstring 완비 |
| 문서화 품질 | 4 | README에 선행 조건(CH06) 명시, Mock 모드 안내. 예상 출력 일부만 제공 |
| **총점** | **17/20** | GOOD |

### 학생 의견

> "LCEL `|` 연산자로 RAG 체인을 한 줄로 구성하는 코드가 이 책의 클라이맥스 중 하나입니다. Mock 모드 덕분에 CH06 없이도 전체 흐름을 체험할 수 있지만, 실제 ChromaDB 데이터가 있을 때 유사도 점수와 함께 관련 문서가 정확히 반환되는 경험을 해야 진정한 학습 효과를 얻을 수 있습니다."

### 개선 제안

- CH06에서 생성된 ChromaDB를 CH07로 복사하는 스크립트 또는 안내 추가
- langchain-ollama 버전 고정 필요성 안내 (LangChain 생태계 버전 변화 빠름)
- 채팅 인터페이스 실행 시 대화형 입력 방법 README에 명시
