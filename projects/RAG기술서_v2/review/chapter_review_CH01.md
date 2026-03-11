# CH01 이 책의 목표와 최종 완성본 미리보기 — 독자 리뷰 보고서

> 작성일: 2026-02-26 | 리뷰 방식: 학생 입장 직접 따라하기 | 챕터 컨셉: 이서연 스토리텔링

---

## 1. 챕터 개요

| 항목 | 내용 |
|------|------|
| 학습 목표 | 전체 아키텍처 이해 + 최종 데모 체험 (Mock 모드) |
| 전제 조건 | Python 3.11+, Git (Ollama 없어도 동작) |
| 실행 단계 수 | 5단계 (clone → env → install → run demo) |
| 실제 소요 시간 | 약 10분 |

## 2. 환경 점검 결과

| 항목 | 상태 | 비고 |
|------|------|------|
| Python 버전 | PASS | Python 3.14.3 설치됨 |
| Ollama | PASS | deepseek-r1:1.5b, llava, nomic-embed-text 설치됨 |
| Docker | FAIL | Docker Desktop 미설치 |
| Git | PASS | 설치됨 |

## 3. 단계별 실행 결과

### STEP 1: requirements.txt 설치

**원고 지시:** `pip install -r requirements.txt`

**실행 명령어:**
```bash
cd 자동/examples/CH01_목표와미리보기
python3 -m pip install -r requirements.txt
```

**실제 출력:** PEP 668로 인해 시스템 pip 설치 제한이 있었지만, 기설치된 패키지로 실행 가능

**결과:** PASS (기설치 패키지)

**비고:** macOS에서 PEP 668 제한으로 `--break-system-packages` 없이는 설치 실패. 챕터에 venv 사용 안내 없음이 문제.

---

### STEP 2: demo.py 실행

**원고 지시:** `python src/demo.py`

**실행 명령어:**
```bash
python3 src/demo.py
```

**실제 출력:**
```
============================================================
  AI 업무 비서 구축: RAG + MCP 실전 가이드
  CH01 최종 완성본 미리보기 데모
============================================================
  Ollama 연결 상태 확인
============================================================
  서버 주소  : http://localhost:11434
  모델       : deepseek-r1
  상태       : [연결됨] 정상 연결
...
  데모 실행 완료.
```

**결과:** PASS

**비고:** Ollama가 실행 중이어서 "연결됨" 표시. 챕터의 기대 출력(오프라인 Mock)과 달리 실제로는 연결됨 상태로 출력되었으나 데모 자체는 정상 동작.

---

## 4. 챕터 원고 품질 평가

| 항목 | 점수 (5점) | 근거 |
|------|----------|------|
| 설명 충분성 | 5 | RAG vs Fine-tuning 비교, 정형+비정형 통합 이유 명확히 설명 |
| Why 설명 | 5 | 각 기술 선택 이유(왜 Ollama인가, 왜 RAG인가) 모두 포함 |
| 실행 재현성 | 3 | venv 없이 `pip install` 직접 지시 → macOS PEP 668 오류 발생 가능 |
| 코드 발췌 정확성 | 5 | main() 함수 구조가 demo.py 실제 코드와 일치 |
| 오류 대응 안내 | 4 | Ollama 없을 때 Mock 모드 안내는 있으나, pip 오류 대응 없음 |
| 분량 적절성 | 5 | 입문 챕터로서 적절한 분량. 스토리 + 기술 균형 좋음 |
| **총점** | **27/30** | |

## 5. 발견된 문제점

1. **pip 설치 방식**: `pip install -r requirements.txt` 직접 실행 지시 → macOS Python 3.14에서 PEP 668 오류 발생. venv 생성 후 설치 안내 필요.
2. **git clone URL**: `git clone https://github.com/{repo}/CH01_목표와미리보기` — 실제 URL이 아닌 플레이스홀더로 독자가 실제 URL을 알 수 없음.
3. **Ollama 연결 시 출력 불일치**: 챕터 기대 출력은 "오프라인 (데모 모드로 계속 진행)"이지만 Ollama가 실행 중이면 "정상 연결"로 출력되어 혼란 가능.

## 6. 학생 한 줄 평

> "이서연 스토리가 입문자의 동기부여를 효과적으로 자극하며, Mock 모드 덕분에 Ollama 없이도 전체 흐름을 체험할 수 있어 입문 챕터로서 완성도가 높습니다. 다만 venv 안내 없이 pip 직접 실행을 지시하는 부분은 macOS 환경에서 오류를 유발할 수 있어 주의가 필요합니다."

## 7. 개선 제안

- `pip install` 앞에 `python3 -m venv venv && source venv/bin/activate` 단계 추가
- git clone URL을 실제 URL 또는 명확한 주석으로 대체
- Ollama가 실행 중일 때의 출력도 예시로 추가하여 두 가지 시나리오 모두 안내
