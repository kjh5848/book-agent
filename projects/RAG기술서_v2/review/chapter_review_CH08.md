# CH08 통합에이전트 — 독자 리뷰 보고서

> 작성일: 2026-02-26 | 리뷰 방식: 학생 입장 직접 따라하기

---

## 1. 챕터 개요

| 항목 | 내용 |
|------|------|
| 학습 목표 | 정형(DB) + 비정형(문서) 분기 처리, QueryRouter(규칙→LLM 2단계), ReAct 에이전트, MCP @tool 패턴 통합 |
| 전제 조건 | Python 3.11+, Docker (PostgreSQL), Ollama (없으면 Mock 모드), CH06/CH07 ChromaDB |
| 실행 단계 수 | 4단계 (clone → docker-compose up → pip install → python src/main.py) |
| 실제 소요 시간 | Mock 모드 15분 / Docker+Ollama 포함 시 약 30~45분 |

---

## 2. 환경 점검 결과

| 항목 | 상태 | 버전/비고 |
|------|------|---------|
| Python | PASS | 3.14.3 (주의: LangChain 0.3.x와 호환 이슈 존재) |
| Docker | SKIP | 미설치 — PostgreSQL 컨테이너 구동 불가. MCP 도구는 Mock 데이터로 전환됨 |
| Ollama | CONDITIONAL | deepseek-r1:1.5b 설치됨. 그러나 Python 3.14 + LangChain 0.3.x Pydantic V1 호환 오류로 ReAct 에이전트 활성화 불가 |
| termshot | PASS | 0.6.1 |
| ChromaDB | SKIP | CH06 chroma_db 미연결. RAG 도구는 Mock 문서로 전환됨 |

---

## 3. 단계별 실행 결과

### STEP 01: 환경 점검

**실행 명령어:**
```bash
python3 --version
ollama list
termshot --version
```

**화면 캡처:** ![환경 점검](../../assets/screenshots/CH08/step01_env_check.png)

**결과:** PASS (Python 3.14.3, Ollama deepseek-r1:1.5b, termshot 0.6.1 확인)

---

### STEP 02: 패키지 설치 확인

**실행 명령어:**
```bash
python3 -m venv .venv_review
source .venv_review/bin/activate
pip install -r requirements.txt
pip list | grep -E 'langchain|chromadb|psycopg2|requests'
```

**화면 캡처:** ![pip 설치 확인](../../assets/screenshots/CH08/step02_pip_install.png)

**결과:** PASS (langchain 0.3.25, chromadb 1.5.1, psycopg2-binary, requests 정상 설치)

**비고:** Python 3.14.3 환경에서 `langchain 0.3.x`의 Pydantic V1 의존성(`pydantic.v1`)이 Python 3.14와 호환되지 않는 UserWarning이 발생함. 이는 치명적 오류가 아니라 경고 수준이나, `AgentExecutor` import 시 `TypeError: 'function' object is not subscriptable` 오류로 ReAct 에이전트 구성이 실패함.

---

### STEP 03: main.py 실행 (Mock 모드 — 10개 시나리오 전체)

**실행 명령어:**
```bash
cd CH08_통합에이전트
source .venv_review/bin/activate
python src/main.py
```

**화면 캡처:** ![main.py 실행](../../assets/screenshots/CH08/step03_main_run_mock.png)

**실행 결과 요약:**

| 시나리오 | 유형 | 분류 결과 | 신뢰도 | 방법 | 모드 | 결과 |
|---------|------|---------|--------|------|------|------|
| 01 이서연 연차 조회 | 정형 | structured | 80% | rule | mock | PASS |
| 02 개발팀 1월 매출 | 정형 | structured | 70% | rule | mock | PASS |
| 03 연차 신청 절차 | 비정형 | **hybrid** | 65% | rule | mock | 오류 (상세 아래) |
| 04 육아휴직 규정 | 비정형 | unstructured | 90% | rule | mock | PASS |
| 05 김도현 급여 조회 | 정형 | structured | 80% | rule | mock | PASS |
| 06 박민준 연차+신청방법 | 복합 | hybrid | 75% | rule | mock | PASS |
| 07 VPN 보안 규정 | 비정형 | unstructured | 90% | rule | mock | PASS |
| 08 영업팀 4분기 합계 | 정형 | structured | 80% | rule | mock | PASS |
| 09 신입사원 온보딩 | 비정형 | **hybrid** | 75% | rule | mock | 오류 (상세 아래) |
| 10 이서연 부서+매출 | 복합 | structured | 80% | rule | mock | 부분 PASS |

**10/10 시나리오 성공 완료 메시지 확인됨.**

---

### STEP 04: 질문 라우터 단독 테스트

**실행 명령어:**
```bash
python3 -c "
from router import QueryRouter
r = QueryRouter(use_llm_fallback=False)
# 4개 대표 질문 분류 테스트
"
```

**화면 캡처:** ![라우터 테스트](../../assets/screenshots/CH08/step04_router_test.png)

**결과:** PASS — 라우터가 키워드 사전 기반으로 정확히 동작 확인.

**라우팅 오류 발견 (챕터 8.4.4절 재현):**
- 질문: "연차 신청은 어떻게 하나요?"
  - 기대: `unstructured` (문서 검색이 맞음)
  - 실제: `hybrid` (신뢰도 65%)
  - 원인: "연차" 키워드가 `STRUCTURED_KEYWORDS`에 포함됨 + "신청"이 `UNSTRUCTURED_KEYWORDS`에 포함됨 → 양쪽 매칭 → hybrid 오분류

- 질문: "신입사원 온보딩 절차가 어떻게 되나요?"
  - 기대: `unstructured`
  - 실제: `hybrid` (신뢰도 75%)
  - 원인: "절차", "어떻게"가 비정형 키워드에 매칭되고, "사원"이 정형 키워드(`STRUCTURED_KEYWORDS`의 "사원")에도 매칭됨

챕터 8.4.4절에서 이 문제를 예고하고 CH10에서 평가 체계로 개선한다는 안내가 있어 일관성 있는 설명임.

---

### STEP 05: MCP DB 도구 단독 테스트

**실행 명령어:**
```bash
python3 -c "
from mcp_tools import get_employee_info, get_leave_balance, get_department_sales
# 직원 정보, 연차, 매출 조회
"
```

**화면 캡처:** ![MCP 도구 테스트](../../assets/screenshots/CH08/step05_mcp_tools_test.png)

**결과:** PASS — Mock 데이터 기반 DB 조회 정상 동작.

```
[직원 정보] 이서연: 개발팀 개발자, 기본급 3,800,000원
[연차 잔액] 총 15일, 사용 12일, 잔여 3일
[매출 정보] 영업팀 2024/10: 142,000,000원, 달성률 101.4%
```

챕터 8.4.1절 예상 출력 결과와 100% 일치 확인.

---

### STEP 06: RAG 문서 검색 도구 단독 테스트

**실행 명령어:**
```bash
python3 -c "
from rag_tool import search_company_docs
result = search_company_docs.invoke({'query': '연차 신청 방법'})
"
```

**화면 캡처:** ![RAG 도구 테스트](../../assets/screenshots/CH08/step06_rag_tool_test.png)

**결과:** PASS — ChromaDB 미연결 시 Mock 문서 키워드 매칭으로 정상 대체.

챕터 8.4.2절 예상 출력 ("출처: HR_취업규칙_v1.0, 유사도: 0.92")과 일치 확인.

---

### STEP 07: Ollama ReAct 에이전트 실행 시도

**실행 명령어:**
```bash
OLLAMA_MODEL=deepseek-r1:1.5b python3 -c "
from agent import IntegratedAgent
agent = IntegratedAgent()
"
```

**화면 캡처:** ![Ollama 에이전트 시도](../../assets/screenshots/CH08/step07_python314_compat_error.png)

**결과:** FAIL — Python 3.14 + LangChain 0.3.x Pydantic 호환 오류

**오류 메시지:**
```
[경고] 에이전트 구성 실패: LangChain 패키지를 찾을 수 없습니다:
cannot import name 'AgentExecutor' from 'langchain.agents'
```

**원인 분석:**
- Python 3.14에서 `pydantic.v1.fields` import 시 `UserWarning: Core Pydantic V1 functionality isn't compatible with Python 3.14 or greater` 발생
- `langchain.chains.base` 로딩 시 `TypeError: 'function' object is not subscriptable` — Python 3.14의 `typing._eval_type` 변경사항과 Pydantic V1의 `Optional[dict[str, Any]]` 타입 어노테이션 충돌
- **핵심 원인**: LangChain 0.3.x는 Python 3.11~3.12 기준으로 작성되었으며 Python 3.14는 공식 지원 범위 밖

**Mock 모드 자동 전환**: 에이전트 구성 실패 시 `is_mock_mode = True`로 자동 전환되어 나머지 10개 시나리오는 모두 정상 실행됨 — Graceful Fallback 설계 검증됨.

---

### STEP 08: 라우팅 오류 재현 (챕터 8.4.4절 검증)

**화면 캡처:** ![라우팅 오류 재현](../../assets/screenshots/CH08/step08_routing_error_case.png)

**결과:** 챕터에서 예고한 라우팅 오류 정확히 재현됨 (PASS — 원고 설명과 일치)

---

### STEP 09: 정리

```bash
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "python src/main" 2>/dev/null || true
docker-compose down 2>/dev/null || true
```

**결과:** PASS (서버 프로세스 없음, Docker 없음 — 정리 완료)

---

## 4. 챕터 원고 품질 평가

| 항목 | 점수 (5점) | 근거 |
|------|----------|------|
| 설명 충분성 | 5 | 정형/비정형 비교표, 2단계 라우팅 전략, ReAct 에이전트 Thought→Action→Observation 사이클, `@tool` docstring 중요성까지 체계적으로 설명함 |
| Why 설명 | 5 | "RAG만으로 DB 값을 못 가져오는 이유", "DB만으로 정책 문서를 못 찾는 이유", "규칙 기반을 LLM보다 먼저 사용하는 이유(속도)", "temperature=0.1로 설정하는 이유" 등 설계 의도가 명확히 서술됨 |
| 실행 재현성 | 3 | Mock 모드가 잘 설계되어 Docker/Ollama 없이도 10개 시나리오 전체 실행 가능. 단, Python 3.14 환경에서 Ollama ReAct 에이전트 활성화 불가. 원고는 Python 3.11+ 요구사항을 명시했으나 3.14 호환성 경고는 없음 |
| 코드 발췌 정확성 | 5 | `STRUCTURED_KEYWORDS`, `_rule_based_classify()`, `_llm_classify()`, `classify()`, `@tool` 도구 구조 발췌 모두 실제 코드와 100% 일치 확인 |
| 오류 대응 안내 | 4 | Ollama Mock 모드 안내 박스 충실함. 라우팅 오류 사례(8.4.4절) 예고 및 CH10 개선 예고도 적절함. 단, Python 버전 호환성 경고(3.14 이상 주의) 미안내 |
| 분량 적절성 | 4 | QueryRouter → MCP 도구 → ReAct 에이전트 → 10개 시나리오로 자연스럽게 전개됨. 단, 8.3.4절 MCP 도구 코드 발췌가 핵심 내용만 제시하고 `rag_tool.py` 발췌는 생략됨 |
| **총점** | **26/30** | |

---

## 5. 발견된 문제점

### P1 (심각) — Python 3.14 호환성 미고지
- **현상**: Python 3.14 환경에서 `from langchain.agents import AgentExecutor` 실패 (`TypeError: 'function' object is not subscriptable`)
- **원인**: LangChain 0.3.x의 Pydantic V1 의존성이 Python 3.14 `typing` 모듈 변경사항과 충돌
- **영향**: Ollama 연결 시도해도 ReAct 에이전트가 활성화되지 않고 Mock 모드로 강제 전환
- **해결책**: requirements.txt에 `# Python 3.11~3.12 권장, 3.14 미지원` 주석 추가 또는 Python 3.12 기준 테스트 환경 명시

### P2 (보통) — 시나리오 유형 레이블과 실제 분류 불일치
- **현상**: `main.py` 시나리오 03 ("연차 신청은 어떻게 하나요?")이 `비정형`으로 정의되어 있으나 라우터는 `hybrid`로 분류
- **원인**: "연차" 키워드가 `STRUCTURED_KEYWORDS`에, "신청"이 `UNSTRUCTURED_KEYWORDS`에 동시 포함 → hybrid 오분류
- **챕터 원고**: 8.4.4절에서 이 문제를 예고하고 있어 의도적 설계이나, 시나리오 실행 화면 예시(8.4.1절 표)와 실제 실행 결과가 불일치함
  - 원고 표: 시나리오 05 "연차 신청은 어떻게 하나요?" → `unstructured (70%)`
  - 실제 결과: `hybrid (65%)`

### P3 (보통) — 시나리오 10 복합 처리 미완성
- **현상**: 시나리오 10 ("이서연의 부서와 그 부서의 올해 매출은?") 결과가 직원 정보만 출력하고 매출 조회를 수행하지 않음
- **원인**: `_mock_run()`의 `structured` 경로에서 이름 추출 후 매출 조회를 연계하는 로직 미구현. 이서연의 부서(개발팀)로 매출 조회를 자동 연계하려면 추가 로직이 필요함
- **원고**: 시나리오 10을 "복합" 유형으로 정의했으나 실제 Mock 에이전트는 이를 `structured`로 분류하여 DB만 조회하고 부서→매출 연계 조회를 수행하지 않음

### P4 (경미) — rag_tool.py Mock 문서 검색 정확도 낮음
- **현상**: "연차 신청 방법" 질문 시 반환 우선순위가 쿼리 단어 단순 포함 수 기반이어서 관련성 낮은 문서 2, 3번이 함께 반환됨
- **원인**: `_search_chromadb` 폴백 로직이 단어 빈도 기반 정렬로, 의미 기반 랭킹 불가

---

## 6. 학생 한 줄 평

> "QueryRouter의 규칙→LLM 2단계 전략과 신뢰도 계산, ReAct 에이전트의 Thought→Action→Observation 사이클 설명이 이 책 전체에서 가장 실용적인 설계 철학을 담고 있다. Mock 모드가 잘 설계되어 Docker/Ollama 없이도 흐름 전체를 체험할 수 있었지만, Python 3.14 환경에서 Ollama ReAct 에이전트가 실제로 동작하지 않아 책에서 강조한 'Thought→Final Answer' 추론 과정을 직접 확인할 수 없었다는 점이 아쉽다."

---

## 7. 개선 제안

1. **Python 버전 요구사항 명시 강화**: requirements.txt 상단 주석 및 README에 `Python 3.11~3.12 권장 (3.14 미지원)` 명시. 현재 "Python 3.11+ 기준" 표현만으로는 3.14 호환 문제를 예측하기 어려움.

2. **시나리오 표 vs 실제 실행 결과 동기화**: 챕터 8.4.1 표에서 시나리오 05의 분류를 `unstructured (70%)`로 표기했으나 실제는 `hybrid (65%)`. 코드와 원고 간 동기화 필요.

3. **시나리오 10 Mock 에이전트 개선**: "직원 부서 조회 + 해당 부서 매출 조회"를 복합 유형으로 소개하려면, `_mock_run()`이 직원 정보에서 부서를 추출해 매출 조회까지 연계하는 로직 추가 필요.

4. **ReAct 추론 과정 예시 보강**: Ollama 연결 시 Thought→Action→Observation 사이클 실제 출력 예시를 적어도 1개 이상 원고에 포함하면 에이전트 학습 효과가 크게 향상됨.

5. **Docker 없는 대안 명시**: PostgreSQL을 `sqlite:///connecthr.db`로 대체하는 인메모리/SQLite 옵션 또는 관련 안내 추가.
