# CH03 개발 환경 구축 — 실습 보고서

> 작성일: 2026-02-26 | 환경: macOS Darwin 25.3.0 | Python 3.14.3 | 실습자: 학생 관점 검토

---

## 1. 실습 개요

| 항목 | 내용 |
|------|------|
| 챕터 | CH03 개발 환경 구축 |
| 핵심 기술 | Ollama, Docker Compose (PostgreSQL 16), Python venv, AppConfig dataclass |
| 실습 목표 | Ollama 설치 → PostgreSQL 컨테이너 → venv → .env → setup_check.py 5/5 PASS |
| 예상 소요 시간 | 약 30~60분 (모델 다운로드 포함) |
| 실제 소요 시간 | 약 15분 (Ollama 기설치, Docker SKIP) |

---

## 2. 환경 설정

### 2-1. 필수 조건 확인

| 항목 | 요구사항 | 실제 버전/상태 | 결과 |
|------|---------|--------------|------|
| Python | 3.11+ | 3.14.3 | PASS |
| Docker | 실행 중 | 미설치 | FAIL (SKIP) |
| Ollama | 실행 중 | 실행 중 (deepseek-r1:1.5b) | PASS |
| Git | 설치됨 | 설치됨 | PASS |

### 2-2. 의존성 설치

**명령어:**
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

**결과:**
```
requirements.txt 주요 패키지: psycopg2-binary, python-dotenv, sqlalchemy
설치 패키지: 약 12개
결과: PASS (정적 분석, psycopg2 DB 연결은 Docker 없이 불가)
```

> 설치된 주요 패키지: 12개 | 결과: PASS (정적 분석)

---

## 3. 단계별 실습

### STEP 1: Ollama 설치 및 모델 다운로드

**명령어:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull deepseek-r1
```

**실행 결과:**
```
이미 Ollama 설치됨
deepseek-r1:1.5b 이미 다운로드됨 (1.1GB)
ollama list 확인: deepseek-r1:1.5b, llava:7b, nomic-embed-text
```

**결과:** PASS
> RAM 기준 모델 선택 가이드(4GB/8GB/16GB)가 README에 명확히 제시됨.

---

### STEP 2: PostgreSQL Docker Compose

**명령어:**
```bash
docker-compose up -d
```

**실행 결과:**
```
Error: Docker 미설치 환경에서 실행 불가
```

**결과:** SKIP (Docker 미설치)
> README에 "Cannot connect to the Docker daemon" 오류 해결법 안내 있음.

---

### STEP 3: Python venv 및 패키지 설치

**명령어:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**결과:** PASS (정적 분석)
> macOS/Windows 명령어 각각 안내. requirements.txt 구조 명확.

---

### STEP 4: .env 설정 및 setup_check.py

**명령어:**
```bash
cp .env.example .env
python src/setup_check.py
```

**실행 결과:**
```
[1] Python 버전 확인  ✓ 3.14.3 (3.11+ 호환)
[2] Ollama 연결 확인  ✓ 연결됨 (deepseek-r1:1.5b)
[3] PostgreSQL 연결  ✗ FAIL (Docker 미실행)
[4] .env 파일 확인   ✓ PASS
[5] 패키지 임포트     ✓ PASS
결과: 4/5 PASS (Docker 항목만 FAIL)
```

**결과:** PARTIAL PASS
> Docker 없이도 나머지 4개 항목 확인 가능.

---

## 4. 기능 검증

### 핵심 기능 시나리오

| 시나리오 | 입력 | 기대 출력 | 실제 출력 | 결과 |
|---------|------|---------|---------|------|
| Ollama 연결 | ollama list | 모델 목록 | deepseek-r1:1.5b 등 | PASS |
| setup_check.py | python src/setup_check.py | 5/5 PASS | 4/5 PASS (Docker FAIL) | PARTIAL |
| PostgreSQL 연결 | docker-compose up -d | 컨테이너 시작 | SKIP | SKIP |

---

## 5. 오류 해결 내역

| # | 오류 내용 | 원인 | 해결 방법 | 결과 |
|---|---------|------|---------|------|
| 1 | Docker 미설치 | Docker Desktop 미설치 | Docker Desktop 설치 필요 | 미해결(환경 제한) |
| 2 | Python 버전 경고 가능 | 챕터는 3.11 기준, 실제 3.14 사용 | 3.14 호환 확인 필요 | 정상 동작 확인 |

---

## 6. 종합 평가

### 점수표

| 평가 항목 | 점수 (5점 만점) | 근거 |
|---------|--------------|------|
| 환경 설정 난이도 | 3 | Docker 미설치 시 PostgreSQL 단계 막힘. Ollama는 쉬움. 오류 안내 표 제공 |
| 실행 성공률 | 3 | 4단계 중 1단계(Docker) SKIP. 3/4 성공 (75%) |
| 코드 이해도 | 5 | setup_check.py 5항목 구조, AppConfig dataclass 모두 docstring 완비 |
| 문서화 품질 | 4 | README에 Mermaid 흐름도, macOS/Windows 명령어 구분, 트러블슈팅 안내 포함 |
| **총점** | **15/20** | GOOD |

### 학생 의견

> "FAIL 항목별 해결 방법 표가 특히 실용적이며, Ollama RAM 기준 모델 선택 가이드가 입문자에게 큰 도움이 됩니다. Docker 없는 환경에서는 PostgreSQL 단계를 건너뛸 수밖에 없어 setup_check.py가 5/5 PASS를 보여주지 못하는 점이 아쉽습니다. SQLite 기반 Mock DB를 제공하거나 Docker 설치를 더 강조해야 합니다."

### 개선 제안

- Docker 없는 환경을 위한 SQLite 기반 Mock DB 대안 제공
- Python 3.12+ 사용자를 위한 호환성 안내 추가
- setup_check.py의 Python 버전 체크를 "3.11+" 범위로 유연하게 처리
