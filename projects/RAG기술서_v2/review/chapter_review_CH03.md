# CH03 개발 환경 구축 — 독자 리뷰 보고서

> 작성일: 2026-02-26 | 리뷰 방식: 학생 입장 직접 따라하기 | 챕터 컨셉: 팀 표준 환경 구축

---

## 1. 챕터 개요

| 항목 | 내용 |
|------|------|
| 학습 목표 | Ollama + PostgreSQL(Docker) + Python venv + .env 환경 구축, setup_check.py 5/5 PASS |
| 전제 조건 | Docker Desktop, Python 3.11, Git |
| 실행 단계 수 | 4단계 (Ollama → PostgreSQL Docker → venv → .env 설정) |
| 실제 소요 시간 | 약 30~60분 (모델 다운로드 포함) |

## 2. 환경 점검 결과

| 항목 | 상태 | 비고 |
|------|------|------|
| Python 버전 | PASS | 3.14.3 (챕터 권장: 3.11. 3.11+ 호환 가능) |
| Ollama | PASS | 설치 및 실행 중 |
| Docker | FAIL | 이 리뷰 환경에서 미설치 |
| Git | PASS | 설치됨 |

## 3. 단계별 실행 결과

### STEP 1: Ollama 설치 및 모델 다운로드

**원고 지시:** `curl -fsSL https://ollama.com/install.sh | sh` → `ollama pull deepseek-r1`

**실제 상태:** 이미 Ollama 설치됨, deepseek-r1:1.5b 설치됨

**결과:** PASS

**비고:** 챕터에서 RAM 기준 모델 선택 가이드(4GB/8GB/16GB)를 명확하게 제시한 점이 매우 유용함.

---

### STEP 2: PostgreSQL Docker Compose

**원고 지시:** `docker-compose up -d`

**실제 상태:** Docker 미설치로 실행 불가 (SKIP)

**결과:** SKIP (Docker 미설치 환경)

**비고:** 챕터에 "Cannot connect to the Docker daemon" 오류 해결법이 안내되어 있어 독자 친화적.

---

### STEP 3: Python venv 및 패키지 설치

**원고 지시:** `python3 -m venv venv` → `source venv/bin/activate` → `pip install -r requirements.txt`

**결과:** 정적 분석 - 절차 명확, requirements.txt 내용 적절

**비고:** macOS/Linux와 Windows 명령어를 각각 안내하는 점이 좋음.

---

### STEP 4: .env 설정 및 setup_check.py

**원고 지시:** `cp .env.example .env` → `python src/setup_check.py`

**예제 코드 검증:**
- `.env.example` 내용이 챕터 발췌와 일치
- `AppConfig` dataclass 구조가 챕터 설명과 일치
- 5/5 PASS 출력 형식 일치

**결과:** PASS (정적 분석)

---

## 4. 챕터 원고 품질 평가

| 항목 | 점수 (5점) | 근거 |
|------|----------|------|
| 설명 충분성 | 5 | Docker vs 직접 설치 비교표, 가상환경 필요 이유 등 충분한 배경 설명 |
| Why 설명 | 5 | 왜 Docker Compose인가, 왜 venv인가, 왜 .env인가 모두 명확히 설명 |
| 실행 재현성 | 4 | Docker 미설치 시 오류 안내 있음. Python 3.11 요구 vs 3.12+ 호환성 문제 미언급 |
| 코드 발췌 정확성 | 5 | docker-compose.yml, AppConfig 발췌가 실제 코드와 일치 |
| 오류 대응 안내 | 5 | FAIL 항목별 해결 방법 표가 탁월. 포트 충돌 해결법까지 포함 |
| 분량 적절성 | 5 | 환경 구축 챕터로 적절한 분량. 이서연 스토리로 도입하여 지루하지 않음 |
| **총점** | **29/30** | |

## 5. 발견된 문제점

1. **Python 버전 안내**: "Python 3.11 기준 작성" 명시되어 있으나 3.12, 3.13, 3.14 호환성 확인 안내 부재. 현재 환경(3.14.3)에서 일부 패키지 호환성 이슈 가능.
2. **Docker 없는 환경 대안**: Docker 미설치 시 PostgreSQL을 어떻게 대체할지(예: SQLite) 안내 없음. 입문자는 여기서 막힐 수 있음.

## 6. 학생 한 줄 평

> "FAIL 항목별 해결 방법 표가 특히 실용적이며, 이서연이 겪은 세 가지 실패 사례로 시작하는 도입부가 '왜 이 챕터가 필요한가'를 자연스럽게 납득시키는 잘 구성된 환경 구축 가이드입니다."

## 7. 개선 제안

- Python 3.12+ 사용자를 위한 호환성 안내 추가 (특히 일부 패키지)
- Docker 미설치 환경에서 PostgreSQL 대안(Docker Desktop 설치 안내 강화 또는 SQLite Mock 옵션) 제공
- setup_check.py의 Python 버전 체크를 "3.11.x"가 아닌 "3.11+" 범위로 유연하게 처리
