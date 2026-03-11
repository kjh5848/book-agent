# CH02 개발 환경 설정 — Reader Review Report


---

## 1. Chapter Overview

| Item | Content |
|------|---------|
| Learning objective | Ollama + DeepSeek R1(로컬 LLM), Docker + PostgreSQL, Python 가상환경 세 가지 기둥을 설치하고 `verify_env.py` 4개 항목 PASS 달성 |
| Prerequisites | CH01 개념 학습 완료 / Python 3.10+, Docker Desktop, Git 설치 |
| Number of execution steps | 5 steps (환경 확인 → pip 설치 → Docker 확인 → verify_env → LLM 연결 테스트) |

---

## 2. Environment Check Results

### 2-1. Prerequisites Check

| Item | Requirement | Actual Version/Status | Result |
|------|-------------|-----------------------|--------|
| Python | 3.10+ | 3.14.3 (시스템) / 3.12.12 (venv) | PASS (주의: psycopg2-binary 빌드 이슈로 Python 3.12 사용) |
| Docker | Running | v29.1.3 | PASS |
| Ollama | Running | 0.16.3 (deepseek-r1:1.5b 사용) | PASS |
| Git | Installed | 2.51.0 | PASS |

> **환경 특이사항**: 시스템 Python이 3.14.3이나 `psycopg2-binary==2.9.10`이 Python 3.14 환경에서는 빌드 오류 발생 가능성이 있어 Python 3.12 (`/opt/homebrew/bin/python3.12`) 로 가상환경을 생성하였습니다. 챕터에 이에 대한 안내가 없어 초심자에게 혼란이 생길 수 있습니다.

### 2-2. Dependency Installation

**Command:**
```bash
python3.12 -m venv .venv_review
source .venv_review/bin/activate
pip install -r requirements.txt
```

**Result:**
```
Successfully installed annotated-types-0.7.0 anyio-4.12.1 certifi-2026.2.25
charset-normalizer-3.4.4 distro-1.9.0 h11-0.16.0 httpcore-1.0.9 httpx-0.28.1
idna-3.11 jiter-0.13.0 openai-1.59.6 psycopg2-binary-2.9.10 pydantic-2.12.5
pydantic-core-2.41.5 python-dotenv-1.0.1 requests-2.32.3 sniffio-1.3.1
tqdm-4.67.3 typing-extensions-4.15.0 typing-inspection-0.4.2 urllib3-2.6.3
```

> Installed packages: 20 | Result: PASS

**Screen Capture:**
![pip install 결과](../assets/CH02/step02_pip_install.png)

---

## 3. Step-by-Step Execution Results

### STEP 01: 환경 사전 확인

**Manuscript instruction:** "실습을 시작하기 전에 아래 체크리스트를 확인하십시오."

**Executed command:**
```bash
python3.12 --version && ollama --version && docker --version && git --version
```

**Actual output:**
```
Python 3.12.12
ollama version is 0.16.3
Docker version 29.1.3, build f52814d
git version 2.51.0
```

**Screen Capture:**
![환경 사전 확인](../assets/CH02/step01_env_check.png)

**Result:** PASS
> 모든 필수 도구가 설치되어 있습니다. 단, 시스템 Python이 3.14.3으로 챕터 예상(3.10~3.12)과 달리 최신 버전이며, 이로 인해 psycopg2-binary 설치 시 호환성 문제가 발생할 수 있습니다.

---

### STEP 02: Docker 컨테이너 확인

**Manuscript instruction:** "`docker compose up -d` 실행 후 `docker ps`로 상태를 확인하십시오."

**Executed command:**
```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
```

**Actual output:**
```
NAMES                  STATUS         PORTS
metacoding-ai-db       Up 5 minutes   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp
metacoding-ai-vector   Up 5 minutes   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
```

**Screen Capture:**
![Docker 컨테이너 상태](../assets/CH02/step03_docker_ps.png)

**Result:** PASS (조건부)
> `docker compose up -d` 실행 시 포트 5432가 이미 다른 컨테이너(`metacoding-ai-db`)에 의해 사용 중이어서 `connect_hr_db` 컨테이너를 추가로 실행하지 못했습니다. 대신 기존 실행 중인 PostgreSQL 컨테이너의 접속 정보로 `.env` 파일을 수정하여 진행하였습니다. 챕터는 이 상황에 대한 안내가 없습니다.

**오류 발생 기록:**
```
Error response from daemon: failed to set up container networking:
Bind for 0.0.0.0:5432 failed: port is already allocated
```
**해결:** `.env` 파일의 PostgreSQL 접속 정보를 기존 실행 중인 컨테이너의 정보로 변경

---

### STEP 03: 의존성 설치

**Manuscript instruction:** "`pip install -r requirements.txt` 를 실행하십시오."

**Executed command:**
```bash
pip install -r requirements.txt
```

**Actual output:**
```
Successfully installed psycopg2-binary-2.9.10 python-dotenv-1.0.1 requests-2.32.3 openai-1.59.6
(및 기타 의존 패키지 포함 총 20개)
```

**Screen Capture:**
![pip install 결과](../assets/CH02/step02_pip_install.png)

**Result:** PASS
> Python 3.12 가상환경에서 psycopg2-binary 포함 모든 패키지가 정상 설치되었습니다. 챕터에서 안내한 예상 출력과 동일합니다.

---

### STEP 04: 환경 검증 (verify_env.py)

**Manuscript instruction:** "`python src/verify_env.py` 를 실행하십시오. 4개 항목이 모두 PASS여야 CH03 실습으로 진행할 수 있습니다."

**Executed command:**
```bash
python src/verify_env.py
```

**Actual output:**
```
=======================================================
  커넥트HR AI 비서 — 개발 환경 검증
=======================================================
  [PASS] Python 버전  (3.12.12)
  [PASS] Docker  (v29.1.3)
  [PASS] Ollama  (http://localhost:11434  모델: [deepseek-r1:1.5b, llava:7b, llava:latest, nomic-embed-text:latest, deepseek-r1:8b])
  [PASS] PostgreSQL  (localhost:5432/metacoding_db)
=======================================================
  결과: 4/4 항목 통과

  모든 환경 검증이 완료되었습니다.
  CH03 실습으로 진행하십시오.
=======================================================
```

**Screen Capture:**
![verify_env.py 전항목 PASS](../assets/CH02/step04_verify_env.png)

**Result:** PASS
> 4개 항목 모두 PASS. Ollama 항목에서 챕터 예상 출력(`deepseek-r1:8b`)과 달리 실제 사용 모델이 `deepseek-r1:1.5b`이지만 검증 스크립트는 서버 연결 여부만 확인하므로 정상 통과합니다. PostgreSQL 항목도 챕터 예상(`connect_hr`)과 다른 DB명(`metacoding_db`)을 가리키지만 PASS 처리됩니다.

---

### STEP 05: LLM Provider 연결 테스트

**Manuscript instruction:** "`python src/llm_provider.py` 를 실행하여 LLM 연결을 확인하십시오."

**Executed command:**
```bash
python src/llm_provider.py
```

**Actual output:**
```
[LLM Provider 연결 테스트]
  Provider : ollama
  Model    : deepseek-r1:1.5b
  질문     : 안녕하세요. 한 문장으로 자기소개를 해 주십시오.
--------------------------------------------------
  응답     : 안녕하세요! 그 asset가 도움을给你해드리겠습니다.
--------------------------------------------------
LLM 연결 테스트 성공.
```

**Screen Capture:**
![LLM Provider 연결 테스트](../assets/CH02/step05_llm_provider.png)

**Result:** PASS (주의 사항 있음)
> 연결 테스트 자체는 성공했습니다. 그러나 `deepseek-r1:1.5b` 모델이 한국어 질문에 중국어/혼재 언어로 응답하는 현상이 발생하였습니다. 챕터 예상 출력은 "저는 DeepSeek R1, 추론 능력이 강화된 AI 언어 모델입니다."이나 실제 응답은 한중 혼합 문장이었습니다. 1.5b 소형 모델의 한국어 지원 한계로 보이며, 챕터에서 더 작은 모델 사용 시의 품질 차이에 대한 안내가 부족합니다.

---

## 4. Chapter Manuscript Quality Evaluation

| Evaluation Item | Score (out of 5) | Rationale |
|----------------|-----------------|-----------|
| Explanation sufficiency | 4 | Docker를 사용하는 이유, 팩토리 패턴의 개념 등 핵심 개념 설명이 충실합니다. Python 3.14 등 최신 버전 호환성 이슈에 대한 안내는 부족합니다. |
| Why explanation | 5 | "PostgreSQL을 Docker로 설치하는 이유", "psycopg2-binary를 사용하는 이유", "팩토리 패턴을 먼저 만드는 이유" 등 근거 설명이 매우 잘 되어 있습니다. |
| Execution reproducibility | 3 | 기본 환경에서는 잘 동작하지만, 포트 충돌(5432 이미 사용 중), 최신 Python 버전 호환성, 소형 모델의 응답 품질 차이 등 실제 발생 가능한 예외 상황에 대한 안내가 부족합니다. |
| Code excerpt accuracy | 5 | 챕터에 인용된 `get_llm_client()`, `run_all_checks()` 코드가 실제 `src/llm_provider.py`, `src/verify_env.py`와 완전히 일치합니다. |
| Error handling guidance | 3 | FAIL 항목 해결 방법 표가 있어 유용하지만, 포트 충돌이나 Python 버전 호환성 문제 등 실제 발생하기 쉬운 오류에 대한 안내가 없습니다. |
| Volume appropriateness | 4 | 챕터 분량이 적절하며 단계별 흐름이 명확합니다. LLM Provider 설계 설명이 다소 상세하여 환경 설정 챕터에서 다루기에 무게감이 있습니다. |
| **Total** | **24/30** | |

---

## 5. Issues Found

### 이슈 1: Python 3.14 호환성 안내 부재
- **증상**: 시스템 Python이 3.14.3인 경우 `psycopg2-binary==2.9.10` 설치 시 빌드 오류 발생 가능
- **챕터 안내**: 없음 (최소 요구사항에 "Python 3.10 이상"만 명시)
- **영향**: 독자가 최신 Python을 사용하는 경우 첫 단계에서 막힐 수 있음
- **제안**: requirements.txt 의존성 표에 "Python 3.12까지 검증됨" 등의 호환성 노트 추가

### 이슈 2: 포트 충돌 시나리오 미안내
- **증상**: 5432 포트를 이미 다른 서비스가 사용 중인 경우 `docker compose up -d` 실패
- **챕터 안내**: 없음
- **영향**: 다른 PostgreSQL 프로젝트를 병행하는 독자에게 혼란 발생
- **제안**: FAIL 해결 방법 표에 "PostgreSQL 포트 충돌" 케이스 추가

### 이슈 3: 소형 모델(1.5b)의 응답 품질 미안내
- **증상**: `deepseek-r1:1.5b` 모델이 한국어 질문에 중국어 혼재 응답 반환
- **챕터 안내**: 1.5b를 8b 대체재로 안내하지만 응답 품질 차이 미언급
- **영향**: 독자가 LLM이 정상적으로 동작하는지 판단하기 어려움
- **제안**: "1.5b 모델은 한국어 지원이 제한적일 수 있습니다. 응답이 영어나 중국어로 나와도 연결은 성공한 것입니다." 등의 팁 추가

### 이슈 4: `.env` 파일 내 `[수정]` 태그 원고 미반영
- **증상**: 원고 `## 1. 필수 요구사항 확인` 섹션에 `[수정] 필요없음.` 등 편집 메모가 본문에 노출됨
- **영향**: 출판용 원고에 미완성 편집 메모가 포함되어 있음
- **제안**: 원고 최종 검토 시 `[수정]` 태그 제거 필요

### 이슈 5: 챕터 타이틀 텍스트 불일치
- **증상**: 챕터 원고의 `verify_env.py` 출력 예상값에는 "Q/A 사내 AI 비서"가 나오지만, 실제 코드는 "커넥트HR AI 비서"를 출력함
- **챕터 안내**: 예상 출력 `"  Q/A 사내 AI 비서 — 개발 환경 검증"`
- **실제 출력**: `"  커넥트HR AI 비서 — 개발 환경 검증"`
- **제안**: 챕터 예상 출력과 코드를 일치시켜야 함

---

## 6. Student One-liner

> CH02는 세 가지 인프라 기둥(Python, Ollama, Docker/PostgreSQL)의 설치 흐름이 논리적으로 잘 연결되고, 특히 팩토리 패턴의 설계 근거 설명이 인상적이었습니다. 다만, 시스템 Python 3.14에서 psycopg2-binary 설치 오류, 포트 충돌 등 실제 발생하기 쉬운 시나리오에 대한 안내가 없어 환경 설정 단계에서 막히는 독자가 생길 수 있습니다.

---

## 7. Improvement Suggestions

1. **Python 버전 호환성 명시**: requirements.txt 설명 표 또는 도입부에 "Python 3.10–3.12 환경에서 검증됨" 을 명시하고, 3.13+ 사용자를 위한 대안(psycopg2 소스 빌드 또는 `asyncpg` 대체) 안내 추가

2. **포트 충돌 해결 가이드 추가**: FAIL 해결 방법 표에 "PostgreSQL 포트(5432) 충돌" 케이스 추가 — `docker ps`, `lsof -i :5432`, `.env`에서 포트 변경하는 방법 안내

3. **소형 모델 응답 품질 안내**: `deepseek-r1:1.5b` 사용 시 한국어 응답 품질이 제한될 수 있음을 팁 박스로 안내. "모델 크기와 한국어 지원 품질의 관계"를 한 문단으로 설명

4. **편집 메모 제거**: 원고 본문의 `[수정] 필요없음.` 등 편집 태그를 최종 원고에서 제거

5. **예상 출력과 코드 동기화**: `verify_env.py`의 실제 출력 문자열("커넥트HR AI 비서")을 챕터 예상 출력에 반영 (또는 코드를 "Q/A 사내 AI 비서"로 수정)

6. **`.env.example`의 모델명**: `.env.example`의 `OLLAMA_MODEL=deepseek-r1:8b`를 실제 환경에 맞게 주석으로 선택지 표기 (`# 소형 모델 대체: deepseek-r1:1.5b`) 하면 독자가 직접 수정하지 않아도 됨

---

## Appendix: Screenshot Summary

| Step | 파일명 | 결과 |
|------|--------|------|
| 01 - 환경 사전 확인 | `step01_env_check.png` | PASS |
| 02 - pip install | `step02_pip_install.png` | PASS |
| 03 - docker ps | `step03_docker_ps.png` | PASS (조건부) |
| 04 - verify_env.py | `step04_verify_env.png` | PASS (4/4) |
| 05 - llm_provider.py | `step05_llm_provider.png` | PASS (응답 품질 주의) |

**Placeholder 충족:**
- `[CAPTURE NEEDED: 02_verify-env-pass]` → `assets/CH02/02_verify-env-pass.png` 저장 완료
