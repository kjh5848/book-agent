import os
from playwright.sync_api import sync_playwright

def convert():
    # 현재 스크립트 위치 기준: 실습용/ex01/scripts/step_by_step/
    # 프로젝트 루트: ai-llm-rag/
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "../../../../")) # 4단계 위
    
    html_path = os.path.join(project_root, "실습용/ex01/docs/HR_사내규정_다단_파괴.html")
    pdf_path = os.path.join(project_root, "실습용/ex01/data/docs/hr/HR_사내규정_다단_파괴.pdf")
    
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"file://{html_path}")
        page.wait_for_timeout(1000)
        page.pdf(path=pdf_path, format="A4", print_background=True)
        browser.close()
    print(f"✅ PDF 생성 완료: {pdf_path}")

if __name__ == "__main__":
    convert()
