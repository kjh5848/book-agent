#!/usr/bin/env python3
"""챕터 예제 프로젝트 표준 폴더 구조를 자동 생성합니다.

Usage:
    python scaffold_project.py CH06_vector-db ./examples
    python scaffold_project.py CH07_qa-engine .
"""

import argparse
import os
import sys


FOLDER_STRUCTURE = {
    "src": ["__init__.py", "main.py"],
    "data": [],
    "outputs": [],
}

ENV_EXAMPLE = """\
# Ollama 서버 주소 (기본값 사용 시 변경 불필요)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=deepseek-r1

# 인프라 레포 PostgreSQL 연결 정보
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sampledb
DB_USER=admin
DB_PASSWORD=password
"""

REQUIREMENTS = """\
# Core — 버전은 프로젝트에 맞게 고정할 것
langchain>=0.3.0
chromadb>=0.5.0
ollama>=0.3.0

# Utilities
python-dotenv>=1.0.0
"""

MAIN_PY = '''\
"""
{chapter_name} — 메인 실행 파일

실행:
    python src/main.py
"""

from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    """메인 진입점."""
    print("챕터 예제 실행 시작...")
    # TODO: 챕터 핵심 로직 구현


if __name__ == "__main__":
    main()
'''

README = """\
# {chapter_name}

> {book_title} — {chapter_num}장 실습 코드

## 목적 및 학습 목표

- TODO: 학습 목표 1
- TODO: 학습 목표 2

## 실행 환경

- Python 3.11+
- Docker (인프라 구동용)
- Ollama + DeepSeek R1

## 사전 준비 — 인프라 구동 (최초 1회)

```bash
git clone https://github.com/{{repo}}/rag-infra
cd rag-infra
docker-compose up -d
```

## 설치 및 실행

```bash
git clone https://github.com/{{repo}}/{chapter_name}
cd {chapter_name}
cp .env.example .env
# .env 파일에 필요한 값을 입력합니다.
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
venv\\Scripts\\activate
pip install -r requirements.txt
```

## 실행

```bash
python src/main.py
```

## 예상 결과

<!-- [캡처 사진 삽입 위치: 터미널 성공 실행 전체 화면] -->

```
TODO: 실제 실행 결과를 여기에 100% 그대로 붙여넣으십시오.
```

> **주의**: 위 출력은 실제 실행 결과를 그대로 복사한 것입니다.
"""


def scaffold(chapter_name: str, output_dir: str, book_title: str = "기술서") -> None:
    """표준 챕터 프로젝트 구조를 생성합니다."""
    chapter_num = chapter_name.split("_")[0].replace("CH", "")
    project_path = os.path.join(output_dir, chapter_name)

    if os.path.exists(project_path):
        print(f"오류: 이미 존재합니다 — {project_path}", file=sys.stderr)
        sys.exit(1)

    # 폴더 생성
    for folder, files in FOLDER_STRUCTURE.items():
        folder_path = os.path.join(project_path, folder)
        os.makedirs(folder_path, exist_ok=True)
        for filename in files:
            filepath = os.path.join(folder_path, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                if filename == "main.py":
                    f.write(MAIN_PY.format(chapter_name=chapter_name))

    # 루트 파일 생성
    with open(os.path.join(project_path, ".env.example"), "w", encoding="utf-8") as f:
        f.write(ENV_EXAMPLE)

    with open(os.path.join(project_path, "requirements.txt"), "w", encoding="utf-8") as f:
        f.write(REQUIREMENTS)

    with open(os.path.join(project_path, "README.md"), "w", encoding="utf-8") as f:
        f.write(README.format(
            chapter_name=chapter_name,
            chapter_num=chapter_num,
            book_title=book_title,
        ))

    # outputs/.gitkeep
    with open(os.path.join(project_path, "outputs", ".gitkeep"), "w") as f:
        pass

    print(f"✓ 생성 완료: {project_path}")
    print(f"  src/__init__.py, src/main.py")
    print(f"  data/, outputs/")
    print(f"  .env.example, requirements.txt, README.md")


def main() -> None:
    parser = argparse.ArgumentParser(description="챕터 예제 프로젝트 스캐폴딩")
    parser.add_argument("chapter_name", help="예: CH06_vector-db")
    parser.add_argument("output_dir", help="생성할 상위 디렉토리 경로")
    parser.add_argument("--book-title", default="기술서", help="책 제목")
    args = parser.parse_args()

    scaffold(args.chapter_name, args.output_dir, args.book_title)


if __name__ == "__main__":
    main()
