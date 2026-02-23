"""
샘플 PDF 생성 스크립트.

reportlab 라이브러리를 사용하여 실습용 PDF 파일 두 개를 생성합니다.

생성 파일:
    HR_취업규칙_v1.0.pdf  — 3페이지 (취업규칙, 표 포함)
    FIN_매출현황_v1.0.pdf — 2페이지 (매출 현황, 다단 레이아웃 포함)

네이밍 규칙: {부서}_{문서명}_{버전}.pdf

실행 방법:
    python data/create_sample_pdfs.py
"""

import os
import sys
from pathlib import Path

# 이 스크립트가 있는 폴더(data/)를 기준으로 PDF 저장 경로 결정
_SCRIPT_DIR = Path(__file__).parent
_OUTPUT_DIR = _SCRIPT_DIR  # data/ 폴더에 저장


def create_hr_policy_pdf(output_path: str) -> None:
    """HR 취업규칙 샘플 PDF(3페이지)를 생성합니다.

    페이지 구성:
        1페이지: 제목 + 제1조(연차규정)
        2페이지: 제2조(보안USB정책) + 실습용 표
        3페이지: 제3조(복리후생)

    Args:
        output_path: 생성할 PDF 파일의 절대 경로.

    Returns:
        None. 지정된 경로에 PDF 파일을 저장합니다.

    Raises:
        RuntimeError: reportlab 미설치 시.
        IOError: 파일 저장에 실패했을 때.
    """
    # --- Input ---
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
            PageBreak,
        )
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
    except ImportError:
        raise RuntimeError(
            "reportlab이 설치되지 않았습니다. 'pip install reportlab'을 실행하십시오."
        )

    # 한글 폰트 등록 시도 (macOS/Linux 기본 경로)
    _register_korean_font()

    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    )

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = _get_styles()
    story = []

    # ------------------------------------------------------------------ #
    # 1페이지: 제목 + 제1조(연차규정)
    # ------------------------------------------------------------------ #
    story.append(Paragraph("테크컴퍼니 취업규칙", styles["title"]))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph("제정일: 2024년 1월 1일  |  버전: v1.0", styles["subtitle"]))
    story.append(Spacer(1, 12 * mm))

    story.append(Paragraph("제1조 (연차 유급 휴가 규정)", styles["heading"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        "① 신입 사원은 입사 후 만 3년간 별도 연차 휴가가 발생하지 않습니다.",
        styles["body"]
    ))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        "② 신입 사원은 매월 1회 '리프레시 데이'를 사용할 수 있습니다. "
        "리프레시 데이는 사전 팀장 승인 후 사용 가능하며, "
        "미사용 시 다음 달로 이월되지 않습니다.",
        styles["body"]
    ))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        "③ 만 3년 경과 후에는 근로기준법 제60조에 따라 연차 휴가가 부여됩니다.",
        styles["body"]
    ))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        "④ 연차 휴가는 발생일로부터 1년 이내에 사용하여야 하며, "
        "미사용 연차에 대해서는 회사 정책에 따라 처리합니다.",
        styles["body"]
    ))

    story.append(PageBreak())

    # ------------------------------------------------------------------ #
    # 2페이지: 제2조(보안USB정책) + 실습용 표
    # ------------------------------------------------------------------ #
    story.append(Paragraph("제2조 (보안 USB 관리 정책)", styles["heading"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        "① 업무 데이터의 외부 반출은 IT 팀에서 발급한 암호화 보안 USB만 허용됩니다.",
        styles["body"]
    ))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        "② 보안 USB는 개인 관리 책임 하에 있으며, 분실 시 즉시 IT 팀에 신고하여야 합니다. "
        "신고 지연 시 징계 처분을 받을 수 있습니다.",
        styles["body"]
    ))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        "③ 보안 USB에는 업무 목적 이외의 개인 파일을 저장하는 것을 금지합니다.",
        styles["body"]
    ))
    story.append(Spacer(1, 6 * mm))

    # 실습용 표: 항목/내용/비고 3열
    story.append(Paragraph("[보안 USB 정책 요약표]", styles["table_title"]))
    story.append(Spacer(1, 3 * mm))

    table_data = [
        ["항목", "내용", "비고"],
        ["발급 주체", "IT 보안팀", "연 1회 재발급"],
        ["허용 용량", "최대 32GB", "업무용 한정"],
        ["암호화 방식", "AES-256", "필수 적용"],
        ["분실 신고 시한", "24시간 이내", "지연 시 징계"],
        ["사용 기간", "발급일로부터 1년", "만료 시 반납"],
    ]

    table = Table(
        table_data,
        colWidths=[45 * mm, 75 * mm, 45 * mm],
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B4590")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), _get_font_name()),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(table)

    story.append(PageBreak())

    # ------------------------------------------------------------------ #
    # 3페이지: 제3조(복리후생)
    # ------------------------------------------------------------------ #
    story.append(Paragraph("제3조 (복리 후생 제도)", styles["heading"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        "① 식대 지원: 전 직원에게 법인카드를 지급하며, 점심·저녁 식비를 무제한으로 지원합니다. "
        "단, 1인당 1식 기준 5만 원을 초과하는 경우 팀장 사전 승인이 필요합니다.",
        styles["body"]
    ))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        "② 교육비 지원: 업무 관련 교육 및 자격증 취득 비용을 연 200만 원 한도 내에서 지원합니다. "
        "지원 대상 교육은 HR 팀의 사전 승인을 받아야 합니다.",
        styles["body"]
    ))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        "③ 건강검진: 전 직원은 연 1회 종합 건강검진을 회사 비용으로 실시합니다. "
        "30세 이상 직원은 추가 정밀 검진 항목을 선택할 수 있습니다.",
        styles["body"]
    ))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        "④ 경조사 지원: 결혼, 출산, 부모 상(喪) 등 주요 경조사에 대해 회사 규정에 따라 "
        "경조금 및 경조 휴가를 지원합니다.",
        styles["body"]
    ))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        "⑤ 사내 동호회: 취미 활동 지원을 위해 사내 동호회 운영비를 분기별로 지원합니다.",
        styles["body"]
    ))

    # --- Process ---
    doc.build(story)

    # --- Output ---


def create_fin_revenue_pdf(output_path: str) -> None:
    """FIN 매출현황 샘플 PDF(2페이지)를 생성합니다.

    페이지 구성:
        1페이지: 제목 + 결재란 + 2단 레이아웃(요약/부서별 매출표)
        2페이지: 분기별 매출 표(Q1~Q4, 마케팅/개발/영업)

    Args:
        output_path: 생성할 PDF 파일의 절대 경로.

    Returns:
        None. 지정된 경로에 PDF 파일을 저장합니다.

    Raises:
        RuntimeError: reportlab 미설치 시.
        IOError: 파일 저장에 실패했을 때.
    """
    # --- Input ---
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
            PageBreak,
        )
    except ImportError:
        raise RuntimeError(
            "reportlab이 설치되지 않았습니다. 'pip install reportlab'을 실행하십시오."
        )

    _register_korean_font()

    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    )

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = _get_styles()
    story = []

    # ------------------------------------------------------------------ #
    # 1페이지: 제목 + 결재란 + 2단 레이아웃
    # ------------------------------------------------------------------ #
    story.append(Paragraph("2024년도 매출 현황 보고서", styles["title"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("작성일: 2024년 12월 31일  |  작성 부서: 재무팀", styles["subtitle"]))
    story.append(Spacer(1, 6 * mm))

    # 결재란 (기안/검토/승인)
    story.append(Paragraph("[결재란]", styles["table_title"]))
    story.append(Spacer(1, 2 * mm))
    approval_data = [
        ["구분", "기안", "검토", "승인"],
        ["직위", "대리", "팀장", "본부장"],
        ["성명", "김재무", "이관리", "박경영"],
        ["날짜", "2024.12.31", "2025.01.02", "2025.01.03"],
        ["서명", " ", " ", " "],
    ]
    approval_table = Table(
        approval_data,
        colWidths=[30 * mm, 40 * mm, 40 * mm, 40 * mm],
    )
    approval_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), _get_font_name()),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B4590")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
        ("ROWHEIGHT", (0, 4), (-1, 4), 15 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(approval_table)
    story.append(Spacer(1, 6 * mm))

    # 2단 레이아웃: 좌(요약) + 우(부서별 매출표)
    summary_text = (
        "<b>요약</b><br/><br/>"
        "2024년도 전체 매출은 전년 대비 23% 성장하였습니다.<br/><br/>"
        "마케팅 부서: 45억 원<br/>"
        "개발 부서: 38억 원<br/>"
        "영업 부서: 62억 원<br/><br/>"
        "<b>합계: 145억 원</b>"
    )
    summary_para = Paragraph(summary_text, styles["body"])

    dept_data = [
        ["부서", "상반기(억)", "하반기(억)", "합계(억)"],
        ["마케팅", "20", "25", "45"],
        ["개발", "17", "21", "38"],
        ["영업", "28", "34", "62"],
        ["합계", "65", "80", "145"],
    ]
    dept_table = Table(
        dept_data,
        colWidths=[25 * mm, 25 * mm, 28 * mm, 25 * mm],
    )
    dept_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), _get_font_name()),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B4590")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 4), (-1, 4), colors.HexColor("#E8EAF6")),
        ("FONTNAME", (0, 4), (-1, 4), _get_font_name()),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    # 2단 레이아웃: 좌우 배치
    two_col_data = [[summary_para, dept_table]]
    two_col_table = Table(
        two_col_data,
        colWidths=[75 * mm, 95 * mm],
    )
    two_col_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 5 * mm),
        ("LEFTPADDING", (1, 0), (1, 0), 5 * mm),
        ("RIGHTPADDING", (1, 0), (1, 0), 0),
    ]))
    story.append(two_col_table)

    story.append(PageBreak())

    # ------------------------------------------------------------------ #
    # 2페이지: 분기별 매출 표 (Q1~Q4, 3개 부서)
    # ------------------------------------------------------------------ #
    story.append(Paragraph("분기별 매출 상세 현황 (단위: 억 원)", styles["heading"]))
    story.append(Spacer(1, 6 * mm))

    quarterly_data = [
        ["부서", "Q1\n(1~3월)", "Q2\n(4~6월)", "Q3\n(7~9월)", "Q4\n(10~12월)", "연간 합계"],
        ["마케팅", "8.5", "11.5", "11.0", "14.0", "45.0"],
        ["개발", "7.2", "9.8", "9.5", "11.5", "38.0"],
        ["영업", "12.0", "16.0", "15.0", "19.0", "62.0"],
        ["분기 합계", "27.7", "37.3", "35.5", "44.5", "145.0"],
    ]
    quarterly_table = Table(
        quarterly_data,
        colWidths=[28 * mm, 28 * mm, 28 * mm, 28 * mm, 28 * mm, 28 * mm],
    )
    quarterly_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), _get_font_name()),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B4590")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 4), (-1, 4), colors.HexColor("#E8EAF6")),
        ("BACKGROUND", (-1, 1), (-1, 3), colors.HexColor("#FFF3E0")),
        ("BACKGROUND", (-1, 4), (-1, 4), colors.HexColor("#BBDEFB")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("ROWBACKGROUNDS", (0, 1), (-2, 3), [colors.white, colors.HexColor("#F5F5F5")]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(quarterly_table)
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph(
        "※ 위 수치는 VAT 제외 기준입니다. 세부 내역은 별첨 자료를 참고하십시오.",
        styles["note"]
    ))

    # --- Process ---
    doc.build(story)

    # --- Output ---


def _register_korean_font() -> None:
    """시스템에 설치된 한글 폰트를 reportlab에 등록합니다.

    macOS, Linux, Windows 순서로 기본 경로를 탐색합니다.
    한글 폰트를 찾지 못하면 기본 영문 폰트를 사용합니다.

    Returns:
        None.
    """
    # --- Input ---
    font_candidates = [
        # macOS
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
        "/Library/Fonts/Arial Unicode MS.ttf",
        # Linux
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJKkr-Regular.otf",
        # Windows
        "C:/Windows/Fonts/malgun.ttf",
        "C:/Windows/Fonts/gulim.ttc",
    ]

    # --- Process ---
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        for font_path in font_candidates:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont("KoreanFont", font_path))
                    return
                except Exception:
                    continue
    except ImportError:
        pass

    # --- Output ---
    # 폰트 등록 실패 시 기본 폰트 사용 (영문만 표시)


def _get_font_name() -> str:
    """등록된 한글 폰트 이름을 반환합니다.

    한글 폰트가 등록되어 있으면 'KoreanFont', 없으면 'Helvetica'를 반환합니다.

    Returns:
        사용 가능한 폰트 이름 문자열.
    """
    # --- Input / Process ---
    try:
        from reportlab.pdfbase import pdfmetrics
        if "KoreanFont" in pdfmetrics.getRegisteredFontNames():
            return "KoreanFont"
    except Exception:
        pass

    # --- Output ---
    return "Helvetica"


def _get_styles() -> dict:
    """reportlab 단락 스타일 딕셔너리를 반환합니다.

    제목, 부제목, 헤딩, 본문, 표 제목, 주석 스타일을 정의합니다.

    Returns:
        스타일 이름을 키로 하는 ParagraphStyle 딕셔너리.
    """
    # --- Input ---
    try:
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    except ImportError:
        raise RuntimeError(
            "reportlab이 설치되지 않았습니다. 'pip install reportlab'을 실행하십시오."
        )

    font_name = _get_font_name()

    # --- Process ---
    styles = {
        "title": ParagraphStyle(
            name="Title",
            fontName=font_name,
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=4,
            textColor=colors.HexColor("#1A237E"),
        ),
        "subtitle": ParagraphStyle(
            name="Subtitle",
            fontName=font_name,
            fontSize=10,
            leading=14,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#555555"),
        ),
        "heading": ParagraphStyle(
            name="Heading",
            fontName=font_name,
            fontSize=13,
            leading=18,
            spaceBefore=6,
            spaceAfter=3,
            textColor=colors.HexColor("#2B4590"),
            borderPad=4,
        ),
        "body": ParagraphStyle(
            name="Body",
            fontName=font_name,
            fontSize=10,
            leading=16,
            alignment=TA_LEFT,
            spaceAfter=2,
        ),
        "table_title": ParagraphStyle(
            name="TableTitle",
            fontName=font_name,
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#444444"),
            spaceBefore=2,
            spaceAfter=2,
        ),
        "note": ParagraphStyle(
            name="Note",
            fontName=font_name,
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#666666"),
        ),
    }

    # --- Output ---
    return styles


def main() -> None:
    """샘플 PDF 두 개를 생성하는 메인 함수.

    HR_취업규칙_v1.0.pdf와 FIN_매출현황_v1.0.pdf를
    이 스크립트와 같은 폴더(data/)에 저장합니다.
    네이밍 규칙 {부서}_{문서명}_{버전}.pdf 적용 여부를 확인 출력합니다.

    Returns:
        None.
    """
    # --- Input ---
    pdf_specs = [
        {
            "filename": "HR_취업규칙_v1.0.pdf",
            "creator": create_hr_policy_pdf,
            "description": "취업규칙 (3페이지, 표 포함)",
        },
        {
            "filename": "FIN_매출현황_v1.0.pdf",
            "creator": create_fin_revenue_pdf,
            "description": "매출현황 (2페이지, 결재란+2단 레이아웃)",
        },
    ]

    # --- Process ---
    print("=" * 60)
    print("  샘플 PDF 생성 시작")
    print("=" * 60)
    print(f"  저장 경로: {_OUTPUT_DIR}")
    print()

    # 네이밍 규칙 검증 출력
    print("[네이밍 규칙 확인] {부서}_{문서명}_{버전}.pdf")
    for spec in pdf_specs:
        parts = spec["filename"].replace(".pdf", "").split("_")
        dept = parts[0] if len(parts) >= 1 else "?"
        doc_name = parts[1] if len(parts) >= 2 else "?"
        version = parts[2] if len(parts) >= 3 else "?"
        print(f"  {spec['filename']}")
        print(f"    부서: {dept} | 문서명: {doc_name} | 버전: {version}")
    print()

    for spec in pdf_specs:
        output_path = str(_OUTPUT_DIR / spec["filename"])
        print(f"생성 중: {spec['filename']} ({spec['description']})...")
        try:
            spec["creator"](output_path)
            file_size = os.path.getsize(output_path)
            print(f"  완료: {output_path} ({file_size:,} bytes)")
        except Exception as e:
            print(f"  오류: {e}", file=sys.stderr)
            sys.exit(1)

    # --- Output ---
    print()
    print("=" * 60)
    print(f"  생성 완료: {len(pdf_specs)}개 PDF")
    print("  다음 단계: python src/main.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
