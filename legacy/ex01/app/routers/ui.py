import os
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from database import get_db_connection, crud, DATABASE_URL

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/admin", tags=["ui"])


@router.get("/")
def admin_root():
    return RedirectResponse(url="/admin/dashboard", status_code=302)


@router.get("/dashboard")
def dashboard(request: Request):
    conn = get_db_connection()
    employees_count = crud.count_employees(conn)
    leaves_count = crud.count_leaves(conn)
    sales_count = crud.count_sales(conn)
    sales_total = crud.sum_sales(conn)
    recent_sales = crud.list_sales(conn, limit=8)
    conn.close()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "active_page": "dashboard",
            "db_path": DATABASE_URL,
            "employees_count": employees_count,
            "leaves_count": leaves_count,
            "sales_count": sales_count,
            "sales_total": sales_total,
            "recent_sales": recent_sales,
        },
    )


@router.get("/employees")
def employees_page(
    request: Request,
    name: str = "",
    dept: str = "",
):
    conn = get_db_connection()
    employees = crud.list_employees(conn)
    conn.close()

    # 필터링 로직 (Python 레벨에서 처리)
    if name:
        employees = [e for e in employees if name in e["name"]]
    if dept:
        employees = [e for e in employees if dept in e["dept"]]

    return templates.TemplateResponse(
        "employees.html",
        {
            "request": request,
            "active_page": "employees",
            "employees": employees,
            "search_name": name,
            "search_dept": dept,
        },
    )


@router.get("/leaves")
def leaves_page(
    request: Request,
    employee_name: str = "",
):
    conn = get_db_connection()
    leaves = crud.list_leaves(conn)
    conn.close()

    # 직원 이름 필터링
    if employee_name:
        leaves = [l for l in leaves if employee_name in l["name"]]

    return templates.TemplateResponse(
        "leaves.html",
        {
            "request": request,
            "active_page": "leaves",
            "leaves": leaves,
            "search_employee_name": employee_name,
        },
    )


@router.get("/sales")
def sales_page(
    request: Request,
    period_start: str = "",
    period_end: str = "",
    dept: str = "",
):
    conn = get_db_connection()
    sales = crud.list_sales(conn, limit=50)

    period_sales = []
    if period_start and period_end:
        period_sales = crud.get_sales_period(conn, period_start, period_end)

    dept_summary = None
    if dept:
        dept_summary = crud.get_sales_by_dept(conn, dept)

    conn.close()

    return templates.TemplateResponse(
        "sales.html",
        {
            "request": request,
            "active_page": "sales",
            "sales": sales,
            "period_sales": period_sales,
            "dept_summary": dept_summary,
            "period_start": period_start,
            "period_end": period_end,
            "dept": dept,
        },
    )


# ---- Admin Form Handlers ----

@router.post("/employees/create")
def admin_create_employee(
    name: str = Form(...),
    dept: str = Form(...),
    email: str = Form(...),
    hire_date: str = Form(...),
):
    conn = get_db_connection()
    try:
        crud.create_employee(conn, name, dept, email, hire_date)
    finally:
        conn.close()
    return RedirectResponse(url="/admin/employees", status_code=303)


@router.post("/employees/update")
def admin_update_employee(
    employee_id: int = Form(...),
    name: str = Form(""),
    dept: str = Form(""),
    email: str = Form(""),
    hire_date: str = Form(""),
):
    conn = get_db_connection()
    try:
        crud.update_employee(
            conn,
            employee_id,
            name=name or None,
            dept=dept or None,
            email=email or None,
            hire_date=hire_date or None,
        )
    finally:
        conn.close()
    return RedirectResponse(url="/admin/employees", status_code=303)


@router.post("/employees/delete")
def admin_delete_employee(employee_id: int = Form(...)):
    conn = get_db_connection()
    try:
        crud.delete_employee(conn, employee_id)
    finally:
        conn.close()
    return RedirectResponse(url="/admin/employees", status_code=303)


@router.post("/leaves/usage")
def admin_use_leave(employee_id: int = Form(...), days: float = Form(...)):
    conn = get_db_connection()
    try:
        crud.use_leave(conn, employee_id, days)
    finally:
        conn.close()
    return RedirectResponse(url="/admin/leaves", status_code=303)


@router.post("/leaves/update")
def admin_update_leave(
    leave_id: int = Form(...),
    employee_id: int = Form(...),
    year: int = Form(...),
    total: float = Form(...),
    used: float = Form(...),
    remaining: float = Form(...),
):
    conn = get_db_connection()
    try:
        crud.update_leave(
            conn,
            leave_id,
            employee_id=employee_id,
            year=year,
            total=total,
            used=used,
            remaining=remaining,
        )
    finally:
        conn.close()
    return RedirectResponse(url="/admin/leaves", status_code=303)


@router.post("/sales/create")
def admin_create_sales(
    dept: str = Form(...),
    amount: int = Form(...),
    date: str = Form(...),
    description: str = Form(""),
):
    conn = get_db_connection()
    try:
        crud.create_sale(conn, dept, amount, date, description)
    finally:
        conn.close()
    return RedirectResponse(url="/admin/sales", status_code=303)
