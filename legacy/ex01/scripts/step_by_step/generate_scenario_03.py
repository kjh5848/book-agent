import sys
import os
from playwright.sync_api import sync_playwright

def convert():
    # 경로 설정
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # ex01
    html_path = os.path.join(base_dir, "data/docs/security/SEC_보안정책_노이즈.html")
    pdf_path = os.path.join(base_dir, "data/docs/security/SEC_보안정책_노이즈.pdf")
    
    print(f"🚀 PDF 변환 시작: 3. 헤더/푸터 노이즈 시나리오")
    print(f"📄 HTML 소스: {html_path}")
    
    if not os.path.exists(html_path):
        print("❌ HTML 파일을 찾을 수 없습니다.")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        page.goto(f"file://{html_path}")
        page.wait_for_timeout(1000)
        
        # 반복적인 헤더/푸터도 PDF로 그대로 출력됨 (A4 사이즈)
        page.pdf(
            path=pdf_path, 
            format="A4", 
            print_background=True
        )
        browser.close()
        
    print(f"✅ PDF 생성 완료: {pdf_path}")

if __name__ == "__main__":
    convert()
