"""메타데이터 관리 모듈.

문서별 메타데이터를 추출하고 JSON 파일로 저장/로드합니다.
ChromaDB 필터링에 활용할 수 있는 구조화된 메타데이터를 생성합니다.
"""

import json
import os
import sys
import re
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 메타데이터 저장 디렉토리 환경 변수
METADATA_OUTPUT_DIR = os.getenv("METADATA_OUTPUT_DIR", "outputs/metadata")

# 문서 유형 자동 감지 키워드 매핑
DOC_TYPE_KEYWORDS: dict[str, list[str]] = {
    "hr_policy": ["인사", "채용", "퇴직", "평가", "복리후생", "출퇴근"],
    "leave": ["휴가", "연차", "병가", "육아", "경조사"],
    "it_guide": ["VPN", "보안", "비밀번호", "슬랙", "노션", "깃", "장비"],
    "finance": ["예산", "지출", "매출", "비용", "세금"],
    "operations": ["운영", "프로세스", "절차", "가이드라인"],
}

# 태그 추출 키워드 (문서 내 등장 시 태그로 추가)
TAG_KEYWORDS: list[str] = [
    "Python", "API", "SQL", "Docker", "RAG", "LLM",
    "HR", "IT", "재택근무", "보안", "교육", "채용",
    "연차", "휴가", "평가", "온보딩",
]


def detect_doc_type(text: str, file_name: str) -> str:
    """파일명과 내용 키워드를 기반으로 문서 유형을 자동 감지합니다.

    Args:
        text: 문서 본문 텍스트
        file_name: 파일명 (확장자 포함)

    Returns:
        감지된 문서 유형 문자열. 감지 실패 시 "general" 반환.
    """

    # --- Input ---
    file_stem = Path(file_name).stem.lower()
    combined = (file_stem + " " + text[:1000]).lower()  # 앞 1000자만 검사

    # --- Process ---
    best_type = "general"
    best_score = 0

    for doc_type, keywords in DOC_TYPE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in combined)
        if score > best_score:
            best_score = score
            best_type = doc_type

    # --- Output ---
    return best_type


def extract_tags(text: str) -> list[str]:
    """문서 내 등장하는 태그 키워드를 추출합니다.

    Args:
        text: 문서 본문 텍스트

    Returns:
        등장한 태그 키워드 리스트 (중복 제거, 알파벳순 정렬)
    """

    # --- Input ---
    found_tags: set[str] = set()

    # --- Process ---
    for keyword in TAG_KEYWORDS:
        # 대소문자 무시하여 검색
        if re.search(re.escape(keyword), text, re.IGNORECASE):
            found_tags.add(keyword)

    # --- Output ---
    return sorted(list(found_tags))


def extract_version(text: str) -> str:
    """문서 내 버전 정보를 추출합니다.

    Args:
        text: 문서 본문 텍스트

    Returns:
        버전 문자열. 예: "v2.3". 찾지 못하면 "unknown" 반환.
    """

    # --- Input / Process ---
    match = re.search(r"버전:\s*(v[\d.]+)", text)
    if match:
        return match.group(1)

    match = re.search(r"v(\d+\.\d+)", text)
    if match:
        return f"v{match.group(1)}"

    # --- Output ---
    return "unknown"


def build_metadata(
    file_path: str,
    text: str,
    normalized_path: str = "",
) -> dict:
    """문서 파일로부터 전체 메타데이터 딕셔너리를 생성합니다.

    Args:
        file_path: 원본 파일의 절대 경로
        text: 문서 본문 텍스트
        normalized_path: 정규화된 Markdown 파일 경로 (없으면 빈 문자열)

    Returns:
        아래 키를 포함하는 메타데이터 딕셔너리:
        - file_name: 원본 파일명
        - source: 원본 파일 절대 경로
        - normalized_path: 정규화 파일 경로
        - created_at: 메타데이터 생성 시각 (ISO 8601)
        - modified_at: 파일 최종 수정 시각 (ISO 8601)
        - size_bytes: 파일 크기 (바이트)
        - doc_type: 문서 유형
        - version: 문서 버전
        - tags: 태그 리스트
        - char_count: 문자 수
    """

    # --- Input ---
    path = Path(file_path)

    if not path.exists():
        print(f"오류: 파일을 찾을 수 없습니다 - {file_path}")
        sys.exit(1)

    stat = path.stat()

    # --- Process ---
    doc_type = detect_doc_type(text, path.name)
    tags = extract_tags(text)
    version = extract_version(text)

    metadata = {
        "file_name": path.name,
        "source": str(path.absolute()),
        "normalized_path": normalized_path,
        "created_at": datetime.now().isoformat(),
        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "size_bytes": stat.st_size,
        "doc_type": doc_type,
        "version": version,
        "tags": tags,
        "char_count": len(text),
    }

    # --- Output ---
    return metadata


def save_metadata(metadata: dict, output_dir: str) -> str:
    """메타데이터 딕셔너리를 JSON 파일로 저장합니다.

    저장 경로: {output_dir}/{file_name}.metadata.json

    Args:
        metadata: build_metadata() 반환값과 동일한 형식의 딕셔너리
        output_dir: 저장할 디렉토리 경로

    Returns:
        저장된 JSON 파일의 절대 경로
    """

    # --- Input ---
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    file_stem = Path(metadata["file_name"]).stem
    output_file = output_path / f"{file_stem}.metadata.json"

    # --- Process ---
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"  메타데이터 저장: {output_file}")

    # --- Output ---
    return str(output_file.absolute())


def load_all_metadata(metadata_dir: str) -> list[dict]:
    """메타데이터 디렉토리에서 모든 JSON 파일을 로드합니다.

    Args:
        metadata_dir: 메타데이터 JSON 파일들이 있는 디렉토리 경로

    Returns:
        메타데이터 딕셔너리 리스트
    """

    # --- Input ---
    dir_path = Path(metadata_dir)

    if not dir_path.exists():
        print(f"오류: 메타데이터 디렉토리를 찾을 수 없습니다 - {metadata_dir}")
        return []

    # --- Process ---
    metadata_list: list[dict] = []

    for json_file in sorted(dir_path.glob("*.metadata.json")):
        with open(json_file, encoding="utf-8") as f:
            metadata = json.load(f)
        metadata_list.append(metadata)

    # --- Output ---
    return metadata_list


def print_metadata_summary(metadata_list: list[dict]) -> None:
    """메타데이터 목록의 요약 정보를 출력합니다.

    Args:
        metadata_list: 메타데이터 딕셔너리 리스트
    """

    # --- Input ---
    print("=" * 60)
    print("메타데이터 요약")
    print("=" * 60)
    print(f"총 문서 수: {len(metadata_list)}개")
    print()

    # --- Process ---
    for meta in metadata_list:
        print(f"파일명   : {meta['file_name']}")
        print(f"유형     : {meta['doc_type']}")
        print(f"버전     : {meta['version']}")
        print(f"크기     : {meta['size_bytes'] / 1024:.1f} KB ({meta['char_count']}자)")
        print(f"태그     : {', '.join(meta['tags']) if meta['tags'] else '없음'}")
        print(f"수정일   : {meta['modified_at'][:10]}")
        print("-" * 40)

    # --- Output ---
    # (화면 출력 전용 함수)


if __name__ == "__main__":
    # 독립 실행 시: sample_docs의 .txt 파일 메타데이터 생성 및 저장
    base_dir = Path(__file__).parent.parent
    sample_dir = base_dir / "data" / "sample_docs"
    output_dir = base_dir / METADATA_OUTPUT_DIR

    txt_files = list(sample_dir.glob("*.txt"))

    if not txt_files:
        print(f"오류: {sample_dir} 에서 .txt 파일을 찾을 수 없습니다.")
        sys.exit(1)

    print(f"메타데이터 생성 대상: {len(txt_files)}개 파일")
    print(f"출력 경로: {output_dir}")
    print()

    for txt_file in sorted(txt_files):
        print(f"처리 중: {txt_file.name}")
        with open(txt_file, encoding="utf-8") as f:
            text = f.read()

        metadata = build_metadata(str(txt_file), text)
        save_metadata(metadata, str(output_dir))

    print()
    all_meta = load_all_metadata(str(output_dir))
    print_metadata_summary(all_meta)
