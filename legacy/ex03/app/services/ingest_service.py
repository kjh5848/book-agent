import os
import glob
import subprocess
from typing import List, Dict

class IngestService:
    def __init__(self):
        self.docs_dir = "docs"
        self.md_dir = "data/markdown_docs"
        print(f"[IngestService] 초기화 완료 (문서 경로: {self.docs_dir})")

    def get_categorized_status(self) -> Dict[str, List[Dict]]:
        """카테고리별(폴더별) 문서 상태 확인"""
        categories = ["hr", "security", "ops", "guide", "general"]
        result = {cat: [] for cat in categories}
        
        # 스캔할 루트 디렉토리들
        scan_roots = ["docs", "data/docs"]
        
        for root in scan_roots:
            if not os.path.exists(root): continue
            
            # 각 카테고리 폴더 스캔
            for cat in categories:
                cat_path = os.path.join(root, cat)
                if not os.path.exists(cat_path): continue
                
                # 지원하는 파일 확장자들
                patterns = ["*.pdf", "*.docx", "*.xlsx", "*.md"]
                doc_files = []
                for p in patterns:
                    doc_files.extend(glob.glob(os.path.join(cat_path, p)))
                
                for f in doc_files:
                    base_name = os.path.basename(f)
                    md_name = f"{os.path.splitext(base_name)[0]}.md"
                    md_path = os.path.join(self.md_dir, md_name)
                    
                    is_converted = os.path.exists(md_path)
                    is_embedded = os.path.exists("data/embedding_db") if is_converted else False
                    
                    # 파일 정보 구성
                    file_info = {
                        "name": base_name,
                        "path": f,
                        "md_path": md_path if is_converted else None,
                        "status": "Vector 완료" if is_embedded else ("MD 완료" if is_converted else "Raw"),
                        "can_convert": not is_converted and not f.endswith('.md'),
                        "can_embed": is_converted and not is_embedded
                    }
                    
                    # 중복 방지 (이미 다른 루트에서 찾은 경우)
                    if not any(item['name'] == base_name for item in result[cat]):
                        result[cat].append(file_info)
        
        # 루트에 직접 있는 파일들은 'general'로 분류 (위 로직에서 폴더별로 이미 했으므로 추가 처리 필요 시)
        return result

    def save_uploaded_file(self, file_content: bytes, filename: str, category: str):
        """업로드된 파일을 카테고리 폴더에 저장"""
        target_dir = os.path.join(self.docs_dir, category)
        os.makedirs(target_dir, exist_ok=True)
        
        file_path = os.path.join(target_dir, filename)
        with open(file_path, "wb") as f:
            f.write(file_content)
        return file_path

    def run_convert(self, filename: str = None):
        """파일 변환 수행 (ingest.py 호출)"""
        cmd = ["./venv/bin/python", "ingest.py", "--mode", "convert"]
        if filename:
            cmd.extend(["--file", filename])
        
        try:
            subprocess.run(cmd, check=True)
            return True
        except Exception as e:
            print(f"[IngestService] 변환 오류: {e}")
            return False

    def run_embed(self):
        """임베딩 수행 (ingest.py 호출)"""
        try:
            subprocess.run(["./venv/bin/python", "ingest.py", "--mode", "embed"], check=True)
            return True
        except Exception as e:
            print(f"[IngestService] 임베딩 오류: {e}")
            return False

# 싱글톤 인스턴스
ingest_service = IngestService()
