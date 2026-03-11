# Dependency Management Rules

## 1. requirements.txt Rules
<!-- 재현성 보장을 위한 버전 고정 규칙 -->

- **Pin versions** without exception. (ensures reproducibility)
- Separate core packages from utility packages.

```txt
# Core
langchain==0.2.16
chromadb==0.5.5
ollama==0.3.1

# Utilities
python-dotenv==1.0.1
tqdm==4.66.5
```

## 2. .env.example Rules
<!-- 실제 API 키를 포함하지 않는 환경 변수 템플릿 규칙 -->

- Never include actual API keys.
- Use comments to guide readers on what values to enter.

```env
# OpenAI API key (obtain from https://platform.openai.com/api-keys)
OPENAI_API_KEY=your-api-key-here

# Ollama server address (no change needed if using the default)
OLLAMA_HOST=http://localhost:11434
```

## 3. Practice Environment Setup Principles
<!-- 실습 환경 구성 원칙 -->

1. **Minimize dependencies**: Make it possible to start with a single `pip install -r requirements.txt`.
2. **Include data**: Pre-include all data required for practice (PDFs, images, etc.) in the repository.
3. **Verify outputs**: Present "expected execution results" as text or screenshots at each step.
