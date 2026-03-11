from fastapi import APIRouter, Depends, HTTPException, Query

from database import get_db, schemas, crud

router = APIRouter()


@router.get("/sales")
def list_sales(conn=Depends(get_db)):
    return crud.list_sales(conn)


@router.post("/sales")
def create_sales(payload: schemas.SalesCreate, conn=Depends(get_db)):
    return crud.create_sale(conn, payload.dept, payload.amount, payload.date, payload.description)


@router.get("/sales/period")
def sales_by_period(start: str = Query(...), end: str = Query(...), conn=Depends(get_db)):
    return crud.get_sales_period(conn, start, end)


@router.get("/sales/dept/{dept_name}")
def sales_by_dept(dept_name: str, conn=Depends(get_db)):
    result = crud.get_sales_by_dept(conn, dept_name)
    if not result:
        raise HTTPException(status_code=404, detail="No sales for department")
    return result
