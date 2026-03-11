# README Template

## Required Sections for Student README
<!-- 학생용 README에 반드시 포함해야 하는 항목 -->

```markdown
# {Project Name}

> {Book Title} - Chapter {Number} Practice Code

## Purpose and Learning Objectives

- {Learning Objective 1}
- {Learning Objective 2}

## Runtime Environment

- Python 3.11+
- Docker (for infrastructure)
- Ollama + DeepSeek R1 model
- {Additional tools per chapter}

## Prerequisites — Infrastructure Setup (First Time Only)

Clone the infrastructure repository and start PostgreSQL and the CRUD server before practicing.

```bash
git clone https://github.com/{repo}/rag-infra
cd rag-infra
docker-compose up -d
```

> PostgreSQL (with sample data) and FastAPI CRUD server will start automatically.

## Installation and Execution

Clone this chapter's example code repository.

```bash
git clone https://github.com/{repo}/{chapter_repo_name}
cd {chapter_repo_name}
```

Set environment variables.

```bash
cp .env.example .env
# Open the .env file and enter the required values (API keys, etc.).
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

## Run

```bash
python src/main.py
```

## Expected Output

<!-- [CAPTURE NEEDED: full terminal screen after successful execution] -->

```
{Full terminal output — insert 100% as-is, without any omissions}
```

> **Note**: The output above is copied directly from an actual execution. Compare it character by character with your terminal output to debug.

## Overall Structure

{Mermaid diagram}
```

## Writing Rules
<!-- README 작성 규칙 -->

- **Git Clone First**: Readers do not type or copy-paste code. Cloning with `git clone` and running immediately is the standard approach.
- **Specify Infrastructure Prerequisites**: Chapters requiring infrastructure (DB, backend) must include a "Prerequisites — Infrastructure Setup" section.
- **Environment Variable Instructions Required**: Always specify the step of copying `.env.example` and entering values.
- **Describe Folder Navigation**: Guide navigation as natural prose (e.g., "Move to the ~ folder") instead of using commands (`cd`).
- **Separate OS-specific Commands**: When commands differ by OS (e.g., installation), provide separate **macOS** and **Windows** instructions.
- **Execution Order**: Clearly lay out each step in the order: clone → .env setup → pip install → python run.
- **Preserve Full Terminal Output**: Insert the actual terminal output text 100% as-is into a code block in the "Expected Output" section, without any summary or omission (absolutely no `...` or "(omitted)" expressions).
- **Specify Capture Location**: Mark where screenshots are needed using HTML comments in the format `<!-- [CAPTURE NEEDED: {specific description}] -->`.
