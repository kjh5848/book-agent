from playwright.sync_api import sync_playwright
import os
import shutil

def generate_complex_pdf():
    # 고정된 절대 경로 사용 (가장 안전함)
    project_root = "/Users/nomadlab/Desktop/김주혁/workspace/coding-study/ai-llm-rag"
    html_file = os.path.join(project_root, "실습용/ex01/docs/html/06_complex_report.html")
    output_pdf = os.path.join(project_root, "실습용/ex01/data/docs/ex_pdf/06_case1_복합보고서.pdf")
    html_dir = os.path.dirname(html_file)
    
    # 신규 프리미엄 이미지 자산 목록
    assets = [
        ("06_premium_cover_bg_png_1771480305618.png", "/Users/nomadlab/.gemini/antigravity/brain/fe6185d0-d55a-43f9-aa30-88a416d5d349/06_premium_cover_bg_png_1771480305618.png"),
        ("06_office_collab_blur_png_1771480324763.png", "/Users/nomadlab/.gemini/antigravity/brain/fe6185d0-d55a-43f9-aa30-88a416d5d349/06_office_collab_blur_png_1771480324763.png")
    ]
    
    # 이미지 복사 (HTML과 동일 폴더로)
    if not os.path.exists(html_dir):
        os.makedirs(html_dir, exist_ok=True)
        
    for filename, source_path in assets:
        dest_path = os.path.join(html_dir, filename)
        if os.path.exists(source_path):
            shutil.copy(source_path, dest_path)
            print(f"🖼️ 자산 복사 완료: {dest_path}")
        else:
            print(f"⚠️ 자산 찾을 수 없음: {source_path}")

    print(f"🚀 [Premium] PDF 생성 시작: {html_file}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        file_url = f"file://{os.path.abspath(html_file)}"
        page.goto(file_url)
        
        # 폰트 및 이미지 로딩 대기
        page.wait_for_timeout(3000) 
        
        # PDF 저장 (A4 사이즈, 배경 포함, 여백 없음)
        page.pdf(
            path=output_pdf,
            format="A4",
            print_background=True,
            margin={
                "top": "0",
                "bottom": "0",
                "left": "0",
                "right": "0"
            }
        )
        browser.close()
        
    print(f"✅ [Premium] PDF 생성 완료: {output_pdf}")

if __name__ == "__main__":
    generate_complex_pdf()
