import sqlite3
from fastapi import APIRouter, Depends, HTTPException

from database import get_db, schemas, crud

router = APIRouter()


@router.get("/employees")
def list_employees(conn=Depends(get_db)):
    return crud.list_employees(conn)


@router.post("/employees")
def create_employee(payload: schemas.EmployeeCreate, conn=Depends(get_db)):
    try:
        return crud.create_employee(conn, payload.name, payload.dept, payload.email, payload.hire_date)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already exists")


@router.get("/employees/{employee_id}")
def get_employee(employee_id: int, conn=Depends(get_db)):
    employee = crud.get_employee(conn, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.put("/employees/{employee_id}")
def update_employee(employee_id: int, payload: schemas.EmployeeUpdate, conn=Depends(get_db)):
    updated = crud.update_employee(
        conn,
        employee_id,
        name=payload.name,
        dept=payload.dept,
        email=payload.email,
        hire_date=payload.hire_date,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Employee not found")
    return updated


@router.delete("/employees/{employee_id}")
def delete_employee(employee_id: int, conn=Depends(get_db)):
    ok = crud.delete_employee(conn, employee_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"deleted": True}
