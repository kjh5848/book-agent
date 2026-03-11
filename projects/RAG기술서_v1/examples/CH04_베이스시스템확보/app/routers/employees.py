"""
routers/employees.py
====================
직원(employees) 관련 API 엔드포인트를 정의합니다.

엔드포인트 목록:
  GET /employees           - 직원 전체 조회
  GET /employees/{id}      - 직원 단건 조회
  GET /employees/{id}/leave-balance - 직원 잔여 연차 조회
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Employee
from app.schemas import EmployeeResponse, LeaveBalanceResponse

router = APIRouter(
    prefix="/employees",
    tags=["employees"],
)


def _get_employee_or_404(employee_id: int, db: Session) -> Employee:
    """
    직원을 조회하고 없으면 404 오류를 발생시킵니다.

    Args:
        employee_id: 조회할 직원의 고유 식별자
        db         : SQLAlchemy 데이터베이스 세션

    Returns:
        Employee: 조회된 직원 ORM 객체

    Raises:
        HTTPException(404): 해당 직원이 존재하지 않는 경우
    """
    # --- Input ---
    # employee_id를 기반으로 DB 조회 수행

    # --- Process ---
    employee: Employee | None = db.query(Employee).filter(Employee.id == employee_id).first()

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"직원을 찾을 수 없습니다. (id={employee_id})",
        )

    # --- Output ---
    return employee


@router.get("", response_model=list[EmployeeResponse], summary="직원 전체 조회")
def get_employees(
    db: Annotated[Session, Depends(get_db)],
) -> list[Employee]:
    """
    등록된 모든 직원 목록을 반환합니다.

    Args:
        db: SQLAlchemy 데이터베이스 세션 (FastAPI 의존성 주입)

    Returns:
        list[Employee]: 직원 ORM 객체 목록
    """
    # --- Input ---
    # 파라미터 없음 — 전체 직원 조회

    # --- Process ---
    employees: list[Employee] = db.query(Employee).order_by(Employee.id).all()

    # --- Output ---
    return employees


@router.get("/{employee_id}", response_model=EmployeeResponse, summary="직원 단건 조회")
def get_employee(
    employee_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Employee:
    """
    특정 직원의 상세 정보를 반환합니다.

    Args:
        employee_id: 조회할 직원의 고유 식별자 (경로 파라미터)
        db         : SQLAlchemy 데이터베이스 세션 (FastAPI 의존성 주입)

    Returns:
        Employee: 직원 ORM 객체

    Raises:
        HTTPException(404): 해당 직원이 존재하지 않는 경우
    """
    # --- Input ---
    # employee_id: URL 경로에서 추출된 직원 식별자

    # --- Process ---
    employee: Employee = _get_employee_or_404(employee_id, db)

    # --- Output ---
    return employee


@router.get(
    "/{employee_id}/leave-balance",
    response_model=LeaveBalanceResponse,
    summary="직원 잔여 연차 조회",
)
def get_leave_balance(
    employee_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> LeaveBalanceResponse:
    """
    특정 직원의 잔여 연차 일수를 반환합니다.
    잔여 연차 = 연간 부여 일수 - 사용 일수

    Args:
        employee_id: 조회할 직원의 고유 식별자 (경로 파라미터)
        db         : SQLAlchemy 데이터베이스 세션 (FastAPI 의존성 주입)

    Returns:
        LeaveBalanceResponse: 직원 이름, 연차 부여/사용/잔여 일수 포함

    Raises:
        HTTPException(404): 해당 직원이 존재하지 않는 경우
    """
    # --- Input ---
    # employee_id: URL 경로에서 추출된 직원 식별자

    # --- Process ---
    employee: Employee = _get_employee_or_404(employee_id, db)
    remaining_days: int = employee.annual_leave_days - employee.used_leave_days

    # --- Output ---
    return LeaveBalanceResponse(
        employee_id=employee.id,
        name=employee.name,
        annual_leave_days=employee.annual_leave_days,
        used_leave_days=employee.used_leave_days,
        remaining_days=remaining_days,
    )
