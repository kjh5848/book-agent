"""
PostgreSQL CRUD 함수 모음.

직원(employees), 휴가(leave_balance), 매출(sales) 테이블에 대한
조회/생성/수정/삭제 함수와 대시보드용 통계 함수를 제공합니다.

모든 함수는 PostgresConnectionWrapper를 첫 번째 인수로 받습니다.
"""

from typing import Any

from app.database.connection import PostgresConnectionWrapper


# ─── 직원 CRUD ───────────────────────────────────────────────


def list_employees(conn: PostgresConnectionWrapper) -> list[dict[str, Any]]:
    """
    전체 직원 목록을 조회합니다.

    Args:
        conn: PostgresConnectionWrapper 연결 객체.

    Returns:
        list[dict]: 직원 정보 딕셔너리 리스트.
    """
    # --- Input ---
    # --- Process ---
    conn.execute("SELECT id, name, dept, email, hire_date::text FROM employees ORDER BY id")
    # --- Output ---
    return conn.fetchall()


def get_employee(conn: PostgresConnectionWrapper, employee_id: int) -> dict[str, Any] | None:
    """
    특정 직원의 상세 정보를 조회합니다.

    Args:
        conn: PostgresConnectionWrapper 연결 객체.
        employee_id: 조회할 직원 ID.

    Returns:
        dict | None: 직원 정보 딕셔너리, 없으면 None.
    """
    # --- Input ---
    # --- Process ---
    conn.execute(
        "SELECT id, name, dept, email, hire_date::text FROM employees WHERE id = %s",
        (employee_id,),
    )
    # --- Output ---
    return conn.fetchone()


def create_employee(
    conn: PostgresConnectionWrapper,
    name: str,
    dept: str,
    email: str,
    hire_date: str,
) -> dict[str, Any]:
    """
    새 직원을 등록합니다.

    Args:
        conn: PostgresConnectionWrapper 연결 객체.
        name: 직원 이름.
        dept: 부서명.
        email: 이메일 주소.
        hire_date: 입사일 (YYYY-MM-DD 형식).

    Returns:
        dict: 생성된 직원 정보 딕셔너리.

    Raises:
        Exception: 이메일 중복 등 DB 오류 발생 시.
    """
    # --- Input ---
    # --- Process ---
    conn.execute(
        "INSERT INTO employees (name, dept, email, hire_date) VALUES (%s, %s, %s, %s) RETURNING id, name, dept, email, hire_date::text",
        (name, dept, email, hire_date),
    )
    result = conn.fetchone()
    conn.commit()
    # --- Output ---
    return result


def update_employee(
    conn: PostgresConnectionWrapper,
    employee_id: int,
    **fields: Any,
) -> dict[str, Any] | None:
    """
    직원 정보를 수정합니다.

    Args:
        conn: PostgresConnectionWrapper 연결 객체.
        employee_id: 수정할 직원 ID.
        **fields: 수정할 필드와 값 (name, dept, email, hire_date 중 일부).

    Returns:
        dict | None: 수정된 직원 정보, 대상이 없으면 None.
    """
    # --- Input ---
    allowed = {"name", "dept", "email", "hire_date"}
    valid_fields = {k: v for k, v in fields.items() if k in allowed}
    if not valid_fields:
        return get_employee(conn, employee_id)

    # --- Process ---
    set_clause = ", ".join(f"{k} = %s" for k in valid_fields)
    values = list(valid_fields.values()) + [employee_id]
    conn.execute(
        f"UPDATE employees SET {set_clause} WHERE id = %s RETURNING id, name, dept, email, hire_date::text",
        tuple(values),
    )
    result = conn.fetchone()
    conn.commit()
    # --- Output ---
    return result


def delete_employee(conn: PostgresConnectionWrapper, employee_id: int) -> bool:
    """
    직원을 삭제합니다.

    Args:
        conn: PostgresConnectionWrapper 연결 객체.
        employee_id: 삭제할 직원 ID.

    Returns:
        bool: 삭제 성공 여부.
    """
    # --- Input ---
    # --- Process ---
    conn.execute("DELETE FROM employees WHERE id = %s RETURNING id", (employee_id,))
    deleted = conn.fetchone()
    conn.commit()
    # --- Output ---
    return deleted is not None


# ─── 휴가 CRUD ───────────────────────────────────────────────


def list_leaves(conn: PostgresConnectionWrapper) -> list[dict[str, Any]]:
    """
    전체 직원의 휴가 현황을 조회합니다.

    Args:
        conn: PostgresConnectionWrapper 연결 객체.

    Returns:
        list[dict]: 직원명 포함 휴가 현황 딕셔너리 리스트.
    """
    # --- Input ---
    # --- Process ---
    conn.execute(
        """
        SELECT lb.id, lb.employee_id, e.name, lb.year,
               lb.total, lb.used, lb.remaining
        FROM leave_balance lb
        JOIN employees e ON lb.employee_id = e.id
        ORDER BY lb.employee_id
        """
    )
    # --- Output ---
    return conn.fetchall()


def get_leave_by_employee(
    conn: PostgresConnectionWrapper,
    employee_id: int,
) -> dict[str, Any] | None:
    """
    특정 직원의 휴가 잔여 정보를 조회합니다.

    Args:
        conn: PostgresConnectionWrapper 연결 객체.
        employee_id: 조회할 직원 ID.

    Returns:
        dict | None: 휴가 정보 딕셔너리, 없으면 None.
    """
    # --- Input ---
    # --- Process ---
    conn.execute(
        """
        SELECT lb.id, lb.employee_id, e.name, lb.year,
               lb.total, lb.used, lb.remaining
        FROM leave_balance lb
        JOIN employees e ON lb.employee_id = e.id
        WHERE lb.employee_id = %s
        ORDER BY lb.year DESC LIMIT 1
        """,
        (employee_id,),
    )
    # --- Output ---
    return conn.fetchone()


def use_leave(
    conn: PostgresConnectionWrapper,
    employee_id: int,
    days: float,
) -> dict[str, Any] | None:
    """
    휴가 사용을 등록하고 잔여량을 자동 차감합니다.

    Args:
        conn: PostgresConnectionWrapper 연결 객체.
        employee_id: 휴가를 사용할 직원 ID.
        days: 사용할 휴가 일수.

    Returns:
        dict | None: 업데이트된 휴가 정보, 직원이 없으면 None.

    Raises:
        ValueError: 잔여 휴가가 부족한 경우.
    """
    # --- Input ---
    current = get_leave_by_employee(conn, employee_id)
    if not current:
        return None

    if float(current["remaining"]) < days:
        raise ValueError(
            f"잔여 휴가가 부족합니다. 요청: {days}일, 잔여: {current['remaining']}일"
        )

    # --- Process ---
    conn.execute(
        """
        UPDATE leave_balance
        SET used = used + %s, remaining = remaining - %s
        WHERE employee_id = %s
        RETURNING id, employee_id, year, total, used, remaining
        """,
        (days, days, employee_id),
    )
    result = conn.fetchone()
    conn.commit()
    # --- Output ---
    return result


# ─── 매출 CRUD ───────────────────────────────────────────────


def list_sales(conn: PostgresConnectionWrapper, limit: int = 50) -> list[dict[str, Any]]:
    """
    전체 매출 내역을 최신 순으로 조회합니다.

    Args:
        conn: PostgresConnectionWrapper 연결 객체.
        limit: 최대 반환 건수 (기본값: 50).

    Returns:
        list[dict]: 매출 내역 딕셔너리 리스트.
    """
    # --- Input ---
    # --- Process ---
    conn.execute(
        "SELECT id, dept, amount, date::text, description FROM sales ORDER BY date DESC LIMIT %s",
        (limit,),
    )
    # --- Output ---
    return conn.fetchall()


def create_sale(
    conn: PostgresConnectionWrapper,
    dept: str,
    amount: int,
    date: str,
    description: str | None = None,
) -> dict[str, Any]:
    """
    매출 데이터를 입력합니다.

    Args:
        conn: PostgresConnectionWrapper 연결 객체.
        dept: 부서명.
        amount: 매출 금액 (원).
        date: 매출 발생일 (YYYY-MM-DD 형식).
        description: 설명 (선택값).

    Returns:
        dict: 생성된 매출 정보 딕셔너리.
    """
    # --- Input ---
    # --- Process ---
    conn.execute(
        "INSERT INTO sales (dept, amount, date, description) VALUES (%s, %s, %s, %s) RETURNING id, dept, amount, date::text, description",
        (dept, amount, date, description),
    )
    result = conn.fetchone()
    conn.commit()
    # --- Output ---
    return result


def get_sales_period(
    conn: PostgresConnectionWrapper,
    start: str,
    end: str,
) -> list[dict[str, Any]]:
    """
    특정 기간의 매출 내역을 조회합니다.

    Args:
        conn: PostgresConnectionWrapper 연결 객체.
        start: 조회 시작일 (YYYY-MM-DD 형식).
        end: 조회 종료일 (YYYY-MM-DD 형식).

    Returns:
        list[dict]: 해당 기간 매출 내역 딕셔너리 리스트.
    """
    # --- Input ---
    # --- Process ---
    conn.execute(
        "SELECT id, dept, amount, date::text, description FROM sales WHERE date BETWEEN %s AND %s ORDER BY date DESC",
        (start, end),
    )
    # --- Output ---
    return conn.fetchall()


def get_sales_by_dept(
    conn: PostgresConnectionWrapper,
    dept_name: str,
) -> dict[str, Any]:
    """
    부서별 매출 집계 결과를 조회합니다.

    Args:
        conn: PostgresConnectionWrapper 연결 객체.
        dept_name: 조회할 부서명.

    Returns:
        dict: {dept, total_amount, count} 집계 결과 딕셔너리.
    """
    # --- Input ---
    # --- Process ---
    conn.execute(
        "SELECT dept, COALESCE(SUM(amount), 0) AS total_amount, COUNT(*) AS count FROM sales WHERE dept = %s GROUP BY dept",
        (dept_name,),
    )
    result = conn.fetchone()
    # --- Output ---
    if result:
        return result
    return {"dept": dept_name, "total_amount": 0, "count": 0}


# ─── 통계 (대시보드용) ───────────────────────────────────────


def count_employees(conn: PostgresConnectionWrapper) -> int:
    """
    전체 직원 수를 반환합니다.

    Args:
        conn: PostgresConnectionWrapper 연결 객체.

    Returns:
        int: 전체 직원 수.
    """
    # --- Input ---
    # --- Process ---
    conn.execute("SELECT COUNT(*) AS cnt FROM employees")
    row = conn.fetchone()
    # --- Output ---
    return int(row["cnt"]) if row else 0


def sum_sales(conn: PostgresConnectionWrapper) -> int:
    """
    전체 매출 합계를 반환합니다.

    Args:
        conn: PostgresConnectionWrapper 연결 객체.

    Returns:
        int: 전체 매출 합계 (원).
    """
    # --- Input ---
    # --- Process ---
    conn.execute("SELECT COALESCE(SUM(amount), 0) AS total FROM sales")
    row = conn.fetchone()
    # --- Output ---
    return int(row["total"]) if row else 0
