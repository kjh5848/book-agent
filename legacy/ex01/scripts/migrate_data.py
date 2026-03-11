import os
import shutil
import glob

# 설정
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(ROOT, "scripts")
DATA_DIR = os.path.join(ROOT, "data")

PDF_DEST = os.path.join(DATA_DIR, "docs/ex_pdf")
EXCEL_DEST = os.path.join(DATA_DIR, "docs/ex_excel")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

def ensure_dirs():
    os.makedirs(PDF_DEST, exist_ok=True)
    os.makedirs(EXCEL_DEST, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    print(f"✅ Directories ensured:\n  - {PDF_DEST}\n  - {EXCEL_DEST}\n  - {PROCESSED_DIR}")

def move_files(src_pattern, dest_dir, file_type):
    files = glob.glob(os.path.join(SCRIPTS_DIR, src_pattern), recursive=True)
    count = 0 
    for f in files:
        if os.path.isdir(f): continue
        if "~$" in f: continue # Skip temp files

        filename = os.path.basename(f)
        dest_path = os.path.join(dest_dir, filename)

        try:
            shutil.move(f, dest_path)
            # print(f"Moved: {filename}")
            count += 1
        except Exception as e:
            print(f"❌ Failed to move {filename}: {e}")
    
    print(f"🚀 Moved {count} {file_type} files to {dest_dir}")

def run():
    print("🔄 Starting Data Migration...")
    ensure_dirs()
    
    # PDF
    move_files("pdf_scripts/**/*.pdf", PDF_DEST, "PDF")
    
    # Excel
    move_files("excel_scripts/**/*.xlsx", EXCEL_DEST, "Excel")
    
    print("✨ Migration Complete!")

if __name__ == "__main__":
    run()
