from typing import List, Optional, Dict, Any

def _row_to_dict(row: Any) -> Dict[str, Any]:
    """psycopg2 DictRow 또는 유사한 객체를 순수 dict로 변환"""
    return dict(row) if row is not None else {}

def list_employees(conn: Any) -> List[Dict[str, Any]]:
    rows = conn.execute("SELECT * FROM employees ORDER BY id DESC").fetchall()
    return [dict(row) for row in rows]

def get_employee(conn: Any, employee_id: int) -> Optional[Dict[str, Any]]:
    row = conn.execute("SELECT * FROM employees WHERE id = %s", (employee_id,)).fetchone()
    return _row_to_dict(row) if row else None

def create_employee(conn: Any, name: str, dept: str, email: str, hire_date: str) -> Dict[str, Any]:
    # PostgreSQL 전용 RETURNING id 구문 사용
    cursor = conn.execute(
        "INSERT INTO employees (name, dept, email, hire_date) VALUES (%s, %s, %s, %s) RETURNING id",
        (name, dept, email, hire_date),
    )
    new_id = cursor.fetchone()[0]
    conn.commit()
    return get_employee(conn, new_id)

def update_employee(
    conn: Any,
    employee_id: int,
    name: Optional[str] = None,
    dept: Optional[str] = None,
    email: Optional[str] = None,
    hire_date: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    current = get_employee(conn, employee_id)
    if not current:
        return None
    name = name if name is not None else current["name"]
    dept = dept if dept is not None else current["dept"]
    email = email if email is not None else current["email"]
    hire_date = hire_date if hire_date is not None else current["hire_date"]
    conn.execute(
        "UPDATE employees SET name = %s, dept = %s, email = %s, hire_date = %s WHERE id = %s",
        (name, dept, email, hire_date, employee_id),
    )
    conn.commit()
    return get_employee(conn, employee_id)

def delete_employee(conn: Any, employee_id: int) -> bool:
    cursor = conn.execute("DELETE FROM employees WHERE id = %s", (employee_id,))
    conn.commit()
    return cursor.rowcount > 0

def list_leaves(conn: Any) -> List[Dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT l.*, e.name
        FROM leave_balance l
        JOIN employees e ON l.employee_id = e.id
        ORDER BY l.id DESC
        """
    ).fetchall()
    return [dict(row) for row in rows]

def get_leave_by_employee(conn: Any, employee_id: int) -> Optional[Dict[str, Any]]:
    row = conn.execute(
        "SELECT * FROM leave_balance WHERE employee_id = %s",
        (employee_id,),
    ).fetchone()
    return _row_to_dict(row) if row else None

def get_leave_by_id(conn: Any, leave_id: int) -> Optional[Dict[str, Any]]:
    row = conn.execute("SELECT * FROM leave_balance WHERE id = %s", (leave_id,)).fetchone()
    return _row_to_dict(row) if row else None

def use_leave(conn: Any, employee_id: int, days: float) -> Optional[Dict[str, Any]]:
    leave = get_leave_by_employee(conn, employee_id)
    if not leave:
        return None
    new_used = float(leave["used"]) + float(days)
    new_remaining = float(leave["total"]) - new_used
    conn.execute(
        "UPDATE leave_balance SET used = %s, remaining = %s WHERE employee_id = %s",
        (new_used, new_remaining, employee_id),
    )
    conn.commit()
    return get_leave_by_employee(conn, employee_id)

def update_leave(
    conn: Any,
    leave_id: int,
    employee_id: Optional[int] = None,
    year: Optional[int] = None,
    total: Optional[float] = None,
    used: Optional[float] = None,
    remaining: Optional[float] = None,
) -> Optional[Dict[str, Any]]:
    current = get_leave_by_id(conn, leave_id)
    if not current:
        return None
    employee_id = employee_id if employee_id is not None else current["employee_id"]
    year = year if year is not None else current["year"]
    total = total if total is not None else current["total"]
    used = used if used is not None else current["used"]
    remaining = remaining if remaining is not None else current["remaining"]
    conn.execute(
        """
        UPDATE leave_balance
        SET employee_id = %s, year = %s, total = %s, used = %s, remaining = %s
        WHERE id = %s
        """,
        (employee_id, year, total, used, remaining, leave_id),
    )
    conn.commit()
    return get_leave_by_id(conn, leave_id)

def list_sales(conn: Any, limit: int = 50) -> List[Dict[str, Any]]:
    rows = conn.execute(
        "SELECT * FROM sales ORDER BY date DESC, id DESC LIMIT %s",
        (limit,),
    ).fetchall()
    return [dict(row) for row in rows]

def create_sale(conn: Any, dept: str, amount: int, date: str, description: Optional[str]) -> Dict[str, Any]:
    cursor = conn.execute(
        "INSERT INTO sales (dept, amount, date, description) VALUES (%s, %s, %s, %s) RETURNING id",
        (dept, amount, date, description),
    )
    new_id = cursor.fetchone()[0]
    conn.commit()
    # PostgreSQL 특성에 맞춰 반환 처리
    row = conn.execute("SELECT * FROM sales WHERE id = %s", (new_id,)).fetchone()
    return _row_to_dict(row)

def get_sales_period(conn: Any, start: str, end: str) -> List[Dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT * FROM sales
        WHERE date BETWEEN %s AND %s
        ORDER BY date DESC, id DESC
        """,
        (start, end),
    ).fetchall()
    return [dict(row) for row in rows]

def get_sales_by_dept(conn: Any, dept_name: str) -> Dict[str, Any]:
    row = conn.execute(
        """
        SELECT dept, SUM(amount) AS total_amount
        FROM sales
        WHERE dept = %s
        GROUP BY dept
        """,
        (dept_name,),
    ).fetchone()
    return _row_to_dict(row) if row else {"dept": dept_name, "total_amount": 0}

def count_employees(conn: Any) -> int:
    row = conn.execute("SELECT COUNT(*) AS cnt FROM employees").fetchone()
    return int(row["cnt"]) if row else 0

def count_leaves(conn: Any) -> int:
    row = conn.execute("SELECT COUNT(*) AS cnt FROM leave_balance").fetchone()
    return int(row["cnt"]) if row else 0

def count_sales(conn: Any) -> int:
    row = conn.execute("SELECT COUNT(*) AS cnt FROM sales").fetchone()
    return int(row["cnt"]) if row else 0

def sum_sales(conn: Any) -> int:
    row = conn.execute("SELECT COALESCE(SUM(amount), 0) AS total FROM sales").fetchone()
    return int(row["total"]) if row else 0
