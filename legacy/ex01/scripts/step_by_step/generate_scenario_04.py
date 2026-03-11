import sys
import os
from playwright.sync_api import sync_playwright

def convert():
    # 경로 설정
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # ex01
    html_path = os.path.join(base_dir, "data/docs/security/SEC_보안규정_스캔.html")
    pdf_path = os.path.join(base_dir, "data/docs/security/SEC_보안규정_스캔.pdf")
    
    print(f"🚀 PDF 변환 시작: 4. 스캔 이미지/OCR 시나리오")
    print(f"📄 HTML 소스: {html_path}")
    
    if not os.path.exists(html_path):
        print("❌ HTML 파일을 찾을 수 없습니다.")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        page.goto(f"file://{html_path}")
        page.wait_for_timeout(1000)
        
        # CSS 필터 효과가 적용된 그대로 PDF로 캡처해야 함
        # 그러나 page.pdf()는 기본적으로 인쇄용 렌더링을 하므로 background가 중요함
        # 배경색(body)까지 포함해서 찍기 위해 print_background=True
        page.pdf(
            path=pdf_path, 
            format="A4", 
            print_background=True
        )
        browser.close()
        
    print(f"✅ PDF 생성 완료: {pdf_path}")

if __name__ == "__main__":
    convert()
