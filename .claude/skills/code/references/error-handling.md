# Python Error Handling Rules

## 1. Basic Principles
<!-- 예제 코드에서도 최소한의 에러 핸들링을 포함하는 원칙 -->

- Include at minimum basic error handling even in example code.
- Catch errors that readers may encounter when running the code.
- Error messages should be written in **reader-friendly Korean**.

## 2. Required Error Handling Patterns
<!-- 필수 에러 처리 패턴 -->

### External Service Connection
<!-- 외부 서비스 연결 에러 처리 -->

```python
try:
    result = client.chat(model="llama3", messages=messages)
except ConnectionError:
    print("Ollama 서버에 연결할 수 없습니다. 'ollama serve' 명령을 먼저 실행하십시오.")
    sys.exit(1)
```

### Missing Environment Variables
<!-- 환경 변수 누락 에러 처리 -->

```python
import os

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
    print(".env 파일에 API 키를 입력하십시오. (.env.example 참조)")
    sys.exit(1)
```

### File Path Error
<!-- 파일 경로 오류 처리 -->

```python
from pathlib import Path

file_path = Path(input_path)
if not file_path.exists():
    print(f"파일을 찾을 수 없습니다: {file_path}")
    print("파일 경로를 확인하십시오.")
    sys.exit(1)
```

## 3. Code Verification Checklist
<!-- 코드 검증 체크리스트 -->

- [ ] Does installation succeed with only `requirements.txt` after creating a fresh virtual environment (venv)?
- [ ] Does `main.py` run normally and match the expected output?
- [ ] Is a friendly error message displayed when a required environment variable is missing?
- [ ] Is an invalid file path handled gracefully without crashing?
- [ ] Do the code snippets in the body match the actual source code 100%?
- [ ] Have execution commands been verified on both Windows and macOS?
- [ ] Output: `verify_report.md` (modification history + final status)
