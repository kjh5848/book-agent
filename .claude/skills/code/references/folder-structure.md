# Standard Folder Structure

## Basic Structure
<!-- 기본 프로젝트 폴더 구조 -->

```
{project_name}/
├── README.md              ← Project description and execution instructions
├── requirements.txt       ← Python dependencies
├── .env.example           ← Environment variable template (no secrets)
├── src/                   ← Source code
│   ├── __init__.py
│   ├── main.py            ← Entry point
│   └── {module_name}.py
├── data/                  ← Practice data (PDFs, images, etc.)
├── tests/                 ← Test code
│   └── test_{module_name}.py
└── outputs/               ← Execution outputs (gitignore target)
```

## Practice Method Principles
<!-- 모든 예제 코드는 GitHub Clone 방식으로 제공하는 원칙 -->

All example code is provided via the **GitHub Clone method**.
Readers do not type or copy-paste code. Cloning with `git clone` and running immediately is the standard approach.

### Chapter Type Classification
<!-- 챕터 유형별 코드 레포 및 인프라 레포 분류 -->

| Type | Chapter Range | Code Repo | Infrastructure Repo |
|------|---------------|-----------|---------------------|
| **Infrastructure / Explanation Chapters** | Chapters 1–5 | None (or minimal) | Use `rag-infra` |
| **AI Code Chapters** | Chapters 6–10 | Independent repo per chapter | Requires `rag-infra` |

### Infrastructure Repo Structure (rag-infra)
<!-- Docker Compose로 전체 백엔드를 한 번에 구동하는 전용 레포 구조 -->

A dedicated repository that launches the entire backend with Docker Compose in one command.

```
rag-infra/
├── docker-compose.yml       ← PostgreSQL + FastAPI + pgAdmin definition
├── init/
│   └── 01_schema_and_data.sql  ← Table creation + sample data (employees/leave/sales)
├── backend/                 ← FastAPI CRUD server
│   ├── main.py
│   ├── routers/
│   └── requirements.txt
└── README.md
```

### AI Code Chapter Repo Structure
<!-- 각 AI 코드 챕터별 독립 레포 구조 -->

Each AI code chapter is an independently cloneable repository.

```
CH{number}_{title}/
├── README.md              ← Clone → .env → pip install → python run order guide
├── requirements.txt       ← Python dependencies (pinned versions)
├── .env.example           ← Environment variable template (no actual keys)
├── src/
│   ├── __init__.py
│   ├── main.py            ← Entry point
│   └── {module_name}.py
├── data/                  ← Source documents and sample data (structure is flexible)
└── outputs/               ← Execution outputs (.gitignore target)
```

### Standalone Execution Rule
<!-- 각 챕터는 선행 챕터 없이도 독립 실행 가능해야 한다는 원칙 -->

Each chapter must be runnable on its own — readers should not need to complete prior chapters first.

If a chapter logically depends on data from a prior chapter (e.g., documents indexed in CH06's ChromaDB), **include the necessary sample data directly inside the chapter's project**. The folder name and structure are up to the code-agent — what matters is that `python src/main.py` works immediately after `git clone → pip install → .env setup`, without any external dependency.

## Cleanup After Each Chapter
<!-- 각 챕터 실습 완료 후 환경 정리 규칙 -->

Each chapter's README and the chapter manuscript must include a **cleanup section** at the end.
Readers must clean up the current chapter's environment before starting the next chapter.

### Standard Cleanup Steps

```bash
# 1. Docker 컨테이너 종료 및 제거 (Docker를 사용한 경우)
docker compose down

# 2. 가상환경 비활성화 (venv를 사용한 경우)
deactivate

# 3. 이전 챕터 디렉토리에서 나가기
cd ..
```

### Rules

- Docker를 사용하지 않는 챕터는 `docker compose down`을 생략한다.
- 가상환경을 사용하지 않는 챕터는 `deactivate`를 생략한다.
- 해당 챕터에서 사용한 리소스만 정리한다. 불필요한 단계를 추가하지 않는다.

## Required Files
<!-- 반드시 포함해야 하는 파일 목록 -->

- `README.md` — Student execution guide
- `chapter_spec.md` — Writing agent specification (agent use only)
- `{dependency file}` — Language-specific, with pinned versions
- `.env.example` — Environment variable template for API keys, etc. (if applicable)
