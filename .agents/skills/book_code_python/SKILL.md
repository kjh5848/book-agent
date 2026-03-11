---
name: book-code-python
description: 파이썬 기반 기술서적 예제 코딩 컨벤션, 네이밍 룰 및 아키텍처 패턴 지식. Use when: 파이썬 예제 코드를 작성, 리팩토링, 또는 에러 검증을 할 때 코딩 컨벤션 및 네이밍 규칙을 확인하기 위해 사용합니다.
---

# 파이썬(Python) 코딩 스킬 셋

이 스킬은 책의 실습 코드를 파이썬으로 작성할 때 지켜야 할 가이드라인과 자동화 스크립트를 제공합니다. 

## 실행 스크립트 (Scripts)
에이전트가 새로운 챕터의 실습 예제 디렉토리를 구축할 때 수동으로 파일들을 만들지 말고, **아래 스크립트를 즉시 실행하여 보일러플레이트를 생성하십시오.**
- `scripts/init_example_dir.py --chapter "02" --name "rag_basic" --out "anti_v2_book/examples"` -> `tech_plan.md`, `README.md`, `requirements.txt` 및 초기 `step1_start.py` 뼈대 구조를 단숨에 생성해줍니다.

## 🎯 핵심 프롬프트 규칙 (Rules)
> **[Rule: 통합 문서형 문학적 프로그래밍 (Literate Programming)]**
> 코딩 에이전트는 실습 예제를 작성할 때, 파편화된 `.py` 파일만 던져놓고 요약만 적어서는 절대 안 됩니다.
> 반드시 독자가 흐름을 따라갈 수 있는 서사형 튜토리얼 구조를 채택해야 합니다.
> 1. 순수 실행 코드 파일(`stepX_*.py`)을 작성합니다.
> 2. **이와 쌍을 이루는 해설 튜토리얼 문서(`docs/tutorial_stepX_*.md`)를 반드시 함께 작성합니다.**
> 3. 튜토리얼 문서 내부에는 "학습 목표", "실제 실행 가능한 파이썬 전체 코드 블록(` ```python `)", "예상 실행 결과 로그", "결과 상세 분석" 이 모두 담겨야 합니다.
> 4. `README.md`에 새롭게 만든 튜토리얼 문서의 링크를 인덱싱하여 연결합니다.

## 보조 참조 문서 (References)
- [naming.md](references/naming.md): 변수, 함수, 클래스 명명 규칙 및 주석 강제 규정
- [ipo-pattern.md](references/ipo-pattern.md): I(Input)-P(Process)-O(Output) 기반 코드 스니펫 모듈화 규정
