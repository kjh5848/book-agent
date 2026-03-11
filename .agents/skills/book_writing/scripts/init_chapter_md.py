#!/usr/bin/env python3
"""
챕터 마크다운 보일러플레이트 생성 스크립트 (init_chapter_md.py)
에이전트가 본문을 쓸 때마다 'chapter-structure.md'의 구조를 외워서 타이핑할 필요 없이,
표준화된 서론/본론/결론 아웃라인이 잡힌 빈 마크다운 파일을 생성합니다.

사용법:
python3 scripts/init_chapter_md.py --chapter "01" --title "RAG 기초" --out "../../anti_v2_book/chapters"
"""

import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="챕터 마크다운 뼈대 생성기")
    parser.add_argument("--chapter", required=True, help="챕터 번호 (예: 01)")
    parser.add_argument("--title", required=True, help="챕터 제목 (예: RAG의 이해와 실제)")
    parser.add_argument("--out", required=True, help="저장할 디렉토리 경로 (예: anti_v2_book/chapters)")
    args = parser.parse_args()

    chap_str = args.chapter.zfill(2)
    # 띄어쓰기를 언더스코어로 변경하여 파일명 생성
    filename = f"CH{chap_str}_{args.title.replace(' ', '_')}.md"
    target_dir = args.out

    os.makedirs(target_dir, exist_ok=True)
    filepath = os.path.join(target_dir, filename)

    content = f"""# CH{chap_str}: {args.title}

## 1. 개념 설명 (Introduction)
<!-- [Gemini 이미지 프롬프트]: "이 챕터의 핵심 개념을 설명하는 직관적인 비유 다이어그램 프롬프트 작성" -->
(이곳에 챕터의 핵심 개념과 왜 이 기술이 필요한지 서술합니다.)

## 2. 실습 진행 (Core Implementation)
(실습 코드의 흐름이나 아키텍처를 Mermaid로 그립니다.)
```mermaid
graph TD
    A[Start] --> B[End]
```
(이하 실습 진행 과정 및 코드 스니펫 설명)

## 3. 요약 및 마무리 (Conclusion)
(본 챕터에서 배운 내용을 3줄 요약하고 다음 챕터로 넘어가는 빌드업을 작성합니다.)
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ 성공적으로 챕터 마크다운 파일이 생성되었습니다: {filepath}")

if __name__ == "__main__":
    main()
