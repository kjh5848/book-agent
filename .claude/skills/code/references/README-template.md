# README 템플릿

## 학생용 README 필수 항목

```markdown
# {프로젝트명}

> {책 제목} - {챕터번호}장 실습 코드

## 목적 및 학습 목표

- {학습 목표 1}
- {학습 목표 2}

## 실행 환경

- Python 3.11+
- Docker (인프라 구동용)
- Ollama + DeepSeek R1 모델
- {챕터별 추가 도구}

## 사전 준비 — 인프라 구동 (최초 1회)

실습 전 인프라 레포를 clone하여 PostgreSQL과 CRUD 서버를 구동합니다.

```bash
git clone https://github.com/{repo}/rag-infra
cd rag-infra
docker-compose up -d
```

> PostgreSQL(샘플 데이터 포함), FastAPI CRUD 서버가 자동으로 실행됩니다.

## 설치 및 실행

이 챕터의 예제 코드 저장소를 클론합니다.

```bash
git clone https://github.com/{repo}/{챕터_레포명}
cd {챕터_레포명}
```

환경 변수를 설정합니다.

```bash
cp .env.example .env
# .env 파일을 열어 필요한 값(API 키 등)을 입력합니다.
```

### macOS

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 실행

```bash
python src/main.py
```

## 예상 결과

<!-- [캡처 사진 삽입 위치: 터미널 성공 실행 전체 화면] -->

```
{터미널 출력 전문 — 한 글자도 생략 없이 100% 그대로 삽입}
```

> **주의**: 위 출력은 실제 실행 결과를 그대로 복사한 것입니다. 독자의 터미널 출력과 한 글자씩 비교하여 디버깅하십시오.

## 전체 구조

{Mermaid 다이어그램}
```

## 작성 규칙

- **Git Clone 우선**: 독자는 코드를 직접 타이핑하거나 복사·붙여넣기하지 않습니다. `git clone` 후 실행하는 것이 기본입니다.
- **인프라 사전 준비 명시**: 인프라(DB, 백엔드)가 필요한 챕터는 반드시 "사전 준비 — 인프라 구동" 섹션을 포함합니다.
- **환경 변수 안내 필수**: `.env.example`을 복사하여 값을 입력하는 단계를 항상 명시합니다.
- **폴더 이동 서술**: 명령어(`cd`) 대신 **"~ 폴더로 이동합니다"** 와 같이 자연스러운 서술형으로 안내합니다.
- **OS별 명령어 분리**: 설치 명령어 등 OS에 따라 달라지는 경우 **macOS** 와 **Windows** 를 구분하여 제공합니다.
- **실행 순서**: clone → .env 설정 → pip install → python 실행 순서를 단계별로 명확히 구성합니다.
- **터미널 출력 전문 보존**: "예상 결과" 섹션에 요약이나 설명 없이 실제 터미널 출력 텍스트를 100% 그대로 코드블록에 삽입합니다. 생략 표현(`...`, `(이하 생략)` 등) 절대 금지.
- **캡처 위치 명시**: 스크린샷이 필요한 위치는 `<!-- [캡처 사진 삽입 위치: {구체적 설명}] -->` 형식의 HTML 주석으로 정확히 표시합니다.
