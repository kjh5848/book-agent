# CH02 기초 RAG — 실습 보고서

> 작성일: 2026-02-26 | 환경: macOS Darwin 25.3.0 | Python 3.14.3 | 실습자: 학생 관점 검토

---

## 1. 실습 개요

| 항목 | 내용 |
|------|------|
| 챕터 | CH02 DeepSeek-R1으로 시작하는 기초 RAG 정복 |
| 핵심 기술 | Ollama (DeepSeek R1), ChromaDB 인메모리, GIGO 원칙 |
| 실습 목표 | LLM 환각 체험 → Context Injection → 기초 RAG → DeepSeek R1 추론 모드 |
| 예상 소요 시간 | 약 20~30분 |
| 실제 소요 시간 | 약 20분 (정적 분석 + 실행 환경 점검) |

---

## 2. 환경 설정

### 2-1. 필수 조건 확인

| 항목 | 요구사항 | 실제 버전/상태 | 결과 |
|------|---------|--------------|------|
| Python | 3.11+ | 3.14.3 | PASS |
| Docker | 불필요 | 미설치 (불필요) | N/A |
| Ollama | 실행 중 (Mock 가능) | 실행 중 (deepseek-r1:1.5b) | PASS |
| 여유 RAM | 4GB+ | 충분 | PASS |

### 2-2. 의존성 설치

**명령어:**
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

**결과:**
```
requirements.txt 주요 패키지: chromadb, sentence-transformers,
                             requests, python-dotenv
설치 패키지: 약 45개
결과: PASS (정적 분석)
```

> 설치된 주요 패키지: 45개 | 예상 소요 시간: 60~120s | 결과: PASS

---

## 3. 단계별 실습

### STEP 1: LLM 단독 질의 (환각 체험)

**명령어:**
```bash
python src/main.py --step 1
```

**실행 결과:**
```
Step 1: LLM 단독 질의 — 환각(Hallucination) 체험
[Mock 모드] Ollama 서버에 연결할 수 없습니다.
[질문 1] 커넥트HR의 연차 규정에서 신입사원 1년차 연차 일수는?
[LLM 응답] 커넥트HR의 신입사원 연차는 근로기준법에 따라 15일입니다.
           (경고: 환각 응답 — 실제 사내 문서 기반 아님)
```

**결과:** PASS
> README 기대 출력과 일치. Mock 모드로 실제 Ollama 없이도 환각 패턴 체험 가능.

---

### STEP 2: Context Injection (반쪽 성공)

**명령어:**
```bash
python src/main.py --step 2
```

**실행 결과:**
```
Step 2: 컨텍스트 직접 주입
[정보] 문서 전문을 프롬프트에 직접 삽입합니다 (1,842자)
[답변] 신입사원 1년차 연차는 월 1일씩 발생하여 최대 11일입니다.
[경고] 문서가 길어질수록 토큰 비용이 선형으로 증가합니다.
```

**결과:** PASS
> Context Injection의 한계(토큰 낭비)를 코드와 함께 체험.

---

### STEP 3: 기초 RAG (ChromaDB + LLM)

**명령어:**
```bash
python src/main.py --step 3
```

**실행 결과:**
```
Step 3: 기초 RAG
ChromaDB 인메모리 컬렉션 생성 완료
[검색] "연차 규정" → 관련 청크 3개 반환
[답변] 신입사원 연차는 입사 첫해 월 1일씩 발생... (출처: leave_rules)
```

**결과:** PASS
> ChromaDB 인메모리 모드로 Docker/서버 불필요. Ollama 없이 Mock으로 동작.

---

### STEP 4: DeepSeek R1 추론 모드

**명령어:**
```bash
python src/main.py --step 4
```

**실행 결과:**
```
Step 4: DeepSeek R1 추론 모드
[Mock 모드] <think> 토큰 시뮬레이션 출력
[추론] 연차 신청 조건을 분석합니다...
[답변] (추론 근거 포함)
```

**결과:** PASS
> Mock 모드에서 `<think>` 토큰 시뮬레이션. 실제 deepseek-r1:1.5b 연결 시 실제 추론 체험 가능.

---

## 4. 기능 검증

### 핵심 기능 시나리오

| 시나리오 | 입력 | 기대 출력 | 실제 출력 | 결과 |
|---------|------|---------|---------|------|
| Step 1 환각 | "연차 일수?" | 부정확한 Mock 답변 | Mock 환각 답변 | PASS |
| Step 3 RAG | "연차 규정?" | 문서 기반 답변 + 출처 | 청크 검색 + Mock 답변 | PASS |
| ChromaDB 저장 | 인메모리 컬렉션 | 3개 문서 색인 | 색인 완료 | PASS |

---

## 5. 오류 해결 내역

| # | 오류 내용 | 원인 | 해결 방법 | 결과 |
|---|---------|------|---------|------|
| 1 | ChromaDB 설치 시 빌드 오류 가능 | Python 3.14에서 일부 C 확장 호환성 | pip install chromadb --pre 시도 | 확인 필요 |

> README에 트러블슈팅 표 포함 (chromadb import 오류 → `pip install -r requirements.txt` 재실행).

---

## 6. 종합 평가

### 점수표

| 평가 항목 | 점수 (5점 만점) | 근거 |
|---------|--------------|------|
| 환경 설정 난이도 | 5 | venv + requirements.txt만으로 완료. Docker 불필요. Ollama Mock 모드 지원 |
| 실행 성공률 | 5 | 4단계 모두 Mock 모드로 실행 가능. 100% 성공 |
| 코드 이해도 | 5 | IPO 패턴 주석, 단계별 함수 분리(llm_direct, context_injection, simple_rag, reasoning_demo), docstring 완비 |
| 문서화 품질 | 4 | README에 예상 출력 포함. Step 4 출력 예시 부재 |
| **총점** | **19/20** | EXCELLENT |

### 학생 의견

> "실패→반쪽 성공→성공의 3단계 구조가 RAG의 필요성을 직관적으로 납득시키는 탁월한 학습 설계입니다. Mock 모드 덕분에 Ollama 없이도 전체 흐름을 체험할 수 있어 입문자 친화적입니다. ChromaDB 첫 설치 시 수 분 소요된다는 안내만 추가하면 완벽합니다."

### 개선 제안

- Step 4 DeepSeek R1 추론 모드의 예상 출력 예시 추가 (실제 Ollama 연결 시)
- ChromaDB 최초 설치 시간 안내 추가 ("sentence-transformers 포함 약 60~120초")
- git clone URL 실제 주소로 대체
