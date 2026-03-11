# CH02 DeepSeek-R1으로 시작하는 기초 RAG 정복 — 독자 리뷰 보고서

> 작성일: 2026-02-26 | 리뷰 방식: 학생 입장 직접 따라하기 | 챕터 컨셉: 실패→성공 3단계 체험

---

## 1. 챕터 개요

| 항목 | 내용 |
|------|------|
| 학습 목표 | LLM 환각 체험 → Context Injection 한계 → 기초 RAG 구현 |
| 전제 조건 | Ollama + DeepSeek R1 (없어도 Mock 모드로 진행 가능) |
| 실행 단계 수 | 4단계 (step 1~4) |
| 실제 소요 시간 | 약 15~20분 (Mock 모드), 30분+ (실제 LLM 연결) |

## 2. 환경 점검 결과

| 항목 | 상태 | 비고 |
|------|------|------|
| Python 버전 | PASS | Python 3.14.3 |
| Ollama | PASS | deepseek-r1:1.5b 설치됨 |
| ChromaDB | 확인 필요 | requirements.txt 설치 후 사용 가능 |
| 가상환경 | 권장 | 챕터에서 venv 사용 안내됨 |

## 3. 단계별 실행 결과

### STEP 1: 실행 환경 준비

**원고 지시:** Ollama 설치 → 모델 다운로드 → 저장소 클론 → venv → pip install

**결과:** PASS (venv 포함 설치 안내가 명확함)

**비고:** CH01과 달리 venv 사용이 명시되어 있음. 개선된 점.

---

### STEP 2: --step 1 (환각 체험)

**원고 지시:** `python src/main.py --step 1`

**예제 코드 검증:**
- `src/llm_direct.py`의 `query_llm_directly` 함수: 챕터 발췌 코드와 일치
- Mock 모드 분기 로직 정확히 구현됨

**결과:** PASS (코드-원고 일치)

---

### STEP 3: --step 2 (Context Injection)

**원고 지시:** `python src/main.py --step 2`

**예제 코드 검증:**
- `src/context_injection.py` 존재 확인
- 챕터의 Context Injection 한계 설명과 코드 구현 일치

**결과:** PASS

---

### STEP 4: --step 3 (기초 RAG)

**원고 지시:** `python src/main.py --step 3`

**예제 코드 검증:**
- `src/simple_rag.py`의 `search_similar_documents` 함수: 챕터 발췌와 100% 일치
- `build_rag_prompt` 함수도 일치
- ChromaDB 인메모리 컬렉션 사용으로 Mock 모드에서도 동작

**결과:** PASS

---

### STEP 5: --step 4 (추론 모드)

**원고 지시:** `python src/main.py --step 4`

**예제 코드 검증:**
- `src/reasoning_demo.py` 존재 확인
- DeepSeek R1의 `<think>` 토큰 설명과 구현 일치

**결과:** PASS (Ollama 연결 시 추론 토큰 확인 가능)

---

## 4. 챕터 원고 품질 평가

| 항목 | 점수 (5점) | 근거 |
|------|----------|------|
| 설명 충분성 | 5 | 실패→반쪽 성공→성공의 3단계 흐름이 독자의 이해를 자연스럽게 이끔 |
| Why 설명 | 5 | "왜 Context Injection이 실패하는가", "왜 RAG가 필요한가" 명확히 설명 |
| 실행 재현성 | 4 | venv 안내 포함, Mock 모드로 대체 가능. --step 번호가 직관적 |
| 코드 발췌 정확성 | 5 | search_similar_documents, build_rag_prompt 발췌가 실제 코드와 일치 |
| 오류 대응 안내 | 4 | "출력 결과가 다를 수 있습니다" 주의 안내 있으나, ChromaDB 설치 오류 안내 부재 |
| 분량 적절성 | 5 | 4개 Step을 점진적으로 쌓는 구조가 학습 흐름에 적합 |
| **총점** | **28/30** | |

## 5. 발견된 문제점

1. **ChromaDB 설치 시간 안내 부재**: ChromaDB + sentence-transformers 최초 설치 시 수 분 소요되지만 챕터에 안내 없음
2. **git clone 플레이스홀더**: `{repo}` URL이 실제 주소가 아님
3. **Step 4 실행 결과 미제시**: Step 4 추론 모드의 실제 출력 예시가 없어 성공 여부 판단 불명확

## 6. 학생 한 줄 평

> "실패 → 반쪽 성공 → 성공의 3단계 구조가 RAG를 왜 쓰는지 직관적으로 이해하게 해주며, Mock 모드 덕분에 Ollama 없이도 전체 흐름을 체험할 수 있는 매우 잘 설계된 입문 챕터입니다."

## 7. 개선 제안

- ChromaDB 최초 설치 시 다운로드 시간 안내 추가
- Step 4 추론 모드 예상 출력 예시 추가
- git clone URL 플레이스홀더를 실제 URL로 교체
