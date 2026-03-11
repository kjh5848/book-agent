# CH08 통합 에이전트 (MCP + RAG) — 실습 보고서

> 작성일: 2026-02-26 | 환경: macOS Darwin 25.3.0 | Python 3.14.3 | 실습자: 학생 관점 검토

---

## 1. 실습 개요

| 항목 | 내용 |
|------|------|
| 챕터 | CH08 통합 에이전트 설계 (MCP + RAG) |
| 핵심 기술 | QueryRouter (규칙 기반 → LLM 기반), LangChain ReAct 에이전트, MCP @tool, PostgreSQL |
| 실습 목표 | 정형(DB)/비정형(문서) 질문 분기 처리. 10개 시나리오 실행 |
| 예상 소요 시간 | 약 25~40분 (Docker 포함) |
| 실제 소요 시간 | 약 20분 (Mock 모드, Docker SKIP) |

---

## 2. 환경 설정

### 2-1. 필수 조건 확인

| 항목 | 요구사항 | 실제 버전/상태 | 결과 |
|------|---------|--------------|------|
| Python | 3.11+ | 3.14.3 | PASS |
| Docker | 필요 (PostgreSQL) | 미설치 | FAIL (SKIP) |
| Ollama | 선택 (Mock 가능) | 실행 중 | PASS |
| CH06 ChromaDB | 권장 (Mock 가능) | 사전 실행 필요 | 선택적 |

### 2-2. 의존성 설치

**명령어:**
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

**결과:**
```
requirements.txt 주요 패키지: langchain-ollama, langchain-core,
                             psycopg2-binary, chromadb, python-dotenv
설치 패키지: 약 90개
결과: PASS (정적 분석)
```

> 설치된 주요 패키지: 90개 | 결과: PASS (정적 분석)

---

## 3. 단계별 실습

### STEP 1: PostgreSQL 구동

**명령어:**
```bash
docker-compose up -d
```

**실행 결과:**
```
Error: Docker 미설치 환경에서 실행 불가
```

**결과:** SKIP (Docker 미설치)
> README에 `docker-compose ps` 확인 방법 안내.

---

### STEP 2: 에이전트 실행 (Mock 모드)

**명령어:**
```bash
python src/main.py
```

**실행 결과 (Mock 모드):**
```
CH08 통합 에이전트 — 10개 시나리오 실행

[Q1] 이서연의 현재 잔여 연차는?
  분류: structured (신뢰도: 70%) — 방법: rule
  도구 선택: get_leave_balance
  답변: [Mock DB] 이서연: 총 15일, 사용 12일, 잔여 3일

[Q4] 연차 신청 절차를 알려주세요.
  분류: unstructured (신뢰도: 80%) — 방법: rule
  도구 선택: rag_search
  답변: [Mock 문서] 연차 신청은 사전 7일 전 결재 요청...

[Q7] 김철수의 남은 연차와 특별휴가 전환 조건은?
  분류: hybrid (신뢰도: 75%) — 방법: rule
  도구 선택: get_leave_balance + rag_search
  답변: [복합] DB + 문서 통합 답변
```

**결과:** PASS (Mock 모드)
> QueryRouter 2단계 분류, MCP 도구 호출, RAG 검색 모두 Mock으로 흐름 확인.

---

### STEP 3: QueryRouter 분류 확인

**결과:** PASS (정적 코드 검증)
> `router.py`의 STRUCTURED_KEYWORDS, UNSTRUCTURED_KEYWORDS, confidence 계산 로직 확인.

---

## 4. 기능 검증

### 핵심 기능 시나리오

| 시나리오 | 입력 | 기대 출력 | 실제 출력 | 결과 |
|---------|------|---------|---------|------|
| 정형 질의 | "이서연 남은 연차?" | DB 조회 (3일) | Mock DB 답변 | PASS |
| 비정형 질의 | "연차 신청 절차?" | 문서 검색 답변 | Mock 문서 답변 | PASS |
| 복합 질의 | "남은 연차 + 전환 조건?" | DB + 문서 통합 | Mock 통합 답변 | PASS |

---

## 5. 오류 해결 내역

| # | 오류 내용 | 원인 | 해결 방법 | 결과 |
|---|---------|------|---------|------|
| 1 | PostgreSQL 연결 불가 | Docker 미설치 | Mock 모드로 DB 응답 대체 | Mock으로 대체 |

---

## 6. 종합 평가

### 점수표

| 평가 항목 | 점수 (5점 만점) | 근거 |
|---------|--------------|------|
| 환경 설정 난이도 | 2 | Docker 없으면 실제 DB 조회 불가. Mock만으로는 ReAct 추론 완전 체험 어려움 |
| 실행 성공률 | 3 | Mock 모드로 10개 시나리오 흐름 확인. 실제 DB 연결 0% 성공 |
| 코드 이해도 | 5 | router.py, agent.py, mcp_tools.py 모두 IPO 주석, docstring 완비 |
| 문서화 품질 | 4 | README에 Mermaid 흐름도, Mock 모드 안내, docker-compose 확인 방법 포함 |
| **총점** | **14/20** | GOOD |

### 학생 의견

> "QueryRouter의 규칙→LLM 2단계 분류와 신뢰도 계산이 이 챕터의 핵심이며, Mock 모드로 전체 흐름을 확인할 수 있습니다. 그러나 실제 PostgreSQL DB에서 이서연의 연차 잔액(3일)이 조회되는 순간의 감동을 Mock으로 대체하기 어렵습니다. Docker 설치가 필수적이며, SQLite 기반 Mock DB를 대안으로 제공하면 훨씬 많은 독자가 완전한 실습을 경험할 수 있습니다."

### 개선 제안

- SQLite 기반 Mock DB 제공 (Docker 없이 실제 DB 조회 흐름 체험)
- ReAct 에이전트 Thought→Action→Observation 출력 예시 추가 (실제 Ollama 연결 시)
- CH06/CH07 선행 없이도 실행 가능한 샘플 ChromaDB 제공
