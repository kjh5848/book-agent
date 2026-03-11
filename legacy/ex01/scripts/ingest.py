import os
import sys
import glob
import argparse
import shutil

# 프로젝트 루트를 Python 경로에 추가하여 scripts 패키지를 인식하게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
from scripts.converter.pdf_strategy import convert_pdf_to_md
from scripts.converter.docx_strategy import convert_docx_to_md
from scripts.converter.xlsx_strategy import convert_xlsx_to_md
from scripts.embedding.embed_strategy import embed_md_file

# 설정
RAW_DATA_DIRS = ["data/docs"]  # 원본 데이터 폴더: data/docs만 사용
PROCESSED_DIR = "data/processed"
VECTOR_DB_DIR = "data/embedding_db"

def parse_metadata(filename):
    """
    파일명에서 메타데이터 추출
    규칙: {부서}_{제목}_v{버전}.{확장자} (예: HR_휴가규정_v1.0.pdf)
    """
    name_without_ext = os.path.splitext(filename)[0]
    # 정규표현식: (부서)_(제목)_v(버전)
    match = re.match(r"^([A-Za-z0-9가-힣]+)_([A-Za-z0-9가-힣_\s]+)_v([0-9.]+)$", name_without_ext)
    
    if match:
        dept, title, version = match.groups()
        return {
            "dept": dept,
            "title": title,
            "version": version,
            "source_filename": filename
        }
    else:
        # 규칙에 맞지 않으면 기본값 반환
        return {
            "dept": "General",
            "title": name_without_ext,
            "version": "Unknown",
            "source_filename": filename
        }

def run_ingestion(target_file=None):
    """
    데이터 감지 -> 변환 -> 임베딩 통합 파이프라인
    :param target_file: 특정 파일만 처리하고 싶을 때 파일명 또는 패턴
    """
    print("\n" + "="*50)
    print("🚀 메타코딩 AI 비서: 데이터 인제스트(Ingest) 시작")
    print("="*50)
    
    # 1. 지원하는 파일 패턴 정의
    patterns = {
        "**/*.pdf": convert_pdf_to_md,
        "**/*.docx": convert_docx_to_md,
        "**/*.xlsx": convert_xlsx_to_md,
        "**/*.md": lambda src, dst: shutil.copy(src, dst) if src != dst else None
    }
    
    # 2. 모든 파일 목록 미리 수집하여 전체 개수 파악
    all_tasks = []
    print(f"📂 스캔 대상 디렉토리: {', '.join(RAW_DATA_DIRS)}")

    for raw_dir in RAW_DATA_DIRS:
        if not os.path.exists(raw_dir):
            print(f"   ⚠️  [Warning] 디렉토리가 존재하지 않습니다: {raw_dir}")
            continue
            
        print(f"   🔎 스캔 중: {raw_dir} ...", end="")
        dir_file_count = 0
        for pattern, strategy_func in patterns.items():
            files = glob.glob(os.path.join(raw_dir, pattern), recursive=True)
            for f in files:
                # 특정 파일 필터링 반영
                if target_file and target_file not in os.path.basename(f):
                    continue
                all_tasks.append((f, strategy_func))
                dir_file_count += 1
        print(f" -> {dir_file_count}개 파일 발견")

    total_files = len(all_tasks)
    if total_files == 0:
        print("\n💡 처리할 파일을 찾지 못했습니다. docs 또는 data/docs 폴더를 확인해 주세요.")
        return

    print(f"\n📦 총 {total_files}개의 파일을 찾았습니다. 인제스트를 시작합니다...\n")
    
    success_count = 0
    fail_count = 0

    # 3. 루프 내 진행 상황 표시
    for i, (file_path, strategy_func) in enumerate(all_tasks, 1):
        file_name = os.path.basename(file_path)
        print(f"🔄 [{i}/{total_files}] 진행 중: {file_name} ...")
        
        try:
            output_name = f"{os.path.splitext(file_name)[0]}.md"
            output_path = os.path.join(PROCESSED_DIR, output_name)
            
            # 1단계: 파일을 MD로 (변환)
            strategy_func(file_path, output_path)
            
            # 2단계: MD를 임베딩으로 (임베딩)
            if os.path.exists(output_path):
                # 메타데이터 추출
                metadata = parse_metadata(file_name)
                print(f"   ℹ️  Metadata: {metadata}")
                
                embed_md_file(output_path, VECTOR_DB_DIR, metadata=metadata)
                print(f"   ✅ [완료] {file_name}")
                success_count += 1
            else:
                print(f"   ❌ [오류] 파일 변환에 실패했습니다: {file_name}")
                fail_count += 1
        except Exception as e:
            print(f"   ⚠️ [치명적 오류] {file_name} 처리 중 에러 발생: {e}")
            fail_count += 1
            continue
            
    print("\n" + "="*50)
    print(f"✨ 데이터 인제스트 완료!")
    print(f"🎯 전체: {total_files} | ✅ 성공: {success_count} | ❌ 실패: {fail_count}")
    print("="*50 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="메타코딩 AI 비서 데이터 인제스트")
    parser.add_argument("--file", "-f", help="특정 파일명 또는 패턴만 처리하고 싶을 때 사용")
    parser.add_argument("--mode", "-m", choices=["all", "convert", "embed"], default="all", help="작업 모드 설정")
    args = parser.parse_args()

    # 필요한 디렉토리 생성
    for directory in RAW_DATA_DIRS:
        os.makedirs(directory, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(VECTOR_DB_DIR, exist_ok=True)
    
    # 모드에 따른 로직 분기 (현재 run_ingestion은 통합되어 있으므로 필요 시 수정 가능)
    # 여기서는 간단히 run_ingestion을 호출하며 내부적으로 모드 제어가 안 되어 있으므로
    # run_ingestion을 모드 지원하도록 수정하거나 여기서 직접 수행합니다.
    
    if args.mode == "convert" or args.mode == "all":
        # 현재 run_ingestion이 두 작업을 동시에 수행하므로, 
        # 향후 분리를 위해 run_ingestion 내부 로직을 체크하거나 
        # 여기서는 우선 전체 실행으로 대응합니다.
        run_ingestion(target_file=args.file)
    elif args.mode == "embed":
        # 이미 변환된 MD 파일들에 대해 임베딩만 수행
        md_files = glob.glob(os.path.join(PROCESSED_DIR, "*.md"))
        for md_path in md_files:
            print(f"   [Embed Only] {os.path.basename(md_path)} ...")
            embed_md_file(md_path, VECTOR_DB_DIR)
