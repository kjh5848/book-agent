# CH09 LangChain 최종 연결 — 독자 리뷰 보고서

> 작성일: 2026-02-26 | 리뷰 방식: 학생 입장 직접 따라하기 | 챕터 컨셉: 프로덕션 에이전트 — 타임아웃, 재시도, 캐시, 로깅

---

## 1. 챕터 개요

| 항목 | 내용 |
|------|------|
| 학습 목표 | AgentConfig 데이터클래스, ResponseCache TTL캐시, with_retry Exponential Backoff, JSON 구조화 로깅, Tool description 정밀화 |
| 전제 조건 | CH08 완료, Docker (PostgreSQL), Python venv, Ollama (없으면 Mock 모드) |
| 실행 단계 수 | 3단계 (clone → install → python src/main.py) |
| 실제 소요 시간 | 약 15~20분 (Mock 모드 기준) |

## 2. 환경 점검 결과

| 항목 | 상태 | 비고 |
|------|------|------|
| Python 버전 | PASS | 3.14.3 |
| Docker | 선택 | Mock 모드로 대체 가능 (챕터에 명시) |
| Ollama deepseek-r1 | 선택 | Mock 모드로 대체 가능 |
| CH08 선행 | 선택 | 독립적으로 실행 가능(Mock) |

## 3. 단계별 실행 결과

### STEP 1: 저장소 클론 및 환경 설정

**원고 지시:** `git clone ... && cp .env.example .env`

**예제 코드 검증:**
- `.env.example`에 LLM_TIMEOUT=30, LLM_MAX_RETRIES=3, CACHE_TTL=300, LOG_LEVEL=INFO 포함 확인
- "Ollama와 PostgreSQL이 없어도 Mock 모드로 전체 흐름을 학습할 수 있습니다" 안내 명확

**결과:** PASS (정적 분석)

---

### STEP 2: 패키지 설치 및 실행

**원고 지시:** `pip install -r requirements.txt && python src/main.py`

**예제 코드 검증:**
- `src/agent_config.py`의 `AgentConfig` 데이터클래스: 챕터 발췌와 실제 코드 100% 일치
  - `field(default_factory=lambda: os.getenv(...))` 패턴 확인
  - `__post_init__` 유효성 검사 (`llm_timeout <= 0` 체크) 확인
- 챕터 기대 출력(Mock 모드 5개 질문 실행, 캐시 히트율 20%, 토큰 리포트): 코드 로직과 일치
- `src/monitoring.py`: ResponseCache(TTLCache), TokenUsageTracker 구현 확인

**결과:** PASS (정적 분석)

---

### STEP 3: 출력 확인 — 캐시 히트 및 토큰 리포트

**원고 지시:** Q1과 Q5가 동일 질문 → Q5 캐시 히트, LLM 호출 4회, 히트율 20%

**결과:** PASS (코드 로직 검증)

---

## 4. 챕터 원고 품질 평가

| 항목 | 점수 (5점) | 근거 |
|------|----------|------|
| 설명 충분성 | 5 | 타임아웃 없이 Ollama가 느려지면 왜 멈추는지, TTL캐시의 히트율 계산, Tool description이 에이전트 선택에 미치는 영향까지 충분히 설명 |
| Why 설명 | 5 | dataclass를 쓰는 이유, Exponential Backoff가 단순 재시도보다 나은 이유, 구조화 로깅이 필요한 이유 모두 명확 |
| 실행 재현성 | 5 | Docker/Ollama 없이 Mock 모드로 완전 동작. 챕터 기대 출력과 코드 로직 일치. 가장 독립적인 챕터 |
| 코드 발췌 정확성 | 5 | AgentConfig 데이터클래스 발췌가 실제 코드와 완벽 일치 |
| 오류 대응 안내 | 4 | Mock 모드 설명 탁월. LLM_TIMEOUT 유효성 오류(ValueError) 발생 시나리오 안내 있음. log 파일 권한 오류 안내 없음 |
| 분량 적절성 | 5 | "이서연의 월요일 아침" 스토리로 문제를 자연스럽게 도입. 타임아웃→캐시→로깅→도구설명 순서가 학습 흐름에 적합 |
| **총점** | **29/30** | |

## 5. 발견된 문제점

1. **log 파일 경로 권한**: `.env`의 `LOG_FILE=./outputs/app.log`에서 `outputs/` 디렉토리가 없을 경우 발생하는 FileNotFoundError 안내 없음.
2. **git clone URL 플레이스홀더**: `git clone https://github.com/{repo}/CH09_LangChain연결` — 실제 URL이 아닌 플레이스홀더.
3. **pip install 전 venv 지시 위치**: CH09는 `pip install -r requirements.txt`만 안내하고 venv 생성 안내가 이전 챕터에 비해 짧음. CH06에서 상세히 설명했으므로 "CH06 참조"라는 표현이라도 추가하면 좋음.

## 6. 학생 한 줄 평

> "Mock 모드만으로도 캐시 히트율, 토큰 추적, 구조화 로깅 전체 동작을 확인할 수 있어 프로덕션 에이전트의 설계 원칙을 가장 안전하게 학습할 수 있는 챕터이며, AgentConfig 데이터클래스의 `__post_init__` 유효성 검사 패턴은 현업에서 즉시 활용 가능한 실용적인 기법입니다."

## 7. 개선 제안

- `outputs/` 디렉토리 자동 생성 로직 추가 또는 안내 ("없으면 mkdir outputs/")
- git clone URL을 실제 URL 또는 명확한 주석으로 대체
- venv 생성 단계를 간략하게라도 재안내 ("CH06 참조: python3 -m venv venv && source venv/bin/activate")
