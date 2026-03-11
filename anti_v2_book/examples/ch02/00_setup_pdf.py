import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import urllib.request

def step1_download_font():
    """안티그래비티 한국어 출력용 폰트(나눔고딕) 다운로드"""
    font_path = "NanumGothic.ttf"
    if not os.path.exists(font_path):
        print("[1] 한글 폰트를 다운로드합니다...")
        url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
        urllib.request.urlretrieve(url, font_path)
    
    pdfmetrics.registerFont(TTFont('NanumGothic', font_path))
    print("[1] 폰트 준비 완료!")

def step2_create_pdf(file_path: str):
    """가상의 사내 규정 PDF 문서 생성 (텍스트 + 표 혼합)"""
    print(f"[2] 가상의 사내 규정 PDF를 '{file_path}'에 생성합니다...")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    c = canvas.Canvas(file_path, pagesize=A4)
    c.setFont('NanumGothic', 16)
    
    # 텍스트 섹션
    c.drawString(50, 800, "안티그래비티 주식회사 - 2024년도 하계 휴가 지원금 및 규정 안내")
    c.setFont('NanumGothic', 12)
    c.drawString(50, 770, "1. 목적: 임직원의 리프레시를 위해 하계 휴가 기간 동안 지원금을 지급한다.")
    c.drawString(50, 750, "2. 대상: 2024년 6월 1일 이전 입사자 전원.")
    c.drawString(50, 710, "[표 1] 직급별 하계 휴가 및 지원금 상세 내역")
    
    # 표(Table) 그리기 (외곽선 및 텍스트)
    c.setLineWidth(1)
    # 가로 선 (행)
    y_starts = [690, 660, 630, 600, 570]
    for y in y_starts:
        c.line(50, y, 500, y)
    
    # 세로 선 (열)
    x_starts = [50, 150, 300, 500]
    for x in x_starts:
        c.line(x, 570, x, 690)
    
    # 표 데이터 인쇄
    c.setFont('NanumGothic', 11)
    data = [
        ("직급", "부여 휴가(일)", "휴가 지원금"),
        ("사원", "3", "300,000 원"),
        ("대리/과장", "5", "500,000 원"),
        ("차장 이상", "7", "800,000 원")
    ]
    
    y = 670
    for row in data:
        c.drawString(80, y, row[0])
        c.drawString(190, y, row[1])
        c.drawString(350, y, row[2])
        y -= 30

    c.setFont('NanumGothic', 10)
    c.drawString(50, 540, "* 주의사항: 위 지원금은 매년 7월 급여에 합산되어 일괄 지급됩니다.")
    c.drawString(50, 520, "* 본 규정은 2024년 12월 31일까지 유효합니다.")

    c.save()
    print(f"[2] PDF 생성 완료: {file_path}")

if __name__ == "__main__":
    print("=== [사내 지식 데이터 전처리] 가상의 PDF 사내 규정 생성기 ===")
    step1_download_font()
    step2_create_pdf("data/dummy_rules.pdf")
    print("이제 이 PDF를 바탕으로 텍스트와 표를 추출하는 실습을 진행하세요!")
