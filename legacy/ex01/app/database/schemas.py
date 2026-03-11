from pydantic import BaseModel
from typing import Optional

class EmployeeBase(BaseModel):
    name: str
    dept: str
    email: str
    hire_date: str

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    dept: Optional[str] = None
    email: Optional[str] = None
    hire_date: Optional[str] = None

class LeaveUsage(BaseModel):
    employee_id: int
    days: float

class LeaveUpdate(BaseModel):
    id: Optional[int] = None
    employee_id: int
    year: int
    total: float
    used: float
    remaining: float

class SalesCreate(BaseModel):
    dept: str
    amount: int
    date: str
    description: Optional[str] = None
