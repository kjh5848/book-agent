# CH01. 비전 및 기초 다지기 — 예제 코드 플랜 (example_plan)

## 1. 개요 및 목표

- **목표**: Ollama를 기반으로 DeepSeek R1 로컬 모델을 구동하고, 기초적인 프롬프트 질의응답을 구현하여 "할루시네이션(Hallucination)" 현상 등 기존 LLM의 한계점을 독자가 직접 체감하게 합니다.
- **주요 기능**:
  - Ollama API를 이용한 로컬 모델 연동
  - 단발성 질문(Zero-shot)에 대한 모델의 답변 도출

## 2. 파일 구성도

```text
anti_v2_book/examples/ch01/
├── requirements.txt      # 필요한 패키지 (langchain-ollama 등)
├── 01_basic_llm.py       # Ollama DeepSeek R1 로컬 연동 및 질의응답 테스트
└── README.md             # 초보자용 실행 가이드라인 및 캡처 삽입
```

## 3. 코드 아키텍처 및 IPO 명세

**`01_basic_llm.py`**
- **Input (입력)**: 파이썬 스크립트 내 하드코딩된 사용자 질문 (예: "우리 회사 규정상 올해 여름 휴가비는 얼마야?")
- **Process (처리)**: LangChain의 `ChatOllama` 모듈을 통해 로컬 DeepSeek R1 모델에 접근, 질문 전달 및 추론 대기
- **Output (출력)**: 터미널에 모델의 답변 출력 (할루시네이션 결과 유도)

## 4. 검증 시나리오 (Verification)

1. 사용자가 사전에 Ollama와 `deepseek-r1` 모델을 설치했다고 가정.
2. 가상환경 활성화 후 `pip install -r requirements.txt` 실행.
3. `python 01_basic_llm.py` 실행 시 로컬 모델이 응답을 반환하는지 로그 확인.
4. 이상 없이 실행되면 터미널 결과를 캡처하여 `assets/CH01_result_hallucination.png` 로 저장.
