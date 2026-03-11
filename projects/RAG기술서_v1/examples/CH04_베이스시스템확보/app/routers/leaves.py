"""
routers/leaves.py
=================
연차(leaves) 관련 API 엔드포인트를 정의합니다.

엔드포인트 목록:
  GET  /leaves              - 연차 전체 조회
  POST /leaves              - 연차 신청
  PUT  /leaves/{id}/status  - 연차 승인/반려
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Employee, Leave
from app.schemas import LeaveCreate, LeaveResponse, LeaveStatusUpdate

router = APIRouter(
    prefix="/leaves",
    tags=["leaves"],
)

VALID_STATUSES: set[str] = {"approved", "rejected", "pending"}


@router.get("", response_model=list[LeaveResponse], summary="연차 전체 조회")
def get_leaves(
    db: Annotated[Session, Depends(get_db)],
) -> list[Leave]:
    """
    등록된 모든 연차 신청 목록을 반환합니다.

    Args:
        db: SQLAlchemy 데이터베이스 세션 (FastAPI 의존성 주입)

    Returns:
        list[Leave]: 연차 ORM 객체 목록 (신청일 오름차순)
    """
    # --- Input ---
    # 파라미터 없음 — 전체 연차 신청 조회

    # --- Process ---
    leaves: list[Leave] = db.query(Leave).order_by(Leave.id).all()

    # --- Output ---
    return leaves


@router.post(
    "",
    response_model=LeaveResponse,
    status_code=status.HTTP_201_CREATED,
    summary="연차 신청",
)
def create_leave(
    leave_data: LeaveCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Leave:
    """
    새로운 연차 신청을 등록합니다.
    신청 직원이 존재하는지 확인한 후 저장합니다.
    시작일이 종료일보다 늦으면 오류를 반환합니다.

    Args:
        leave_data: 연차 신청 데이터 (LeaveCreate 스키마)
        db        : SQLAlchemy 데이터베이스 세션 (FastAPI 의존성 주입)

    Returns:
        Leave: 생성된 연차 ORM 객체

    Raises:
        HTTPException(404): 직원이 존재하지 않는 경우
        HTTPException(422): 시작일이 종료일보다 늦은 경우
    """
    # --- Input ---
    # leave_data: JSON 요청 본문에서 역직렬화된 연차 신청 데이터

    # --- Process ---
    # 1. 직원 존재 여부 확인
    employee: Employee | None = db.query(Employee).filter(
        Employee.id == leave_data.employee_id
    ).first()
    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"직원을 찾을 수 없습니다. (employee_id={leave_data.employee_id})",
        )

    # 2. 날짜 유효성 검사
    if leave_data.start_date > leave_data.end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="시작일은 종료일보다 이전이거나 같아야 합니다.",
        )

    # 3. 연차 신청 레코드 생성
    new_leave = Leave(
        employee_id=leave_data.employee_id,
        start_date=leave_data.start_date,
        end_date=leave_data.end_date,
        reason=leave_data.reason,
        status="pending",
    )
    db.add(new_leave)
    db.commit()
    db.refresh(new_leave)

    # --- Output ---
    return new_leave


@router.put(
    "/{leave_id}/status",
    response_model=LeaveResponse,
    summary="연차 승인 또는 반려",
)
def update_leave_status(
    leave_id: int,
    status_data: LeaveStatusUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> Leave:
    """
    특정 연차 신청의 처리 상태를 변경합니다.
    approved(승인) 또는 rejected(반려)로 변경할 수 있습니다.

    Args:
        leave_id   : 상태를 변경할 연차 신청의 고유 식별자 (경로 파라미터)
        status_data: 변경할 상태 값 (LeaveStatusUpdate 스키마)
        db         : SQLAlchemy 데이터베이스 세션 (FastAPI 의존성 주입)

    Returns:
        Leave: 상태가 변경된 연차 ORM 객체

    Raises:
        HTTPException(404): 해당 연차 신청이 존재하지 않는 경우
        HTTPException(422): 유효하지 않은 상태 값인 경우
    """
    # --- Input ---
    # leave_id   : URL 경로에서 추출된 연차 식별자
    # status_data: JSON 요청 본문에서 역직렬화된 상태 변경 데이터

    # --- Process ---
    # 1. 유효한 상태 값인지 확인
    if status_data.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"유효하지 않은 상태 값입니다. 허용값: {', '.join(VALID_STATUSES)}",
        )

    # 2. 연차 신청 레코드 조회
    leave: Leave | None = db.query(Leave).filter(Leave.id == leave_id).first()
    if leave is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"연차 신청을 찾을 수 없습니다. (id={leave_id})",
        )

    # 3. 상태 변경 및 저장
    leave.status = status_data.status
    db.commit()
    db.refresh(leave)

    # --- Output ---
    return leave
