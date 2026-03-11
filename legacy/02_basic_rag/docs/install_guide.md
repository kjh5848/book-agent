# 🖥️ OS별 파이썬 RAG 환경 설치 가이드

이 문서는 사용자의 운영체제에 맞춰 파이썬 패키지를 설치하고 실행하는 방법을 안내합니다.

---

## 🍎 macOS (맥) 사용자

맥은 기본 파이썬 버전 충돌이 잦으므로, 항상 실행 중인 파이썬 경로를 확인하는 것이 좋습니다.

### 1. 패키지 설치
터미널에서 아래 명령어를 사용하세요. (`pip` 대신 `python3 -m pip` 사용 권장)
```bash
# 기본 설치 방식
python3 -m pip install langchain langchain-community langchain-chroma langchain-ollama

# 만약 Homebrew 파이썬을 사용 중이라면
/opt/homebrew/bin/python3 -m pip install langchain langchain-community langchain-chroma langchain-ollama

# 가상환경(venv)을 사용 중이라면
./.venv/bin/python -m pip install langchain langchain-community langchain-chroma langchain-ollama
```

### 2. 코드 실행
```bash
python3 파일명.py
# 또는
./.venv/bin/python 파일명.py
```

---

## 🪟 Windows (윈도우) 사용자

윈도우는 환경 변수 설정에 따라 `python` 또는 `py` 명령어를 사용합니다.

### 1. 패키지 설치
명령 프롬프트(CMD) 또는 PowerShell에서 실행하세요.
```bash
# 기본 설치 방식
python -m pip install langchain langchain-community langchain-chroma langchain-ollama

# 또는 파이썬 런처 사용 시
py -m pip install langchain langchain-community langchain-chroma langchain-ollama
```

### 2. 코드 실행
```bash
python 파일명.py
# 또는
py 파일명.py
```

---

## 💡 공통 팁: 어떤 pip를 써야 할지 모를 때

가장 확실한 방법은 **실행하려는 파이썬 경로를 직접 지정**하는 것입니다.

1. **내 파이썬 위치 확인**:
   - 맥: `which python3`
   - 윈도우: `where python`
2. **설치 공식**: `[확인된 파이썬 경로] -m pip install [라이브러리명]`
   - 예: `/Users/name/ai-llm-rag/.venv/bin/python -m pip install langchain`

---

## 🦙 Ollama 모델 설치 (공통)

터미널/명령 프롬프트에서 아래 명령어를 순서대로 실행하세요.
```bash
ollama pull deepseek-r1:8b
ollama pull nomic-embed-text
```
