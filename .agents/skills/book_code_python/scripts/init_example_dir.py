#!/usr/bin/env python3
"""
Python 예제 디렉토리 초기화 스크립트 (init_example_dir.py)
에이전트가 새로운 챕터의 실습 코드를 작성할 때마다 수동으로 
tech_plan.md, README.md, requirements.txt 등을 만드는 번거로움을 없애고
표준화된 보일러플레이트를 단번에 생성해주는 헬퍼 스크립트입니다.

사용법:
python3 scripts/init_example_dir.py --chapter "02" --name "rag_basic" --out "../../anti_v2_book/examples"
"""

import os
import argparse

def create_tech_plan(path, chapter_num, project_name):
    content = f"""# CH{chapter_num} {project_name} 기술 명세 (tech_plan.md)

## 1. 개요 및 목표
- 본 실습 예제의 교육적 목표와 해결하고자 하는 문제 상황을 작성합니다.

## 2. 실습 아키텍처 및 흐름
- Mermaid 다이어그램을 삽입하여 데이터 흐름이나 시스템 구조를 그립니다.
```mermaid
graph TD
    A[문제 발생] --> B(해결 로직)
```

## 3. 단계별 파일 명세 (Step-by-Step)
- **[주의] 에이전트는 코드 작성 시 반드시 `docs/tutorial_*.md` 문서를 세트로 같이 작성해야 합니다!**
- `step1_xxx.py` : (코드 역할) + `docs/tutorial_step1_xxx.md` (해설 가이드)
- `step2_xxx.py` : (코드 역할) + `docs/tutorial_step2_xxx.md` (해설 가이드)

## 4. 검증 및 확인 (Verification Plan)
- 터미널이나 가상환경에서 어떤 명령어로 실행해야 하는지 명시합니다.
"""
    with open(os.path.join(path, "tech_plan.md"), "w", encoding="utf-8") as f:
        f.write(content)

def create_readme(path, chapter_num, project_name):
    content = f"""# CH{chapter_num} 실습 가이드

본 디렉토리는 챕터 {chapter_num}의 `{project_name}` 실습 예제를 담고 있습니다.

## 📂 프로젝트 구조
- `docs/` : 단계별 상세 튜토리얼 가이드 (이론 및 코드 해설)
- `step1_*.py` ~ : 단계별 실행 가능한 예제 스크립트 

## 🚀 단계별 튜토리얼 (순서대로 학습하세요)
1. [1단계: 시작하기](docs/tutorial_step1_start.md) (해당 파일 링크 연결)
2. (AI가 추가 단계 작성할 것)

## ⚙️ 환경 세팅 및 실행 방법
1. 의존성 패키지를 설치합니다: `pip install -r requirements.txt`
2. 환경변수(`.env`)가 필요하다면 복사하여 세팅합니다.
3. 스크립트를 단계별로 실행합니다.
"""
    with open(os.path.join(path, "README.md"), "w", encoding="utf-8") as f:
        f.write(content)

def create_requirements(path):
    with open(os.path.join(path, "requirements.txt"), "w", encoding="utf-8") as f:
        f.write("# 실습에 필요한 패키지들을 하단에 명시하세요.\n")

def main():
    parser = argparse.ArgumentParser(description="Python 실습 예제 디렉토리 생성기")
    parser.add_argument("--chapter", required=True, help="챕터 번호 (예: 02)")
    parser.add_argument("--name", required=True, help="실습 프로젝트 영문명 (예: rag_basic)")
    parser.add_argument("--out", required=True, help="생성할 타겟 부모 폴더 경로 (예: anti_v2_book/examples)")
    args = parser.parse_args()

    # 폴더명: ch02_rag_basic 형태
    dir_name = f"ch{args.chapter.zfill(2)}_{args.name}"
    target_path = os.path.join(args.out, dir_name)

    os.makedirs(target_path, exist_ok=True)
    
    # docs 폴더 생성
    docs_path = os.path.join(target_path, "docs")
    os.makedirs(docs_path, exist_ok=True)
    
    create_tech_plan(target_path, args.chapter.zfill(2), args.name)
    create_readme(target_path, args.chapter.zfill(2), args.name)
    create_requirements(target_path)
    
    # 기본 메인/스텝 스크립트 더미 파일 생성
    with open(os.path.join(target_path, "step1_start.py"), "w", encoding="utf-8") as f:
        f.write("# 여기에 코드를 작성하세요.\n")
        
    # 기본 단계 튜토리얼 문서 생성
    tutorial_content = """# 1단계: 시작하기

### ◈ 학습 목표
1. 본 단계에서 무엇을 배우고 어떤 문제를 겪는지 서술합니다.

---

## 1) 코드: `step1_start.py`
(실제 Python 코드 블록 삽입)

---

## 2) 실제 실행 결과
(터미널 출력 로그 등 삽입)

---

## 3) 결과 분석
(무엇을 알 수 있었는지, 왜 실패했거나 성공했는지 해설)
"""
    with open(os.path.join(docs_path, "tutorial_step1_start.md"), "w", encoding="utf-8") as f:
        f.write(tutorial_content)

    print(f"✅ 성공적으로 예제 폴더가 초기화되었습니다: {target_path}")
    print("생성된 파일: tech_plan.md, README.md, requirements.txt, step1_start.py, docs/tutorial_step1_start.md")

if __name__ == "__main__":
    main()
