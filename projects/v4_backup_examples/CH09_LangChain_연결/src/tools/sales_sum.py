"""
CH09 LangChain 연결 전략 — 매출 합계 조회 도구.

@tool 데코레이터를 사용하여 LangChain Agent에서 호출 가능한 도구를 정의합니다.
부서별·전체 매출 합계를 PostgreSQL 또는 모의 데이터에서 조회합니다.
"""

import os
import logging
from typing import Optional, Union

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# --- 모의 데이터 (DB 없이 테스트 가능) ---
MOCK_SALES: list[dict] = [
    {"id": 1, "dept": "영업팀", "amount": 12000000, "date": "2025-01-15", "description": "Q1 소프트웨어 판매"},
    {"id": 2, "dept": "영업팀", "amount": 8500000, "date": "2025-02-10", "description": "기업 라이선스 계약"},
    {"id": 3, "dept": "마케팅팀", "amount": 3200000, "date": "2025-01-20", "description": "광고 캠페인 수익"},
    {"id": 4, "dept": "개발팀", "amount": 5000000, "date": "2025-02-28", "description": "외주 개발 프로젝트"},
    {"id": 5, "dept": "영업팀", "amount": 9800000, "date": "2025-03-05", "description": "신규 고객 계약"},
    {"id": 6, "dept": "마케팅팀", "amount": 1500000, "date": "2025-03-12", "description": "이벤트 수익"},
]


def _query_from_db(dept: Optional[str] = None) -> Union[dict, None]:
    """PostgreSQL에서 매출 합계를 조회합니다.

    Args:
        dept: 조회할 부서명. None이면 전체 매출 합계를 반환합니다.

    Returns:
        매출 합계 딕셔너리 또는 None (연결 실패 시)
    """
    try:
        import psycopg2
        import psycopg2.extras

        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            dbname=os.getenv("POSTGRES_DB", "connect_hr"),
            user=os.getenv("POSTGRES_USER", "connect_hr"),
            password=os.getenv("POSTGRES_PASSWORD", "connect_hr_pass"),
        )
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        if dept:
            # ① 부서별 매출 합계
            cursor.execute(
                """
                SELECT dept, SUM(amount) AS total_amount, COUNT(*) AS count
                FROM sales
                WHERE dept = %s
                GROUP BY dept
                """,
                (dept,),
            )
            row = cursor.fetchone()
            cursor.execute(
                "SELECT * FROM sales WHERE dept = %s ORDER BY date DESC LIMIT 5",
                (dept,),
            )
            recent_records = [dict(r) for r in cursor.fetchall()]
        else:
            # ② 전체 매출 합계
            cursor.execute(
                "SELECT SUM(amount) AS total_amount, COUNT(*) AS count FROM sales"
            )
            row = cursor.fetchone()
            cursor.execute("SELECT * FROM sales ORDER BY date DESC LIMIT 5")
            recent_records = [dict(r) for r in cursor.fetchall()]

        conn.close()

        if not row or row["total_amount"] is None:
            return {"dept": dept or "전체", "total_amount": 0, "count": 0, "recent_records": []}

        return {
            "dept": dept or "전체",
            "total_amount": int(row["total_amount"]),
            "count": int(row["count"]),
            "recent_records": recent_records,
        }

    except Exception as exc:
        logger.warning("PostgreSQL 연결 실패, 모의 데이터 사용: %s", exc)
        return None


def _query_from_mock(dept: Optional[str] = None) -> Union[dict, str]:
    """모의 데이터에서 매출 합계를 조회합니다.

    Args:
        dept: 조회할 부서명. None이면 전체 매출 합계를 반환합니다.

    Returns:
        매출 합계 딕셔너리 또는 오류 문자열
    """
    # ① 부서 필터 적용
    target_sales = MOCK_SALES
    if dept:
        target_sales = [s for s in MOCK_SALES if dept in s["dept"]]

    if not target_sales:
        available_depts = list({s["dept"] for s in MOCK_SALES})
        return f"'{dept}' 매출 데이터가 없습니다. 조회 가능한 부서: {available_depts}"

    # ② 합계 계산
    total_amount = sum(s["amount"] for s in target_sales)

    return {
        "dept": dept or "전체",
        "total_amount": total_amount,
        "count": len(target_sales),
        "recent_records": target_sales[:5],
    }


# --- INPUT ---
@tool
def get_sales_sum(dept: Optional[str] = None) -> Union[dict, str]:
    """부서별 또는 전체 매출 합계와 실적 정보를 조회합니다.

    부서명을 지정하면 해당 부서의 매출 합계를, 지정하지 않으면
    전체 부서의 합산 매출을 반환합니다.

    Args:
        dept: 조회할 부서명 (예: "영업팀"). None이면 전체 매출 합계를 반환합니다.

    Returns:
        부서, 총 매출액, 거래 건수, 최근 거래 내역이 담긴 딕셔너리.
        데이터가 없으면 오류 메시지 문자열을 반환합니다.
    """
    # --- PROCESS ---
    logger.info("[get_sales_sum] 조회 대상 부서: %s", dept or "전체")

    # DB 조회 시도 → 실패 시 모의 데이터로 폴백
    result = _query_from_db(dept)
    if result is None:
        result = _query_from_mock(dept)

    # --- OUTPUT ---
    logger.info("[get_sales_sum] 결과: %s", result)
    return result
