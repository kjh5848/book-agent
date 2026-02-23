"""
routers/sales.py
================
매출(sales) 관련 API 엔드포인트를 정의합니다.

엔드포인트 목록:
  GET /sales          - 매출 전체 조회
  GET /sales/summary  - 부서별/분기별 매출 합계 조회
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Sale
from app.schemas import SaleResponse

router = APIRouter(
    prefix="/sales",
    tags=["sales"],
)


@router.get("/summary", summary="부서별/분기별 매출 합계 조회")
def get_sales_summary(
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    """
    부서별, 분기별 매출 합계를 반환합니다.
    응답 형식: {"결과": [{"department": "영업부", "quarter": "2024-Q4", "total_amount": 15800000.0}]}

    Args:
        db: SQLAlchemy 데이터베이스 세션 (FastAPI 의존성 주입)

    Returns:
        dict: 부서별 분기별 매출 합계 목록을 담은 딕셔너리
    """
    # --- Input ---
    # 파라미터 없음 — 전체 매출 집계 조회

    # --- Process ---
    # 부서(department) 및 분기(quarter) 기준 GROUP BY 집계 쿼리
    rows = (
        db.query(
            Sale.department,
            Sale.quarter,
            func.sum(Sale.amount).label("total_amount"),
        )
        .group_by(Sale.department, Sale.quarter)
        .order_by(Sale.department, Sale.quarter)
        .all()
    )

    # 결과를 직렬화 가능한 딕셔너리 리스트로 변환
    summary: list[dict] = [
        {
            "department": row.department,
            "quarter": row.quarter,
            "total_amount": float(row.total_amount) if row.total_amount is not None else 0.0,
        }
        for row in rows
    ]

    # --- Output ---
    return {"결과": summary}


@router.get("", response_model=list[SaleResponse], summary="매출 전체 조회")
def get_sales(
    db: Annotated[Session, Depends(get_db)],
) -> list[Sale]:
    """
    등록된 모든 매출 기록을 반환합니다.

    Args:
        db: SQLAlchemy 데이터베이스 세션 (FastAPI 의존성 주입)

    Returns:
        list[Sale]: 매출 ORM 객체 목록 (id 오름차순)
    """
    # --- Input ---
    # 파라미터 없음 — 전체 매출 기록 조회

    # --- Process ---
    sales: list[Sale] = db.query(Sale).order_by(Sale.id).all()

    # --- Output ---
    return sales
