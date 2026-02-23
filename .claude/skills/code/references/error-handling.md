# Python 에러 처리 규칙

## 1. 기본 원칙

- 예제 코드에서도 최소한의 에러 핸들링을 포함합니다.
- 독자가 실행 시 만날 수 있는 에러를 미리 잡아줍니다.
- 에러 메시지는 **독자 친화적 한국어** 로 작성합니다.

## 2. 필수 에러 처리 패턴

### 외부 서비스 연결

```python
try:
    result = client.chat(model="llama3", messages=messages)
except ConnectionError:
    print("Ollama 서버에 연결할 수 없습니다. 'ollama serve' 명령을 먼저 실행하십시오.")
    sys.exit(1)
```

### 환경 변수 누락

```python
import os

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
    print(".env 파일에 API 키를 입력하십시오. (.env.example 참조)")
    sys.exit(1)
```

### 파일 경로 오류

```python
from pathlib import Path

file_path = Path(input_path)
if not file_path.exists():
    print(f"파일을 찾을 수 없습니다: {file_path}")
    print("파일 경로를 확인하십시오.")
    sys.exit(1)
```

## 3. 코드 검증 체크리스트

- [ ] 가상환경(venv) 신규 생성 후 `requirements.txt`만으로 설치 성공하는가
- [ ] `main.py` 정상 실행 및 예상 결과와 일치하는가
- [ ] 필수 환경 변수 누락 시 친절한 에러 메시지가 출력되는가
- [ ] 잘못된 파일 경로 입력 시 크래시 없이 처리되는가
- [ ] 본문 코드 스니펫과 실제 소스 코드가 100% 일치하는가
- [ ] Windows / macOS 양쪽 실행 명령어가 검증되었는가
- [ ] 산출물: `verify_report.md` (수정 내역 + 최종 상태)
