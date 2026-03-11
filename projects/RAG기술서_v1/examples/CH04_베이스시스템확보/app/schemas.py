"""
schemas.py
==========
Pydantic v2 요청/응답 스키마 정의입니다.
FastAPI의 직렬화와 유효성 검사에 사용됩니다.

Pydantic v2 기준: model_config = ConfigDict(from_attributes=True)를 사용하여
SQLAlchemy ORM 객체를 직접 응답 모델로 변환합니다.
"""

import datetime
import decimal

from pydantic import BaseModel, ConfigDict, Field


# =============================================================
# Employee 스키마
# =============================================================

class EmployeeResponse(BaseModel):
    """
    직원 조회 응답 스키마입니다.

    Attributes:
        id               : 직원 고유 식별자
        name             : 직원 이름
        department       : 소속 부서명
        annual_leave_days: 연간 부여 연차 일수
        used_leave_days  : 사용한 연차 일수
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    department: str | None = None
    annual_leave_days: int
    used_leave_days: int


class LeaveBalanceResponse(BaseModel):
    """
    잔여 연차 조회 응답 스키마입니다.

    Attributes:
        employee_id   : 직원 고유 식별자
        name          : 직원 이름
        annual_leave_days: 연간 부여 연차 일수
        used_leave_days  : 사용한 연차 일수
        remaining_days   : 잔여 연차 일수 (annual - used)
    """

    employee_id: int
    name: str
    annual_leave_days: int
    used_leave_days: int
    remaining_days: int


# =============================================================
# Leave 스키마
# =============================================================

class LeaveCreate(BaseModel):
    """
    연차 신청 요청 스키마입니다.

    Attributes:
        employee_id: 신청 직원의 고유 식별자
        start_date : 연차 시작일
        end_date   : 연차 종료일
        reason     : 신청 사유
    """

    employee_id: int = Field(..., description="신청 직원의 고유 식별자", gt=0)
    start_date: datetime.date = Field(..., description="연차 시작일 (YYYY-MM-DD)")
    end_date: datetime.date = Field(..., description="연차 종료일 (YYYY-MM-DD)")
    reason: str | None = Field(None, description="신청 사유")


class LeaveStatusUpdate(BaseModel):
    """
    연차 상태 변경 요청 스키마입니다.

    Attributes:
        status: 변경할 처리 상태 (approved / rejected)
    """

    status: str = Field(..., description="변경할 상태: approved 또는 rejected")


class LeaveResponse(BaseModel):
    """
    연차 조회/응답 스키마입니다.

    Attributes:
        id         : 연차 신청 고유 식별자
        employee_id: 직원 고유 식별자
        start_date : 연차 시작일
        end_date   : 연차 종료일
        reason     : 신청 사유
        status     : 처리 상태 (pending / approved / rejected)
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int | None = None
    start_date: datetime.date | None = None
    end_date: datetime.date | None = None
    reason: str | None = None
    status: str


# =============================================================
# Sale 스키마
# =============================================================

class SaleResponse(BaseModel):
    """
    매출 조회 응답 스키마입니다.

    Attributes:
        id         : 매출 기록 고유 식별자
        employee_id: 직원 고유 식별자
        department : 부서명
        amount     : 매출 금액 (원)
        sale_date  : 매출 발생일
        quarter    : 분기 (예: '2024-Q1')
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int | None = None
    department: str | None = None
    amount: decimal.Decimal | None = None
    sale_date: datetime.date | None = None
    quarter: str | None = None
