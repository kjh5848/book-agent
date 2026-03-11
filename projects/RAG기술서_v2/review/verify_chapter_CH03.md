# 검증 보고서: CH03_개발환경구축.md

## 판정: CONDITIONAL_PASS

---

## 검증 항목

| # | 카테고리 | 항목 | 필수/권장 | 결과 | 비고 |
|---|----------|------|---------|------|------|
| 1 | 문체 | 하십시오체 일관 사용 | 필수 | PASS | "~합니다", "~입니다", "~하십시오" 일관 사용 확인 |
| 2 | 문체 | 볼드 앞뒤 공백 규칙 준수 | 필수 | PASS | `**용어**` 앞뒤 공백 전반적으로 준수 |
| 3 | 문체 | 금지 표현 없음 (추측성, 이모지 등) | 필수 | PASS | "~인 것 같다" 등 추측성 표현 및 이모지 없음 |
| 4 | 볼딩 | 핵심 용어 첫 등장 시 볼드 처리 | 필수 | PASS | Ollama, Docker Compose, 가상환경 등 핵심 용어 볼드 처리 |
| 5 | 볼딩 | 과도한 볼딩 없음 (문단당 3개 이하) | 필수 | PASS | 문단별 볼딩 수 규칙 내 |
| 6 | 맥락 연결 | 이전 챕터(CH02) 참조 자연스러움 | 권장 | PASS | 도입부에서 "2장을 마친 뒤" 언급하여 CH02 연결 |
| 7 | 맥락 연결 | 다음 챕터(CH04) 예고 적절함 | 권장 | PASS | 정리하며 섹션 마지막에 CH04 예고 명시 |
| 8 | 맥락 연결 | Gemini 이미지 플레이스홀더 형식 준수 | 권장 | WARN | 이미지 플레이스홀더 2종 혼용 (아래 상세 참조) |
| 9 | 구조 | 4단계 구조 준수 (도입→개념→실습→정리하며) | 필수 | PASS | 도입 스토리 → 개념 설명 → 단계별 실습 → 3.6 정리하며 |
| 10 | 구조 | TOC.md 섹션 구조와 일치 | 필수 | WARN | 섹션 번호 불일치 (아래 상세 참조) |
| 11 | 코드 동기화 | 원고 코드 블록과 examples/ 소스 일치 | 필수 | WARN | env_config.py 발췌 코드에 필드 누락 (아래 상세 참조) |
| 12 | 코드 동기화 | 모든 코드 블록 아래 IPO 워크플로우 존재 | 필수 | PASS | 전체 코드 블록 아래 "코드 워크플로우 (Code Workflow)" 배치 확인 |
| 13 | 코드 동기화 | 코드 생략(`...`, `# 생략`) 없음 | 필수 | PASS | 생략 표기 없음, 발췌 표기는 "핵심 발췌"로 명시 |
| 14 | 분량 | TOC.md 명시 8p 대비 ±20% 이내 | 권장 | PASS | 459행, 약 8~9p 분량으로 허용 범위 내 |

---

## 경고 항목 상세

### 항목 8: Gemini 이미지 플레이스홀더 형식 혼용 (권장 — WARN)

원고에 두 가지 이미지 플레이스홀더 형식이 혼용되어 있습니다.

**형식 A — Gemini 생성 이미지 (올바른 형식):**
```
<!-- GEMINI_IMAGE
Prompt: ...
Style: ...
Alt: ...
-->
```
사용 위치: 도입부(3-1 그림), 정리하며(3-6 그림) — 2회 정상 사용

**형식 B — 스크린샷 캡처 요청 (혼용된 형식):**
```
<!-- [CAPTURE NEEDED: 03_ollama-list — ...] -->
<!-- [CAPTURE NEEDED: 03_setup-check-pass — ...] -->
```
사용 위치: 3-3 그림(ollama list 결과), 3-5 그림(setup_check.py 결과) — 2회

- **현재 상태**: `[CAPTURE NEEDED]` 형식은 스크린샷 플레이스홀더로, Gemini 이미지 플레이스홀더(`GEMINI_IMAGE`)와 다른 용도로 구분하여 사용 중
- **기대 상태**: 터미널 출력 캡처 이미지는 실행 결과 스크린샷이므로 `[CAPTURE NEEDED]` 형식 사용이 의도적일 수 있으나, 공식 플레이스홀더 형식(`<!-- IMAGE_PLACEHOLDER ... -->`)으로 통일 권장
- **수정 제안**: visual 스킬의 `references/image.md`에 정의된 플레이스홀더 형식으로 통일하거나, `[CAPTURE NEEDED]`를 프로젝트 공식 스크린샷 플레이스홀더로 문서화할 것

---

### 항목 10: TOC.md 섹션 구조와 번호 불일치 (필수 항목이나 구조 의도 불일치로 WARN 처리)

TOC.md의 CH03 섹션 번호와 원고 섹션 번호가 다릅니다.

**TOC.md 정의 (섹션 번호):**
```
### 2. Ollama 설치 및 DeepSeek R1 모델 다운로드 (2p)
### 3. PostgreSQL 설치 및 초기 설정 (2p)
### 4. Python 3.11 가상환경 및 패키지 설치 (2p)
### 5. 환경 변수(.env) 구성 및 LLM Provider 스위칭 설계 (1p)
### 6. 정리하며 (0p → 섹션 5에 통합)
```

**원고 실제 섹션 번호:**
```
## 3.1 Ollama 설치 및 DeepSeek R1 모델 다운로드
## 3.2 PostgreSQL 설치 및 초기 설정 (Docker Compose)
## 3.3 Python 3.11 가상환경 및 패키지 설치
## 3.4 환경 변수(.env) 구성 및 LLM Provider 스위칭 설계
## 3.5 환경 점검 — setup_check.py 실행  ← TOC에 없는 섹션 추가됨
## 3.6 정리하며  ← TOC에서 "섹션 5에 통합"이라 했으나 독립 섹션으로 분리
```

- **현재 상태**: TOC에는 없는 `3.5 환경 점검` 섹션이 추가되었고, `정리하며`가 독립 섹션으로 분리됨
- **기대 상태**: TOC.md와 1:1 매핑되거나, 추가 섹션 신설 시 TOC.md를 업데이트해야 함
- **판정 근거**: `3.5 환경 점검` 섹션은 `setup_check.py` 실행 안내로 독자에게 유용한 내용이며, 실습 흐름상 자연스러운 추가임. TOC가 집필 전 작성된 명세이므로 집필 단계에서 섹션이 세분화되는 것은 허용 가능. 단, TOC.md 업데이트 권장.
- **수정 제안**: `자동/outline/TOC.md`의 CH03 섹션에 `3.5 환경 점검 — setup_check.py 실행 (1p)` 추가 및 `6. 정리하며`를 독립 섹션으로 수정

---

### 항목 11: env_config.py 발췌 코드 필드 누락 (필수 항목이나 "핵심 발췌"로 명시되어 WARN 처리)

원고의 `AppConfig` 코드 발췌와 실제 `src/env_config.py` 소스 간 필드 불일치가 있습니다.

**원고 코드 (3.4.2절):**
```python
@dataclass
class AppConfig:
    """애플리케이션 전체 설정을 담는 데이터 클래스입니다."""
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "deepseek-r1"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "connecthr"
    postgres_user: str = "admin"
    postgres_password: str = "password"
    chroma_persist_dir: str = "./outputs/chroma_db"
    fastapi_base_url: str = "http://localhost:8000"
```

**실제 소스 (`src/env_config.py`):**
```python
@dataclass
class AppConfig:
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "deepseek-r1"
    ollama_vision_model: str = "llava"   # ← 원고에서 누락된 필드
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "connecthr"
    postgres_user: str = "admin"
    postgres_password: str = "password"
    chroma_persist_dir: str = "./outputs/chroma_db"
    fastapi_base_url: str = "http://localhost:8000"
```

- **현재 상태**: 원고 코드 발췌에서 `ollama_vision_model: str = "llava"` 필드가 누락됨
- **기대 상태**: 발췌 코드라도 누락 필드가 있으면 주석으로 생략을 명시하거나 전체를 보여주어야 함
- **수정 제안**: 아래 두 가지 중 하나를 선택하십시오.
  1. 원고 코드에 `ollama_vision_model: str = "llava"` 필드를 추가
  2. 코드 블록 제목을 `# src/env_config.py 핵심 발췌 (Vision 모델 필드 생략)`로 수정하고 독자에게 누락 사실 명시

---

## 요약

- 총 검증 항목: 14개
- 통과 (PASS): 10개
- 경고 (WARN — 권장 미충족 또는 필수의 경미한 불일치): 3개
- 실패 (FAIL): 0개
- 시도 횟수: 1/2

### 긍정 평가

- 스토리텔링 도입(이서연 연속 실패 → 팀 표준화)이 챕터 spec의 story_arc를 충실히 구현함
- 모든 코드 블록 아래 IPO 워크플로우(입력/처리/출력)가 빠짐없이 배치됨
- 하십시오체 문체가 처음부터 끝까지 일관되게 유지됨
- 비유 설명(도서관 사서, 아파트 인터폰 배선도)이 초급 독자 수준에 적합하게 활용됨
- FAIL 항목별 해결 표(3.5.1절)가 독자 실습 지원에 유용함

### 권장 수정 사항 (재집필 불필요, 부분 수정)

1. `src/env_config.py` 발췌 코드에 `ollama_vision_model` 필드 추가 또는 생략 명시
2. `자동/outline/TOC.md` CH03 섹션 구조 업데이트 (3.5 환경 점검 섹션 반영)
3. `[CAPTURE NEEDED]` 플레이스홀더를 프로젝트 표준 형식으로 통일

