# ⚙️ LLM 모델 설정 및 전환 가이드

메타코딩 AI 비서는 로컬 LLM(Ollama)부터 클라우드 LLM(OpenAI)까지 다양한 모델을 지원합니다. 시스템 환경에 맞춰 최고의 성능을 내는 모델을 선택해 보세요.

---

## 1. 모델 전환 방법

프로젝트 루트 디렉토리의 `.env` 파일을 수정하여 사용 모델을 즉시 바꿀 수 있습니다.

### 옵션 A: 로컬 Ollama 사용 (기본값)

개인 PC의 자원을 사용하여 비용이 발생하지 않으며 보안에 유리합니다.

```bash
# .env 설정 예시
LLM_PROVIDER=ollama
LLM_MODEL_NAME=deepseek-r1:8b  # 또는 llama3, phi3 등
OLLAMA_BASE_URL=http://localhost:11434
```

### 옵션 B: OpenAI 사용 (빠른 속도, 고성능)

강력한 성능과 빠른 응답 속도가 필요할 때 사용합니다. (API Key 필요)

```bash
# .env 설정 예시
LLM_PROVIDER=openai
LLM_MODEL_NAME=gpt-4o  # 또는 gpt-3.5-turbo
OPENAI_API_KEY=your_api_key_here
```

---

## 2. 권장 모델 가이드

| 프로바이더 | 모델명             | 특징                      | 추천 상황              |
| :--------- | :----------------- | :------------------------ | :--------------------- |
| **Ollama** | `deepseek-r1:1.5b` | 매우 빠름, 저사양 가능    | 테스트용, 성능 확인    |
| **Ollama** | `deepseek-r1:8b`   | 추론 능력 우수, 다소 느림 | 정교한 분석 필요 시    |
| **Ollama** | `llama3:8b`        | 범용성 좋음, 표준 속도    | 일반적인 Q&A           |
| **OpenAI** | `gpt-4o-mini`      | 매우 빠름, 저렴함         | 운영 환경, 빠른 응답   |
| **OpenAI** | `gpt-4o`           | 최강 성능, 비쌈           | 복잡한 하이브리드 분석 |

---

## 3. 환경 설정 (.env) 적용 순서

1. 프로젝트 폴더에 `.env` 파일을 생성합니다.
2. 원하는 설정값을 입력하고 저장합니다.
3. 서버를 재시작합니다 (`python app/main.py`).

> [!TIP]
> **Ollama 사용 시 주의사항**: 모델 이름 뒤에 `:8b` 등 버전을 명확히 표기해야 하며, 해당 모델이 사전에 `ollama pull` 명령어로 설치되어 있어야 합니다.
