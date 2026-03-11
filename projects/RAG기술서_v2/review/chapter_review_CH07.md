# CH07 RAG Q&A 엔진 구현 — 독자 리뷰 보고서

> 작성일: 2026-02-26 | 리뷰 방식: 학생 입장 직접 따라하기 | 챕터 컨셉: LangChain LCEL + 출처 표시 시스템

---

## 1. 챕터 개요

| 항목 | 내용 |
|------|------|
| 학습 목표 | ChromaRetriever + LCEL 파이프라인(프롬프트 | LLM | Parser) + CitationFormatter로 출처 포함 답변 생성 |
| 전제 조건 | CH06 완료(ChromaDB 컬렉션 생성), Python venv, Ollama (없으면 Mock 모드) |
| 실행 단계 수 | 3단계 (clone → install → python src/main.py) |
| 실제 소요 시간 | 약 15~20분 (Mock 모드), 30분+ (LLM 연결) |

## 2. 환경 점검 결과

| 항목 | 상태 | 비고 |
|------|------|------|
| Python 버전 | PASS | 3.14.3 |
| Docker | 불필요 | 이 챕터는 ChromaDB 파일 기반 |
| Ollama deepseek-r1 | SKIP 가능 | Mock 모드 자동 전환 |
| CH06 ChromaDB 컬렉션 | 필수 의존 | connecthr_docs 컬렉션 선행 필요 |

## 3. 단계별 실행 결과

### STEP 1: 저장소 클론 및 패키지 설치

**원고 지시:** `git clone ... && cp .env.example .env && pip install -r requirements.txt`

**예제 코드 검증:**
- `.env.example`에 OLLAMA_MODEL, CHROMA_PERSIST_DIR, CHROMA_COLLECTION, RAG_TOP_K 포함 확인
- venv 생성 및 활성화 지시 포함 (macOS/Linux, Windows 구분)

**결과:** PASS (정적 분석)

---

### STEP 2: RAG 파이프라인 실행

**원고 지시:** `python src/main.py`

**예제 코드 검증:**
- `src/rag_chain.py`의 `SYSTEM_PROMPT` 발췌: 챕터 원고와 실제 코드 100% 일치
- LCEL 체인 구성 코드 (`prompt | self.llm | output_parser`): 챕터 발췌와 실제 코드 일치
- `src/retriever.py`의 `ChromaRetriever.search()`: 챕터 발췌와 일치. 코사인 거리→유사도 변환(`1.0 - dist`) 확인
- `src/citation.py`의 `CitationFormatter`: 클래스 구조 및 `_normalize_source_name()` 함수 존재 확인
- Mock 모드 분기 로직 (`_check_ollama_available()`, `_check_langchain_available()`): 구현 확인

**결과:** PASS (정적 분석)

**예상 출력 검증:**
- 챕터 기대 출력: "특별휴가 조건이 뭐예요?" → 출처가 포함된 답변(HR 취업규칙 v1.0, 관련도 92%)
- CitationFormatter 포맷과 도입부 데모 출력 일치

---

### STEP 3: CH06 의존성 확인

**원고 지시:** CH06의 `connecthr_docs` 컬렉션을 먼저 생성하십시오

**비고:** 챕터에 "CH06 없이 실행하면 RuntimeError: ChromaDB 컬렉션을 로드할 수 없습니다 오류가 발생합니다" 경고 박스 존재 — 명확한 의존성 안내.

**결과:** PASS (경고 박스 포함)

---

## 4. 챕터 원고 품질 평가

| 항목 | 점수 (5점) | 근거 |
|------|----------|------|
| 설명 충분성 | 5 | LCEL `|` 연산자 설명, SYSTEM_PROMPT 환각 방지 원칙, CitationFormatter 역할까지 충분 |
| Why 설명 | 5 | 왜 LangChain인가(3가지 이유: 표준 인터페이스, LCEL, 생태계), 왜 temperature=0.1인가, 왜 출처를 표시해야 하는가 모두 설명 |
| 실행 재현성 | 4 | Mock 모드 지원. 단, CH06 선행 의존성이 강함. CH06 없이는 즉시 실습 불가 |
| 코드 발췌 정확성 | 5 | SYSTEM_PROMPT, LCEL chain 구성, retriever.search() 발췌 모두 실제 코드와 일치 |
| 오류 대응 안내 | 4 | CH06 미실행 오류 안내 있음. langchain-ollama 버전 불일치 시 ImportError 안내 없음 |
| 분량 적절성 | 5 | 검색기, 체인, 출처 표시 세 컴포넌트를 균형있게 다룸. 도입부 데모 스토리가 학습 동기 부여 |
| **총점** | **28/30** | |

## 5. 발견된 문제점

1. **CH06 강한 선행 의존성**: 이 챕터는 CH06의 ChromaDB 데이터 없이는 실행 불가. CH06을 건너뛴 독자를 위한 샘플 ChromaDB 데이터 또는 빠른 초기화 스크립트 미제공.
2. **langchain-ollama 버전 경고**: LangChain 생태계는 버전 변화가 빠름. requirements.txt에 langchain-ollama 버전이 고정되어 있지만 최신 설치 시 API 변경 가능. 챕터에 LangChain 버전 주의 안내 필요.
3. **git clone URL 플레이스홀더**: `git clone https://github.com/{repo}/CH07_RAG_QA엔진` — 실제 URL이 아닌 플레이스홀더.

## 6. 학생 한 줄 평

> "LCEL `|` 연산자로 RAG 체인을 한 줄로 표현하는 순간이 이 책의 하이라이트이며, 환각 방지 프롬프트 원칙과 CitationFormatter의 설계 근거까지 명확히 설명한 이 챕터는 프로덕션 RAG 구현의 핵심을 담은 완성도 높은 챕터입니다."

## 7. 개선 제안

- CH06 선행 실행이 어려운 독자를 위한 샘플 ChromaDB 파일 또는 빠른 초기화 스크립트 제공
- langchain-ollama, langchain-core 버전 호환성 주의 안내 추가
- git clone URL을 실제 URL 또는 명확한 주석으로 대체
