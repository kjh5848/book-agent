"""문서 유효성 검사 모듈.

사내 문서 표준 규칙에 따라 파일명 규칙, 형식 지원 여부, 메타데이터를 검증하고
결과를 JSON 형태로 저장한다.
"""

# =============================================================================
# INPUT: data/docs/ 폴더 내 모든 문서 파일 경로
# PROCESS: 파일명 규칙 검증 → 형식 확인 → 메타데이터 추출
# OUTPUT: outputs/metadata.json, 터미널 검증 요약
# =============================================================================

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


# 지원하는 파일 확장자 목록
SUPPORTED_FORMATS: list[str] = [".pdf", ".docx", ".xlsx"]

# 파일명 표준 패턴: {부서코드}_{문서종류}_v{버전}.{확장자}
# 예) HR_취업규칙_v1.0.pdf, SEC_보안규정_v1.0.docx
FILENAME_PATTERN_WITH_VERSION = re.compile(
    r"^([A-Z]{2,5})_(.+)_v(\d+\.\d+)\.(pdf|docx|xlsx)$"
)

# 버전 없이 등록된 파일 패턴 (경고만 출력)
# 예) HR_정보보안서약서.pdf
FILENAME_PATTERN_WITHOUT_VERSION = re.compile(
    r"^([A-Z]{2,5})_(.+)\.(pdf|docx|xlsx)$"
)

# 허용 부서 코드 목록
KNOWN_DEPARTMENTS: dict[str, str] = {
    "HR": "인사",
    "SEC": "보안",
    "OPS": "운영",
    "FIN": "재무",
    "IT": "IT",
    "MKT": "마케팅",
    "GEN": "총무",
}


def check_format_support(file_path: Path) -> tuple[bool, str]:
    """파일 형식이 지원 대상인지 확인한다.

    Args:
        file_path: 검사할 파일의 경로 객체

    Returns:
        (지원여부, 메시지) 형태의 튜플
    """
    ext = file_path.suffix.lower()
    if ext in SUPPORTED_FORMATS:
        return True, f"지원 형식 ({ext.upper().lstrip('.')})"
    return False, f"지원하지 않는 형식: {ext} (지원 형식: PDF, DOCX, XLSX)"


def validate_filename(filename: str) -> dict:
    """파일명이 표준 명명 규칙을 따르는지 검증한다.

    표준 규칙: {부서코드}_{문서종류}_v{버전}.{확장자}
    버전이 없는 파일은 WARN 처리하며, 완전히 규칙을 벗어난 파일은 FAIL 처리한다.

    Args:
        filename: 검사할 파일명 (확장자 포함)

    Returns:
        status, department, doc_type, version, message 키를 포함한 딕셔너리
    """
    # ① 버전 포함 패턴 매칭 시도
    match_with_ver = FILENAME_PATTERN_WITH_VERSION.match(filename)
    if match_with_ver:
        dept_code = match_with_ver.group(1)
        doc_type = match_with_ver.group(2)
        version = match_with_ver.group(3)

        dept_name = KNOWN_DEPARTMENTS.get(dept_code, "알 수 없는 부서")
        is_known_dept = dept_code in KNOWN_DEPARTMENTS

        return {
            "status": "PASS",
            "department_code": dept_code,
            "department_name": dept_name,
            "doc_type": doc_type,
            "version": version,
            "message": "파일명 규칙 준수" if is_known_dept else f"알 수 없는 부서 코드: {dept_code}",
        }

    # ② 버전 없는 패턴 매칭 시도 (경고)
    match_without_ver = FILENAME_PATTERN_WITHOUT_VERSION.match(filename)
    if match_without_ver:
        dept_code = match_without_ver.group(1)
        doc_type = match_without_ver.group(2)
        dept_name = KNOWN_DEPARTMENTS.get(dept_code, "알 수 없는 부서")

        return {
            "status": "WARN",
            "department_code": dept_code,
            "department_name": dept_name,
            "doc_type": doc_type,
            "version": None,
            "message": f"버전 정보 누락 (권장 형식: {dept_code}_{doc_type}_v1.0.{filename.rsplit('.', 1)[-1]})",
        }

    # ③ 어떤 패턴에도 맞지 않는 경우
    return {
        "status": "FAIL",
        "department_code": None,
        "department_name": None,
        "doc_type": None,
        "version": None,
        "message": f"파일명 규칙 위반 (표준: {{부서코드}}_{{문서종류}}_v{{버전}}.{{확장자}})",
    }


def extract_metadata(file_path: Path) -> dict:
    """파일에서 기본 메타데이터를 추출한다.

    doc_id, title, department, version, date(수정일), format 항목을 반환한다.
    파일명 검증 결과를 활용하여 doc_id와 기타 속성을 구성한다.

    Args:
        file_path: 메타데이터를 추출할 파일 경로

    Returns:
        메타데이터 딕셔너리 (doc_id, title, department, version, date, format 포함)
    """
    # ① 파일명 검증 실행
    validation = validate_filename(file_path.name)

    # ② 파일 수정일 추출
    try:
        mtime = os.path.getmtime(file_path)
        file_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
    except OSError:
        file_date = "날짜 추출 실패"

    # ③ 파일 크기 추출 (바이트)
    try:
        file_size = file_path.stat().st_size
    except OSError:
        file_size = 0

    # ④ doc_id 생성: 부서코드_문서종류_버전 형태 (버전 없으면 'unversioned')
    dept_code = validation.get("department_code") or "UNKNOWN"
    doc_type = validation.get("doc_type") or file_path.stem
    version = validation.get("version") or "unversioned"
    doc_id = f"{dept_code}_{doc_type}_{version}".replace(" ", "_")

    return {
        "doc_id": doc_id,
        "filename": file_path.name,
        "title": doc_type if doc_type else file_path.stem,
        "department": validation.get("department_name") or "알 수 없음",
        "department_code": dept_code,
        "version": version,
        "date": file_date,
        "format": file_path.suffix.lower().lstrip(".").upper(),
        "file_size_bytes": file_size,
        "relative_path": str(file_path),
        "validation_status": validation["status"],
        "validation_message": validation["message"],
    }


def scan_docs_directory(docs_dir: Path) -> list[Path]:
    """docs 폴더 내 모든 문서 파일을 재귀적으로 스캔하여 반환한다.

    숨김 파일(.DS_Store 등)과 지원하지 않는 형식은 제외한다.

    Args:
        docs_dir: 스캔할 최상위 문서 폴더 경로

    Returns:
        발견된 파일 경로 목록 (정렬됨)

    Raises:
        FileNotFoundError: docs_dir 경로가 존재하지 않는 경우
    """
    if not docs_dir.exists():
        raise FileNotFoundError(
            f"문서 폴더를 찾을 수 없습니다: {docs_dir}\n"
            "data/docs/ 폴더가 올바르게 구성되어 있는지 확인하십시오."
        )

    # ① 지원 형식 파일만 수집 (재귀 스캔)
    file_paths: list[Path] = []
    for ext in SUPPORTED_FORMATS:
        file_paths.extend(docs_dir.rglob(f"*{ext}"))

    # ② 숨김 파일 및 시스템 파일 제외
    file_paths = [p for p in file_paths if not p.name.startswith(".")]

    return sorted(file_paths)


def validate_all_documents(docs_dir: Path) -> list[dict]:
    """docs 폴더 내 모든 문서의 유효성을 검사하고 메타데이터를 추출한다.

    파일별로 형식 지원 여부와 파일명 규칙을 검증하며, 결과를 리스트로 반환한다.

    Args:
        docs_dir: 검사할 문서 폴더 경로

    Returns:
        각 파일의 검증 결과와 메타데이터를 담은 딕셔너리 리스트
    """
    # INPUT: docs 폴더 스캔
    file_paths = scan_docs_directory(docs_dir)

    if not file_paths:
        print("[경고] 처리할 문서 파일이 없습니다. data/docs/ 폴더를 확인하십시오.")
        return []

    results: list[dict] = []

    print(f"\n총 {len(file_paths)}개 문서 검증 시작...\n")
    print("-" * 60)

    for file_path in file_paths:
        # ① 형식 지원 여부 확인
        is_supported, format_msg = check_format_support(file_path)

        # ② 지원하지 않는 형식은 FAIL 처리
        if not is_supported:
            result = {
                "doc_id": f"UNSUPPORTED_{file_path.stem}",
                "filename": file_path.name,
                "title": file_path.stem,
                "department": "알 수 없음",
                "department_code": "UNKNOWN",
                "version": None,
                "date": None,
                "format": file_path.suffix.lstrip(".").upper(),
                "file_size_bytes": 0,
                "relative_path": str(file_path),
                "validation_status": "FAIL",
                "validation_message": format_msg,
            }
        else:
            # ③ 메타데이터 추출 (파일명 검증 포함)
            result = extract_metadata(file_path)

        results.append(result)

        # 결과 출력
        status = result["validation_status"]
        status_icon = {"PASS": "[PASS]", "WARN": "[WARN]", "FAIL": "[FAIL]"}.get(status, "[????]")
        print(f"{status_icon} {result['filename']}")
        print(f"       부서: {result['department']} | 버전: {result['version'] or '없음'}")
        print(f"       메시지: {result['validation_message']}")
        print()

    return results


def save_metadata_json(results: list[dict], output_path: Path) -> None:
    """검증 결과 메타데이터를 JSON 파일로 저장한다.

    Args:
        results: 검증 결과 딕셔너리 리스트
        output_path: 저장할 JSON 파일 경로

    Raises:
        PermissionError: 저장 경로에 쓰기 권한이 없는 경우
        OSError: 디렉토리 생성에 실패한 경우
    """
    # ① 출력 디렉토리 생성 (없으면 자동 생성)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"[오류] 출력 폴더를 생성할 수 없습니다: {output_path.parent}")
        print(f"       원인: {e}")
        sys.exit(1)

    # ② JSON 형태로 직렬화하여 저장
    output_data = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_documents": len(results),
        "documents": results,
    }

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"메타데이터 저장 완료: {output_path}")
    except PermissionError:
        print(f"[오류] 파일 저장 권한이 없습니다: {output_path}")
        print("       outputs/ 폴더의 쓰기 권한을 확인하십시오.")
        sys.exit(1)


def print_summary(results: list[dict]) -> None:
    """전체 검증 결과 요약을 터미널에 출력한다.

    PASS / WARN / FAIL 건수와 비율을 출력하며, 문제 항목을 별도 나열한다.

    Args:
        results: 검증 결과 딕셔너리 리스트
    """
    total = len(results)
    if total == 0:
        print("검증할 문서가 없습니다.")
        return

    pass_count = sum(1 for r in results if r["validation_status"] == "PASS")
    warn_count = sum(1 for r in results if r["validation_status"] == "WARN")
    fail_count = sum(1 for r in results if r["validation_status"] == "FAIL")

    print("=" * 60)
    print("            문서 검증 결과 요약")
    print("=" * 60)
    print(f"  전체 문서:  {total}개")
    print(f"  PASS:       {pass_count}개  ({pass_count / total * 100:.1f}%)")
    print(f"  WARN:       {warn_count}개  ({warn_count / total * 100:.1f}%)")
    print(f"  FAIL:       {fail_count}개  ({fail_count / total * 100:.1f}%)")
    print("-" * 60)

    # WARN / FAIL 항목 상세 나열
    problem_items = [r for r in results if r["validation_status"] in ("WARN", "FAIL")]
    if problem_items:
        print("\n조치가 필요한 항목:")
        for item in problem_items:
            icon = "[WARN]" if item["validation_status"] == "WARN" else "[FAIL]"
            print(f"  {icon} {item['filename']}")
            print(f"         → {item['validation_message']}")
    else:
        print("\n모든 문서가 표준을 준수합니다.")

    print("=" * 60)

    # 최종 판정
    if fail_count > 0:
        print(f"\n최종 판정: FAIL ({fail_count}개 문서가 기준 미달입니다. 조치 후 재검증하십시오.)")
    elif warn_count > 0:
        print(f"\n최종 판정: WARN ({warn_count}개 문서에 경고가 있습니다. 표준 규칙 적용을 권장합니다.)")
    else:
        print("\n최종 판정: PASS (모든 문서가 CH06 VectorDB 구축에 사용 가능합니다.)")


def main() -> None:
    """문서 수집 표준화 검증 파이프라인의 진입점.

    data/docs/ 폴더를 스캔하여 모든 문서를 검증하고
    결과를 outputs/metadata.json으로 저장한다.
    """
    # ==============================
    # INPUT: 경로 설정
    # ==============================
    # 이 스크립트의 위치를 기준으로 프로젝트 루트 결정
    script_dir = Path(__file__).parent.parent
    docs_dir = script_dir / "data" / "docs"
    output_path = script_dir / "outputs" / "metadata.json"

    print("=" * 60)
    print("   CH05 문서 수집 표준화 검증 도구")
    print("=" * 60)
    print(f"문서 폴더: {docs_dir}")
    print(f"출력 경로: {output_path}")

    # ==============================
    # PROCESS: 문서 검증 실행
    # ==============================
    try:
        results = validate_all_documents(docs_dir)
    except FileNotFoundError as e:
        print(f"\n[오류] {e}")
        sys.exit(1)

    if not results:
        sys.exit(0)

    # ==============================
    # OUTPUT: 결과 저장 및 요약 출력
    # ==============================
    save_metadata_json(results, output_path)
    print()
    print_summary(results)


if __name__ == "__main__":
    main()
