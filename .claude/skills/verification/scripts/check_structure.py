#!/usr/bin/env python3
"""챕터 예제 프로젝트의 파일 구조가 표준을 준수하는지 검증합니다.

Usage:
    python check_structure.py ./examples/CH06_vector-db
    python check_structure.py ./examples/CH06_vector-db --strict
"""

import argparse
import os
import sys


REQUIRED_FILES = [
    "README.md",
    "requirements.txt",
    ".env.example",
    "src/__init__.py",
    "src/main.py",
]

REQUIRED_DIRS = ["src", "data", "outputs"]

OPTIONAL_FILES = ["src/chapter_spec.md"]


def check_structure(project_path: str, strict: bool = False) -> tuple[bool, list[str]]:
    """프로젝트 구조를 검증합니다.

    Returns:
        (통과 여부, 실패 항목 목록)
    """
    issues = []

    if not os.path.isdir(project_path):
        return False, [f"경로가 존재하지 않습니다: {project_path}"]

    # 필수 디렉토리
    for d in REQUIRED_DIRS:
        if not os.path.isdir(os.path.join(project_path, d)):
            issues.append(f"[필수 폴더 없음] {d}/")

    # 필수 파일
    for f in REQUIRED_FILES:
        if not os.path.isfile(os.path.join(project_path, f)):
            issues.append(f"[필수 파일 없음] {f}")

    # README 내용 검증
    readme_path = os.path.join(project_path, "README.md")
    if os.path.isfile(readme_path):
        with open(readme_path, encoding="utf-8") as fh:
            content = fh.read()
        if "git clone" not in content:
            issues.append("[README] git clone 안내 없음")
        if ".env.example" not in content and ".env" not in content:
            issues.append("[README] .env 설정 안내 없음")
        if "예상 결과" not in content:
            issues.append("[README] 예상 결과 섹션 없음")

    # .env.example 내용 검증
    env_path = os.path.join(project_path, ".env.example")
    if os.path.isfile(env_path):
        with open(env_path, encoding="utf-8") as fh:
            env_content = fh.read()
        # 실제 시크릿이 포함되었는지 검사
        for secret_pattern in ["sk-", "api-key=", "password=admin"]:
            if secret_pattern.lower() in env_content.lower():
                if strict:
                    issues.append(f"[보안] .env.example에 실제 시크릿 포함 가능성: {secret_pattern}")

    return len(issues) == 0, issues


def main() -> None:
    parser = argparse.ArgumentParser(description="챕터 프로젝트 구조 검증")
    parser.add_argument("project_path", help="검증할 프로젝트 경로")
    parser.add_argument("--strict", action="store_true", help="보안 검사 포함")
    args = parser.parse_args()

    passed, issues = check_structure(args.project_path, args.strict)

    project_name = os.path.basename(args.project_path.rstrip("/"))

    if passed:
        print(f"✓ PASS: {project_name}")
        sys.exit(0)
    else:
        print(f"✗ FAIL: {project_name}")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)


if __name__ == "__main__":
    main()
