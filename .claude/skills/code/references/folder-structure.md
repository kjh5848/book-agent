# 표준 폴더 구조

## 기본 구조

```
{프로젝트명}/
├── README.md              ← 프로젝트 설명 및 실행 방법
├── requirements.txt       ← Python 의존성
├── .env.example           ← 환경 변수 템플릿 (비밀키 미포함)
├── src/                   ← 소스 코드
│   ├── __init__.py
│   ├── main.py            ← 진입점
│   └── {모듈명}.py
├── data/                  ← 실습용 데이터 (PDF, 이미지 등)
├── tests/                 ← 테스트 코드
│   └── test_{모듈명}.py
└── outputs/               ← 실행 결과물 (gitignore 대상)
```

## 실습 방식 원칙

모든 예제 코드는 **GitHub Clone 방식**으로 제공한다.
독자는 코드를 타이핑하거나 복사·붙여넣기하지 않는다. `git clone` 후 즉시 실행하는 것이 기본이다.

### 챕터 유형 분류

| 유형 | 챕터 범위 | 코드 레포 | 인프라 레포 |
|------|---------|---------|-----------|
| **인프라·설명 챕터** | 1~5장 | 없음 (또는 최소) | `rag-infra` 사용 |
| **AI 코드 챕터** | 6~10장 | 챕터별 독립 레포 | `rag-infra` 전제 |

### 인프라 레포 구조 (rag-infra)

Docker Compose로 전체 백엔드를 한 번에 구동하는 전용 레포.

```
rag-infra/
├── docker-compose.yml       ← PostgreSQL + FastAPI + pgAdmin 정의
├── init/
│   └── 01_schema_and_data.sql  ← 테이블 생성 + 샘플 데이터 (직원/휴가/매출)
├── backend/                 ← FastAPI CRUD 서버
│   ├── main.py
│   ├── routers/
│   └── requirements.txt
└── README.md
```

### AI 코드 챕터 레포 구조

각 AI 코드 챕터는 독립적으로 clone 가능한 레포.

```
CH{번호}_{제목}/
├── README.md              ← clone → .env → pip install → python 실행 순서 안내
├── requirements.txt       ← Python 의존성 (버전 고정)
├── .env.example           ← 환경 변수 템플릿 (실제 키 미포함)
├── src/
│   ├── __init__.py
│   ├── main.py            ← 진입점
│   └── {모듈명}.py
├── data/                  ← 실습용 데이터 (PDF, 이미지 등)
└── outputs/               ← 실행 결과물 (.gitignore 대상)
```

## 필수 파일

- `README.md` — 학생용 실행 가이드
- `chapter_spec.md` — 집필 에이전트 전용 명세
- `{의존성 파일}` — 언어별, 버전 고정
- `.env.example` — API 키 등 환경 변수 템플릿 (해당하는 경우)
