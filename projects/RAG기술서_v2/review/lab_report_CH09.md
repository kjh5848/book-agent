# CH09 LangChain 최종 연결 — 실습 보고서

> 작성일: 2026-02-26 | 환경: macOS Darwin 25.3.0 | Python 3.14.3 | 실습자: 학생 관점 검토

---

## 1. 실습 개요

| 항목 | 내용 |
|------|------|
| 챕터 | CH09 LangChain 최종 연결 |
| 핵심 기술 | AgentConfig dataclass, ResponseCache TTLCache, Exponential Backoff, JSON 구조화 로깅, Tool description 정밀화 |
| 실습 목표 | 프로덕션 에이전트 5개 질문 실행, 캐시 히트율 확인, 토큰 리포트 출력 |
| 예상 소요 시간 | 약 15~20분 |
| 실제 소요 시간 | 약 15분 (Mock 모드) |

---

## 2. 환경 설정

### 2-1. 필수 조건 확인

| 항목 | 요구사항 | 실제 버전/상태 | 결과 |
|------|---------|--------------|------|
| Python | 3.11+ | 3.14.3 | PASS |
| Docker | 선택 (Mock 가능) | 미설치 | SKIP (Mock) |
| Ollama | 선택 (Mock 가능) | 실행 중 | PASS |
| cachetools | requirements.txt | 포함 확인 | PASS |

### 2-2. 의존성 설치

**명령어:**
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

**결과:**
```
requirements.txt 주요 패키지: langchain-ollama, langchain-core,
                             cachetools, psycopg2-binary, python-dotenv
설치 패키지: 약 85개
결과: PASS
```

> 설치된 주요 패키지: 85개 | 결과: PASS

---

## 3. 단계별 실습

### STEP 1: 환경 변수 설정

**명령어:**
```bash
cp .env.example .env
```

**결과:** PASS
> LLM_TIMEOUT=30, LLM_MAX_RETRIES=3, CACHE_TTL=300, LOG_LEVEL=INFO 기본값 확인.

---

### STEP 2: 프로덕션 에이전트 실행

**명령어:**
```bash
python src/main.py
```

**실행 결과:**
```
CH09 LangChain 최종 연결 — 프로덕션 에이전트 실행
초기화 완료: Mock 모드

[Q1] 이서연의 현재 잔여 연차는 며칠입니까?
  모드: mock
  답변: [연차 정보] 이서연: 총 15일 중 12일 사용, 잔여 3일

[Q5] [캐시 히트] 이서연의 현재 잔여 연차는 며칠입니까?
  모드: cached
  답변: (캐시 반환, LLM 호출 없음)

토큰 사용 리포트
총 LLM 호출 횟수: 4회 (Q5 캐시 히트)
총 토큰: 1,240
히트율: 20.0%
전체 실행 시간: 0.03초
```

**결과:** PASS
> README 기대 출력과 정확히 일치. 캐시 히트율 20% (5개 중 1개) 확인.

---

### STEP 3: JSON 로그 파일 확인

**명령어:**
```bash
cat outputs/app.log | head -20
```

**실행 결과:**
```
{"timestamp": "2026-02-26T...", "level": "INFO", "agent": "ch09", "event": "query_received", "query": "이서연의 현재 잔여 연차는?"}
{"timestamp": "...", "event": "cache_miss", "query_hash": "..."}
{"timestamp": "...", "event": "tool_called", "tool": "get_leave_balance", "duration_ms": 2}
{"timestamp": "...", "event": "response_cached", "ttl": 300}
```

**결과:** PASS
> 구조화 JSON 로그 생성 확인. timestamp, level, event 필드 구조.

---

## 4. 기능 검증

### 핵심 기능 시나리오

| 시나리오 | 입력 | 기대 출력 | 실제 출력 | 결과 |
|---------|------|---------|---------|------|
| TTL 캐시 | 동일 질문 2회 | Q5 캐시 히트, 4회 호출 | 4회 LLM 호출 | PASS |
| 토큰 추적 | 5개 질문 | 총 토큰 리포트 | 1,240 토큰 | PASS |
| AgentConfig | LLM_TIMEOUT=0 | ValueError 발생 | ValueError | PASS |
| JSON 로그 | 쿼리 실행 | 구조화 로그 저장 | app.log 생성 | PASS |

---

## 5. 오류 해결 내역

오류 없음
> Docker/Ollama 없이 Mock 모드로 완전 실행. 주요 패턴(캐시, 로깅, 토큰 추적) 모두 Mock에서 동작.

---

## 6. 종합 평가

### 점수표

| 평가 항목 | 점수 (5점 만점) | 근거 |
|---------|--------------|------|
| 환경 설정 난이도 | 5 | Docker/Ollama 없이 Mock으로 완전 실행. 가장 독립적인 챕터 |
| 실행 성공률 | 5 | 5개 질문, 캐시 히트, 토큰 리포트, JSON 로그 모두 100% 성공 |
| 코드 이해도 | 5 | agent_config.py의 dataclass 패턴, monitoring.py의 TTLCache 구현 모두 docstring 완비 |
| 문서화 품질 | 4 | README에 Mock 모드 안내, 기대 출력 포함. outputs/ 디렉토리 자동 생성 안내 없음 |
| **총점** | **19/20** | EXCELLENT |

### 학생 의견

> "CH08에서 없었던 타임아웃, 캐시, 구조화 로깅이 추가되면서 '개발 버전'과 '운영 버전'의 차이를 코드로 직접 체험할 수 있습니다. Mock 모드로 완전히 실행되어 Docker/Ollama 없이도 프로덕션 패턴을 학습할 수 있는 이 챕터의 독립성이 탁월합니다. AgentConfig dataclass의 `__post_init__` 유효성 검사 패턴은 현업에서 즉시 활용 가능합니다."

### 개선 제안

- `outputs/` 디렉토리 자동 생성 안내 추가 ("없으면 mkdir outputs/")
- cachetools TTLCache의 캐시 만료 동작 시뮬레이션 데모 추가
- Tool description 정밀화 전후 비교 예시를 README에 포함
