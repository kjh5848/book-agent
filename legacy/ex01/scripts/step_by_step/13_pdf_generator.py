import sys
import os
from playwright.sync_api import sync_playwright

def html_to_pdf(html_path, pdf_path):
    print(f"🚀 PDF 변환 시작: {html_path}")
    
    with sync_playwright() as p:
        # 브라우저 실행 (headless)
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # 파일 경로를 절대 경로로(file://)
        abs_html_path = os.path.abspath(html_path)
        if not os.path.exists(abs_html_path):
             print(f"❌ HTML 파일이 없습니다: {abs_html_path}")
             return

        url = f"file://{abs_html_path}"
        print(f"Loading: {url}")
        page.goto(url)
        
        # 렌더링 대기
        page.wait_for_timeout(1000)
        
        # PDF 저장 (A4, 배경 포함)
        page.pdf(
            path=pdf_path, 
            format="A4", 
            print_background=True, 
            margin={"top": "2cm", "bottom": "2cm", "left": "2cm", "right": "2cm"}
        )
        browser.close()
        
        if os.path.exists(pdf_path):
            print(f"✅ PDF 생성 완료: {pdf_path}")
        else:
            print(f"❌ PDF 생성 실패.")

if __name__ == "__main__":
    # 실행 위치(CWD)에 따라 경로 보정
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # ex01
    html_file = os.path.join(base_dir, "실습용/ex01/data/docs/hr/HR_사내규정_다단.html")
    pdf_file = os.path.join(base_dir, "실습용/ex01/data/docs/hr/HR_사내규정_다단.pdf")
    
    html_to_pdf(html_file, pdf_file)
