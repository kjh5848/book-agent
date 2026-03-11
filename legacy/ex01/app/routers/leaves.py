from fastapi import APIRouter, Depends, HTTPException

from database import get_db, schemas, crud

router = APIRouter()


@router.get("/leaves")
def list_leaves(conn=Depends(get_db)):
    return crud.list_leaves(conn)


@router.get("/leaves/{emp_id}")
def get_leave_balance(emp_id: int, conn=Depends(get_db)):
    leave = crud.get_leave_by_employee(conn, emp_id)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave record not found")
    return leave


@router.post("/leaves/usage")
def use_leave(payload: schemas.LeaveUsage, conn=Depends(get_db)):
    updated = crud.use_leave(conn, payload.employee_id, payload.days)
    if not updated:
        raise HTTPException(status_code=404, detail="Leave record not found")
    return updated


@router.put("/leaves/{leave_id}")
def update_leave(leave_id: int, payload: schemas.LeaveUpdate, conn=Depends(get_db)):
    updated = crud.update_leave(
        conn,
        leave_id,
        employee_id=payload.employee_id,
        year=payload.year,
        total=payload.total,
        used=payload.used,
        remaining=payload.remaining,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Leave record not found")
    return updated
