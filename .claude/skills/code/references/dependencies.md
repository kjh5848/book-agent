# 의존성 관리 규칙

## 1. requirements.txt 규칙

- 반드시 **버전을 고정** 합니다. (재현성 보장)
- 주요 패키지와 유틸리티 패키지를 구분합니다.

```txt
# Core
langchain==0.2.16
chromadb==0.5.5
ollama==0.3.1

# Utilities
python-dotenv==1.0.1
tqdm==4.66.5
```

## 2. .env.example 규칙

- 실제 API 키는 절대 포함하지 않습니다.
- 독자가 어떤 값을 넣어야 하는지 주석으로 안내합니다.

```env
# OpenAI API 키 (https://platform.openai.com/api-keys 에서 발급)
OPENAI_API_KEY=your-api-key-here

# Ollama 서버 주소 (기본값 사용 시 변경 불필요)
OLLAMA_HOST=http://localhost:11434
```

## 3. 실습 환경 구성 원칙

1. **의존성 최소화**: `pip install -r requirements.txt` 한 번으로 시작할 수 있게 합니다.
2. **데이터 포함**: 실습에 필요한 데이터(PDF, 이미지 등)는 저장소에 미리 포함시킵니다.
3. **결과물 검증**: 각 단계마다 '예상 실행 결과'를 텍스트나 스크린샷으로 제시합니다.
