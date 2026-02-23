#!/usr/bin/env python3
"""
generate_overview.py
--------------------
plan.md + chapter_plan/*.md + example_plan/*.md 를 읽어
master_overview.md 를 자동 생성하는 스크립트.

사용법:
  python generate_overview.py <project_dir>

  project_dir: 수동/ 또는 자동/ 디렉토리 경로 (progress.json이 있는 폴더)

출력:
  <project_dir>/plan/master_overview.md
"""

import sys
import re
from pathlib import Path
from datetime import date


# ─────────────────────────────────────────────
# 헬퍼
# ─────────────────────────────────────────────

def read_file(path: Path) -> str:
    """파일 읽기. 없으면 빈 문자열 반환."""
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def extract_section(text: str, heading: str) -> str:
    """## ... heading ... 섹션 내용 추출 (다음 ## 전까지). heading은 부분 문자열로 검색."""
    idx = text.find(heading)
    if idx == -1:
        return ""
    # heading이 속한 줄의 끝 찾기
    start = text.find("\n", idx) + 1
    # 다음 ## 헤딩 찾기
    end_m = re.search(r"\n##\s", text[start:])
    end = start + end_m.start() if end_m else len(text)
    return text[start:end].strip()


def extract_h1(text: str) -> str:
    """# 제목 추출."""
    m = re.search(r"^#\s+(.+)", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def extract_frontmatter_value(text: str, key: str) -> str:
    """--- 블록에서 key: value 추출."""
    m = re.search(rf"^{key}:\s*(.+)", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def parse_chapter_spec(text: str) -> dict:
    """
    chapter_spec_CH*.md 에서 핵심 정보 파싱.
    반환: {title, sections, code_mapping, keywords, bridge_prev, bridge_next}
    """
    title = extract_h1(text)
    sections_raw = extract_section(text, "챕터 섹션 구조")
    code_raw = extract_section(text, "코드-섹션 매핑")
    keyword_raw = extract_section(text, "핵심 용어")
    bridge_raw = extract_section(text, "챕터 연결")

    # 섹션 목록 (- ## N. ... 줄만 추출)
    sections = re.findall(r"-\s+##\s+\d+\.\s+(.+)", sections_raw)

    # 코드 파일 목록 (표에서 파일 컬럼 추출)
    code_files = re.findall(r"\|\s+`([^`]+)`\s+\|", code_raw)
    code_files = [f for f in code_files if f not in ["파일", "-"]]

    # 핵심 용어 (- 용어: 로 시작하는 줄)
    keywords = re.findall(r"-\s+\*?\*?([^:()]+)\*?\*?\s*[:（(]", keyword_raw)
    keywords = [k.strip() for k in keywords[:5]]  # 최대 5개

    # 챕터 연결
    prev_line = re.search(r"이전 챕터에서 가져오는 개념:\s*(.+)", bridge_raw)
    next_line = re.search(r"다음 챕터로 넘기는 개념:\s*(.+)", bridge_raw)

    return {
        "title": title,
        "sections": sections,
        "code_files": code_files,
        "keywords": keywords,
        "bridge_prev": prev_line.group(1).strip() if prev_line else "",
        "bridge_next": next_line.group(1).strip() if next_line else "",
    }


def parse_example_spec(text: str) -> dict:
    """
    example_spec_CH*.md 에서 핵심 정보 파싱.
    반환: {project_type, main_files, run_command, dependencies}
    """
    h1 = extract_h1(text)
    proj_type_raw = extract_section(text, "프로젝트 유형")

    # 주요 파일 목록 (├── 또는 └── 뒤에 .py .yml .json .txt .md 로 끝나는 줄)
    main_files = re.findall(r"[├└]──\s+([\w./]+\.(?:py|yml|yaml|json|txt|md|sql))", text)
    main_files = [f for f in main_files if not f.startswith(".")][:8]

    # 실행 명령 (python src/main.py 등 핵심 1줄)
    run_m = re.search(r"python\s+src/\w+\.py[^\n]*", text)
    if not run_m:
        run_m = re.search(r"docker-compose\s+up[^\n]*", text)
    run_command = run_m.group(0).strip() if run_m else ""

    # requirements.txt 핵심 패키지
    deps = re.findall(r"([\w-]+)>=[\d.]+\s+#.*", text)
    if not deps:
        deps = re.findall(r"^([\w-]+)>=", text, re.MULTILINE)
    deps = deps[:6]

    return {
        "project_type": proj_type_raw.split("\n")[0].strip() if proj_type_raw else "",
        "main_files": main_files,
        "run_command": run_command,
        "dependencies": deps,
    }


# ─────────────────────────────────────────────
# 섹션 렌더러
# ─────────────────────────────────────────────

def render_header(plan_text: str) -> str:
    """상단 메타 정보."""
    title = extract_h1(plan_text)
    today = date.today().isoformat()
    return f"""# 마스터 오버뷰 — {title}

> 자동 생성: {today}
> 소스: plan.md + chapter_plan/ + example_plan/

---
"""


def render_plan_summary(plan_text: str) -> str:
    """plan.md 요약 (설계 개요 섹션)."""
    design = extract_section(plan_text, "설계 개요")

    # 총 분량, 독자 수준 추출
    pages_m = re.search(r"총\s*분량[^\d]*(\d+)\s*p", plan_text)
    reader_m = re.search(r"독자\s*수준[^\n]*\n.*?[-–]\s*(.+)", plan_text, re.DOTALL)
    stack_section = extract_section(plan_text, "환경 명세")

    lines = ["## 1. 프로젝트 개요\n"]
    if design:
        # 첫 3줄만 요약
        for line in design.split("\n")[:6]:
            if line.strip():
                lines.append(line)
    if pages_m:
        lines.append(f"\n**총 분량**: {pages_m.group(1)}p")

    lines.append("\n### 기술 스택\n")
    # 스택 표 추출 (| 줄)
    stack_table = [l for l in stack_section.split("\n") if l.strip().startswith("|")]
    lines.extend(stack_table[:12])

    return "\n".join(lines) + "\n"


def render_chapter_table(chapters: list[tuple[int, dict, dict]]) -> str:
    """챕터 요약 표."""
    lines = [
        "\n## 2. 챕터 개요 테이블\n",
        "| CH | 제목 | 유형 | 주요 파일 | 핵심 개념 |",
        "|-----|------|------|---------|---------|",
    ]
    for num, spec, example in chapters:
        title_short = spec["title"].replace(f"CH{num:02d} 집필 명세 — ", "")
        proj_type = "인프라" if example.get("project_type", "").startswith("인프라") else "AI코드"
        files = ", ".join(f"`{f}`" for f in example.get("main_files", [])[:3])
        keywords = ", ".join(spec.get("keywords", [])[:3])
        lines.append(f"| {num:02d} | {title_short} | {proj_type} | {files} | {keywords} |")
    return "\n".join(lines) + "\n"


def render_chapter_details(chapters: list[tuple[int, dict, dict]]) -> str:
    """챕터별 상세 블록."""
    blocks = ["\n## 3. 챕터별 상세\n"]
    for num, spec, example in chapters:
        title_short = spec["title"].replace(f"CH{num:02d} 집필 명세 — ", "")
        blocks.append(f"### CH{num:02d} — {title_short}\n")

        # 섹션 구조
        if spec["sections"]:
            blocks.append("**섹션 구조**")
            for i, s in enumerate(spec["sections"], 1):
                blocks.append(f"{i}. {s}")
            blocks.append("")

        # 예제 파일
        if example["main_files"]:
            files_str = " · ".join(f"`{f}`" for f in example["main_files"])
            blocks.append(f"**예제 파일**: {files_str}")

        # 실행 명령
        if example["run_command"]:
            blocks.append(f"**실행**: `{example['run_command']}`")

        # 챕터 연결
        if spec["bridge_next"]:
            blocks.append(f"**→ 다음 챕터**: {spec['bridge_next']}")

        blocks.append("")

    return "\n".join(blocks)


def render_dependency_graph(chapters: list[tuple[int, dict, dict]]) -> str:
    """Mermaid 의존성 그래프."""
    lines = [
        "\n## 4. 챕터 의존성 그래프\n",
        "```mermaid",
        "flowchart LR",
    ]
    for i in range(len(chapters) - 1):
        num_a = chapters[i][0]
        num_b = chapters[i + 1][0]
        title_a = chapters[i][1]["title"].replace(f"CH{num_a:02d} 집필 명세 — ", "")[:12]
        title_b = chapters[i + 1][1]["title"].replace(f"CH{num_b:02d} 집필 명세 — ", "")[:12]
        lines.append(f'    CH{num_a:02d}["{num_a}장 {title_a}"] --> CH{num_b:02d}["{num_b}장 {title_b}"]')
    lines.append("```")
    return "\n".join(lines) + "\n"


def render_run_guide(chapters: list[tuple[int, dict, dict]]) -> str:
    """챕터별 빠른 실행 가이드."""
    lines = ["\n## 5. 빠른 실행 가이드\n"]
    for num, spec, example in chapters:
        if not example["run_command"]:
            continue
        title_short = spec["title"].replace(f"CH{num:02d} 집필 명세 — ", "")
        deps = " · ".join(example["dependencies"][:4])
        lines.append(f"**CH{num:02d} {title_short}**")
        lines.append(f"```bash")
        lines.append(f"# 예제 위치: examples/CH{num:02d}_*/")
        lines.append(f"cp .env.example .env && pip install -r requirements.txt")
        lines.append(f"{example['run_command']}")
        lines.append(f"```")
        if deps:
            lines.append(f"주요 의존성: {deps}")
        lines.append("")
    return "\n".join(lines)


# ─────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("사용법: python generate_overview.py <project_dir>")
        print("  예: python generate_overview.py ./수동")
        sys.exit(1)

    project_dir = Path(sys.argv[1]).resolve()
    plan_dir = project_dir / "plan"
    chapter_dir = plan_dir / "chapter_plan"
    example_dir = plan_dir / "example_plan"
    output_path = plan_dir / "master_overview.md"

    # ── 입력 검증 ──
    if not plan_dir.exists():
        print(f"[오류] plan/ 폴더를 찾을 수 없습니다: {plan_dir}")
        sys.exit(1)

    print(f"[1/5] plan.md 읽는 중...")
    plan_text = read_file(plan_dir / "plan.md")
    if not plan_text:
        print("[오류] plan.md 가 비어있거나 없습니다.")
        sys.exit(1)

    # ── chapter_spec 로딩 ──
    print(f"[2/5] chapter_plan/ 읽는 중...")
    chapter_files = sorted(chapter_dir.glob("chapter_spec_CH*.md")) if chapter_dir.exists() else []

    # ── example_spec 로딩 ──
    print(f"[3/5] example_plan/ 읽는 중...")
    example_files = sorted(example_dir.glob("example_spec_CH*.md")) if example_dir.exists() else []

    # ── 챕터 번호 기준 병합 ──
    def get_ch_num(path: Path) -> int:
        m = re.search(r"CH(\d+)", path.stem)
        return int(m.group(1)) if m else 99

    chapter_map: dict[int, str] = {get_ch_num(f): read_file(f) for f in chapter_files}
    example_map: dict[int, str] = {get_ch_num(f): read_file(f) for f in example_files}

    all_nums = sorted(set(chapter_map) | set(example_map))
    chapters: list[tuple[int, dict, dict]] = []
    for num in all_nums:
        spec = parse_chapter_spec(chapter_map.get(num, ""))
        example = parse_example_spec(example_map.get(num, ""))
        chapters.append((num, spec, example))

    print(f"   → {len(chapter_map)}개 chapter_spec, {len(example_map)}개 example_spec 로딩")

    # ── 문서 조립 ──
    print(f"[4/5] master_overview.md 생성 중...")
    sections = [
        render_header(plan_text),
        render_plan_summary(plan_text),
        render_chapter_table(chapters),
        render_chapter_details(chapters),
        render_dependency_graph(chapters),
        render_run_guide(chapters),
    ]
    output = "\n".join(sections)

    # ── 저장 ──
    print(f"[5/5] 저장: {output_path}")
    output_path.write_text(output, encoding="utf-8")
    print(f"\n✓ 완료: {output_path}")
    print(f"  챕터 수: {len(chapters)}")
    print(f"  파일 크기: {len(output):,}자")


if __name__ == "__main__":
    main()
