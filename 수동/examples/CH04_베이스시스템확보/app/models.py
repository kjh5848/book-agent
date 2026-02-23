"""
models.py
=========
SQLAlchemy ORM 모델 정의입니다.
employees, leaves, sales 테이블과 1:1 대응합니다.

DDL 기준 (init/01_schema_and_data.sql):
  - employees: 직원 기본 정보
  - leaves   : 연차 신청 및 승인 현황
  - sales    : 매출 실적 (분기별)
"""

import decimal
import datetime

from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Employee(Base):
    """
    직원 기본 정보 ORM 모델입니다.

    Attributes:
        id               : 직원 고유 식별자 (자동 증가)
        name             : 직원 이름
        department       : 소속 부서명
        annual_leave_days: 연간 부여 연차 일수 (기본값 15)
        used_leave_days  : 사용한 연차 일수 (기본값 0)
    """

    __tablename__ = "employees"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String(100), nullable=False)
    department: str = Column(String(100))
    annual_leave_days: int = Column(Integer, default=15)
    used_leave_days: int = Column(Integer, default=0)

    # 연관 관계
    leaves: list = relationship("Leave", back_populates="employee")
    sales: list = relationship("Sale", back_populates="employee")


class Leave(Base):
    """
    연차 신청 및 승인 현황 ORM 모델입니다.

    Attributes:
        id         : 연차 신청 고유 식별자 (자동 증가)
        employee_id: 직원 외래키 (employees.id 참조)
        start_date : 연차 시작일
        end_date   : 연차 종료일
        reason     : 신청 사유 (텍스트)
        status     : 처리 상태 (pending / approved / rejected)
    """

    __tablename__ = "leaves"

    id: int = Column(Integer, primary_key=True, index=True)
    employee_id: int = Column(Integer, ForeignKey("employees.id"))
    start_date: datetime.date = Column(Date)
    end_date: datetime.date = Column(Date)
    reason: str = Column(Text)
    status: str = Column(String(20), default="pending")

    # 연관 관계
    employee: Employee = relationship("Employee", back_populates="leaves")


class Sale(Base):
    """
    매출 실적 ORM 모델입니다.

    Attributes:
        id         : 매출 기록 고유 식별자 (자동 증가)
        employee_id: 직원 외래키 (employees.id 참조)
        department : 부서명 (조회 편의용 비정규화 컬럼)
        amount     : 매출 금액 (원, 소수점 2자리)
        sale_date  : 매출 발생일
        quarter    : 분기 표기 (예: '2024-Q1')
    """

    __tablename__ = "sales"

    id: int = Column(Integer, primary_key=True, index=True)
    employee_id: int = Column(Integer, ForeignKey("employees.id"))
    department: str = Column(String(100))
    amount: decimal.Decimal = Column(Numeric(12, 2))
    sale_date: datetime.date = Column(Date)
    quarter: str = Column(String(10))

    # 연관 관계
    employee: Employee = relationship("Employee", back_populates="sales")
