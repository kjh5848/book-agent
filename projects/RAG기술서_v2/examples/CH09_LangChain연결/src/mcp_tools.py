"""MCP 스타일 DB 조회 도구 모듈 (CH09 확장판).

CH08의 MCP 도구를 확장하여 Retry 데코레이터, 실행 시간 측정,
부서별 직원 목록 조회, 연간 매출 합계 조회 기능을 추가합니다.

도구 설명(description)이 LLM의 도구 선택에 직접 영향을 미치므로
각 도구의 설명을 정확하고 구체적으로 작성합니다.

챕터 9.2: MCP Tool 설계 — 도구 구현 및 Retry 적용
"""

import json
import logging
import os
import time
from functools import wraps
from typing import Any, Callable, TypeVar

from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()

logger = logging.getLogger("ch09.mcp_tools")

# ============================================================
# DB 연결 설정
# ============================================================

DB_CONFIG: dict[str, Any] = {
    "host":     os.getenv("POSTGRES_HOST", "localhost"),
    "port":     int(os.getenv("POSTGRES_PORT", "5432")),
    "dbname":   os.getenv("POSTGRES_DB", "connecthr"),
    "user":     os.getenv("POSTGRES_USER", "admin"),
    "password": os.getenv("POSTGRES_PASSWORD", "password"),
}

# 최대 재시도 횟수
DB_MAX_RETRIES: int = int(os.getenv("LLM_MAX_RETRIES", "3"))

# ============================================================
# Mock 데이터 (DB 연결 실패 시 사용)
# ============================================================

_MOCK_EMPLOYEES: dict[str, dict] = {
    "이서연": {
        "id": 2, "name": "이서연", "department": "개발팀",
        "position": "개발자", "hire_date": "2023-01-16",
        "base_salary": 3800000, "email": "seoyeon.lee@connecthr.io",
    },
    "김도현": {
        "id": 1, "name": "김도현", "department": "개발팀",
        "position": "팀장", "hire_date": "2020-03-02",
        "base_salary": 6500000, "email": "dohyun.kim@connecthr.io",
    },
    "박민준": {
        "id": 3, "name": "박민준", "department": "데이터팀",
        "position": "과장", "hire_date": "2021-07-05",
        "base_salary": 5200000, "email": "minjun.park@connecthr.io",
    },
    "최지은": {
        "id": 4, "name": "최지은", "department": "영업팀",
        "position": "팀장", "hire_date": "2019-09-01",
        "base_salary": 6200000, "email": "jieun.choi@connecthr.io",
    },
    "정다희": {
        "id": 5, "name": "정다희", "department": "인사팀",
        "position": "사원", "hire_date": "2024-02-20",
        "base_salary": 3500000, "email": "dahee.jung@connecthr.io",
    },
    "한재원": {
        "id": 6, "name": "한재원", "department": "영업팀",
        "position": "대리", "hire_date": "2022-03-14",
        "base_salary": 4200000, "email": "jaewon.han@connecthr.io",
    },
    "오수빈": {
        "id": 7, "name": "오수빈", "department": "개발팀",
        "position": "사원", "hire_date": "2024-04-01",
        "base_salary": 3600000, "email": "subin.oh@connecthr.io",
    },
}

_MOCK_LEAVE_BALANCE: dict[str, dict] = {
    "이서연": {"이름": "이서연", "연도": 2024, "총_연차": 15, "사용_연차": 12, "잔여_연차": 3},
    "김도현": {"이름": "김도현", "연도": 2024, "총_연차": 15, "사용_연차": 7,  "잔여_연차": 8},
    "박민준": {"이름": "박민준", "연도": 2024, "총_연차": 15, "사용_연차": 5,  "잔여_연차": 10},
    "최지은": {"이름": "최지은", "연도": 2024, "총_연차": 15, "사용_연차": 9,  "잔여_연차": 6},
    "정다희": {"이름": "정다희", "연도": 2024, "총_연차": 10, "사용_연차": 2,  "잔여_연차": 8},
    "한재원": {"이름": "한재원", "연도": 2024, "총_연차": 15, "사용_연차": 4,  "잔여_연차": 11},
    "오수빈": {"이름": "오수빈", "연도": 2024, "총_연차": 10, "사용_연차": 1,  "잔여_연차": 9},
}

_MOCK_SALES_MONTHLY: dict[str, dict] = {
    "개발팀_2024_1":   {"부서": "개발팀",  "연도": 2024, "월": 1,  "매출액": 85000000,  "목표액": 90000000,  "달성률": 94.4},
    "개발팀_2024_2":   {"부서": "개발팀",  "연도": 2024, "월": 2,  "매출액": 92000000,  "목표액": 90000000,  "달성률": 102.2},
    "개발팀_2024_3":   {"부서": "개발팀",  "연도": 2024, "월": 3,  "매출액": 88000000,  "목표액": 90000000,  "달성률": 97.8},
    "개발팀_2024_4":   {"부서": "개발팀",  "연도": 2024, "월": 4,  "매출액": 95000000,  "목표액": 95000000,  "달성률": 100.0},
    "개발팀_2024_5":   {"부서": "개발팀",  "연도": 2024, "월": 5,  "매출액": 97000000,  "목표액": 95000000,  "달성률": 102.1},
    "개발팀_2024_6":   {"부서": "개발팀",  "연도": 2024, "월": 6,  "매출액": 91000000,  "목표액": 95000000,  "달성률": 95.8},
    "개발팀_2024_7":   {"부서": "개발팀",  "연도": 2024, "월": 7,  "매출액": 86000000,  "목표액": 90000000,  "달성률": 95.6},
    "개발팀_2024_8":   {"부서": "개발팀",  "연도": 2024, "월": 8,  "매출액": 89000000,  "목표액": 90000000,  "달성률": 98.9},
    "개발팀_2024_9":   {"부서": "개발팀",  "연도": 2024, "월": 9,  "매출액": 93000000,  "목표액": 90000000,  "달성률": 103.3},
    "개발팀_2024_10":  {"부서": "개발팀",  "연도": 2024, "월": 10, "매출액": 98000000,  "목표액": 100000000, "달성률": 98.0},
    "개발팀_2024_11":  {"부서": "개발팀",  "연도": 2024, "월": 11, "매출액": 102000000, "목표액": 100000000, "달성률": 102.0},
    "개발팀_2024_12":  {"부서": "개발팀",  "연도": 2024, "월": 12, "매출액": 105000000, "목표액": 105000000, "달성률": 100.0},
    "영업팀_2024_1":   {"부서": "영업팀",  "연도": 2024, "월": 1,  "매출액": 120000000, "목표액": 130000000, "달성률": 92.3},
    "영업팀_2024_10":  {"부서": "영업팀",  "연도": 2024, "월": 10, "매출액": 142000000, "목표액": 140000000, "달성률": 101.4},
    "영업팀_2024_11":  {"부서": "영업팀",  "연도": 2024, "월": 11, "매출액": 155000000, "목표액": 145000000, "달성률": 106.9},
    "영업팀_2024_12":  {"부서": "영업팀",  "연도": 2024, "월": 12, "매출액": 162000000, "목표액": 150000000, "달성률": 108.0},
    "데이터팀_2024_1": {"부서": "데이터팀", "연도": 2024, "월": 1,  "매출액": 45000000,  "목표액": 50000000,  "달성률": 90.0},
}

# 부서별 직원 목록 Mock 데이터
_MOCK_DEPT_EMPLOYEES: dict[str, list[dict]] = {
    "개발팀":  [
        {"이름": "김도현", "직급": "팀장"},
        {"이름": "이서연", "직급": "개발자"},
        {"이름": "오수빈", "직급": "사원"},
    ],
    "데이터팀": [
        {"이름": "박민준", "직급": "과장"},
    ],
    "영업팀":  [
        {"이름": "최지은", "직급": "팀장"},
        {"이름": "한재원", "직급": "대리"},
    ],
    "인사팀":  [
        {"이름": "정다희", "직급": "사원"},
    ],
}


# ============================================================
# 유틸리티: Retry 데코레이터 + 실행 시간 측정
# ============================================================

F = TypeVar("F", bound=Callable[..., Any])


def with_retry(max_retries: int = 3, base_delay: float = 1.0) -> Callable[[F], F]:
    """Exponential Backoff 재시도 데코레이터를 반환합니다.

    함수 호출 실패 시 최대 max_retries회까지 재시도합니다.
    대기 시간은 base_delay * 2^(시도횟수-1) 초로 증가합니다.

    Args:
        max_retries: 최대 재시도 횟수 (기본값: 3)
        base_delay:  첫 번째 재시도 전 대기 시간(초) (기본값: 1.0)

    Returns:
        재시도 로직이 추가된 데코레이터 함수
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:

            # --- Input ---
            last_exception: Exception | None = None

            # --- Process ---
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exception = exc
                    if attempt < max_retries:
                        delay = base_delay * (2 ** (attempt - 1))
                        logger.warning(
                            "%s 실패 (시도 %d/%d). %.1f초 후 재시도합니다. 오류: %s",
                            func.__name__,
                            attempt,
                            max_retries,
                            delay,
                            exc,
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            "%s 최종 실패 (총 %d회 시도). 오류: %s",
                            func.__name__,
                            max_retries,
                            exc,
                        )

            # --- Output ---
            raise last_exception  # type: ignore[misc]

        return wrapper  # type: ignore[return-value]

    return decorator


def measure_time(func: F) -> F:
    """함수 실행 시간을 측정하고 로그로 출력하는 데코레이터.

    Args:
        func: 측정 대상 함수

    Returns:
        실행 시간 측정 로직이 추가된 래핑 함수
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:

        # --- Input ---
        start = time.perf_counter()

        # --- Process ---
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start

        # --- Output ---
        logger.debug("%s 실행 완료: %.3f초", func.__name__, elapsed)
        return result

    return wrapper  # type: ignore[return-value]


# ============================================================
# DB 연결 헬퍼
# ============================================================


def _get_db_connection():
    """PostgreSQL 연결 객체를 반환합니다.

    Returns:
        psycopg2 연결 객체

    Raises:
        psycopg2.OperationalError: DB 연결 실패 시
    """

    # --- Process ---
    import psycopg2
    return psycopg2.connect(**DB_CONFIG)

    # --- Output ---
    # psycopg2 Connection 반환


# ============================================================
# MCP 스타일 도구 정의
# ============================================================


@tool
@measure_time
def get_employee_info(name: str) -> str:
    """직원 이름으로 개인 인사 정보를 조회합니다.

    직원의 부서, 직급, 입사일, 기본 급여, 이메일 등
    인사 정보를 데이터베이스에서 가져옵니다.
    특정 직원의 개인 정보가 필요할 때 사용하십시오.

    Args:
        name: 조회할 직원 이름 (예: '이서연', '김도현')

    Returns:
        직원 정보가 담긴 JSON 문자열.
        직원이 없으면 오류 메시지 JSON.
    """

    # --- Input ---
    query = """
        SELECT id, name, department, position,
               hire_date::text, base_salary, email, is_active
        FROM employees
        WHERE name = %s
        LIMIT 1;
    """

    # --- Process ---
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor

        conn = _get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (name,))
            row = cur.fetchone()
        conn.close()

        if row is None:
            return json.dumps(
                {"오류": f"'{name}' 직원을 찾을 수 없습니다."},
                ensure_ascii=False,
            )
        return json.dumps(dict(row), ensure_ascii=False, default=str)

    except psycopg2.OperationalError:
        logger.warning("PostgreSQL 미연결 — Mock 직원 데이터를 사용합니다.")
        mock = _MOCK_EMPLOYEES.get(name)
        if mock is None:
            return json.dumps(
                {"오류": f"'{name}' 직원을 찾을 수 없습니다. (Mock 데이터)"},
                ensure_ascii=False,
            )
        return json.dumps(mock, ensure_ascii=False, default=str)

    # --- Output ---
    # JSON 문자열 반환


@tool
@measure_time
def get_leave_balance(employee_id: int) -> str:
    """직원 ID로 해당 직원의 연차 잔액을 조회합니다.

    지정한 직원의 총 연차일수, 사용일수, 잔여일수를
    데이터베이스에서 가져옵니다.
    직원 ID를 모르는 경우 먼저 get_employee_info로 조회하십시오.

    Args:
        employee_id: 직원 고유 ID (정수, 예: 2)

    Returns:
        연차 잔액 정보 JSON 문자열 (총일수, 사용일수, 잔여일수).
    """

    # --- Input ---
    query = """
        SELECT
            e.name              AS 이름,
            lb.year             AS 연도,
            lb.total_days       AS 총_연차,
            lb.used_days        AS 사용_연차,
            (lb.total_days - lb.used_days) AS 잔여_연차
        FROM leave_balance lb
        JOIN employees e ON e.id = lb.employee_id
        WHERE lb.employee_id = %s
          AND lb.year = 2024
        ORDER BY lb.year DESC
        LIMIT 1;
    """

    # --- Process ---
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor

        conn = _get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (employee_id,))
            row = cur.fetchone()
        conn.close()

        if row is None:
            return json.dumps(
                {"오류": f"직원 ID {employee_id}의 연차 정보가 없습니다."},
                ensure_ascii=False,
            )
        return json.dumps(dict(row), ensure_ascii=False, default=str)

    except psycopg2.OperationalError:
        logger.warning("PostgreSQL 미연결 — Mock 연차 데이터를 사용합니다.")
        id_to_name: dict[int, str] = {v["id"]: k for k, v in _MOCK_EMPLOYEES.items()}
        name = id_to_name.get(employee_id)
        if name is None:
            return json.dumps(
                {"오류": f"직원 ID {employee_id}의 연차 정보를 찾을 수 없습니다. (Mock 데이터)"},
                ensure_ascii=False,
            )
        mock = _MOCK_LEAVE_BALANCE.get(name)
        if mock is None:
            return json.dumps(
                {"오류": f"'{name}'의 연차 정보가 없습니다. (Mock 데이터)"},
                ensure_ascii=False,
            )
        return json.dumps(mock, ensure_ascii=False, default=str)

    # --- Output ---
    # JSON 문자열 반환


@tool
@measure_time
def get_department_sales(department: str, year: int, month: int) -> str:
    """특정 부서의 월별 매출 현황을 조회합니다.

    지정한 부서와 연도/월의 실제 매출, 목표 매출, 달성률을
    데이터베이스에서 가져옵니다.
    월별 매출 실적이나 목표 달성률을 확인할 때 사용하십시오.

    Args:
        department: 부서명 (예: '영업팀', '개발팀', '데이터팀')
        year:       조회 연도 (예: 2024)
        month:      조회 월 (1~12)

    Returns:
        매출 현황 JSON 문자열 (매출액, 목표액, 달성률).
    """

    # --- Input ---
    query = """
        SELECT
            department  AS 부서,
            year        AS 연도,
            month       AS 월,
            revenue     AS 매출액,
            target      AS 목표액,
            CASE
                WHEN target IS NOT NULL AND target > 0
                THEN ROUND((revenue / target * 100)::numeric, 1)
                ELSE NULL
            END AS 달성률
        FROM sales_monthly
        WHERE department = %s
          AND year = %s
          AND month = %s;
    """

    # --- Process ---
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor

        conn = _get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (department, year, month))
            row = cur.fetchone()
        conn.close()

        if row is None:
            return json.dumps(
                {"오류": f"'{department}' {year}년 {month}월 매출 데이터가 없습니다."},
                ensure_ascii=False,
            )
        return json.dumps(dict(row), ensure_ascii=False, default=str)

    except psycopg2.OperationalError:
        logger.warning("PostgreSQL 미연결 — Mock 매출 데이터를 사용합니다.")
        key = f"{department}_{year}_{month}"
        mock = _MOCK_SALES_MONTHLY.get(key)
        if mock is None:
            return json.dumps(
                {"오류": f"'{department}' {year}년 {month}월 매출 데이터가 없습니다. (Mock 데이터)"},
                ensure_ascii=False,
            )
        return json.dumps(mock, ensure_ascii=False, default=str)

    # --- Output ---
    # JSON 문자열 반환


@tool
@measure_time
def get_employee_list(department: str) -> str:
    """특정 부서에 소속된 전체 직원 목록을 조회합니다.

    부서명을 입력하면 해당 부서의 모든 직원 이름과 직급을
    데이터베이스에서 가져옵니다.
    특정 부서에 누가 소속되어 있는지 확인할 때 사용하십시오.

    Args:
        department: 부서명 (예: '개발팀', '영업팀', '인사팀', '데이터팀')

    Returns:
        직원 목록 JSON 문자열 (이름, 직급 포함).
        해당 부서 직원이 없으면 빈 목록 JSON.
    """

    # --- Input ---
    query = """
        SELECT name AS 이름, position AS 직급
        FROM employees
        WHERE department = %s AND is_active = TRUE
        ORDER BY hire_date;
    """

    # --- Process ---
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor

        conn = _get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (department,))
            rows = cur.fetchall()
        conn.close()

        result = [dict(row) for row in rows]
        return json.dumps(
            {"부서": department, "직원수": len(result), "직원목록": result},
            ensure_ascii=False,
            default=str,
        )

    except psycopg2.OperationalError:
        logger.warning("PostgreSQL 미연결 — Mock 부서 직원 목록을 사용합니다.")
        mock_list = _MOCK_DEPT_EMPLOYEES.get(department, [])
        return json.dumps(
            {"부서": department, "직원수": len(mock_list), "직원목록": mock_list},
            ensure_ascii=False,
        )

    # --- Output ---
    # JSON 문자열 반환


@tool
@measure_time
def get_annual_sales(department: str, year: int) -> str:
    """특정 부서의 연간 매출 합계를 계산하여 반환합니다.

    지정한 부서와 연도의 월별 매출을 모두 합산하여
    연간 총 매출액, 연간 총 목표액, 연간 달성률을 제공합니다.
    연간 실적을 요약할 때 사용하십시오.

    Args:
        department: 부서명 (예: '개발팀', '영업팀', '데이터팀')
        year:       조회 연도 (예: 2024)

    Returns:
        연간 매출 합계 JSON 문자열 (연간매출, 연간목표, 달성률).
    """

    # --- Input ---
    query = """
        SELECT
            department          AS 부서,
            year                AS 연도,
            SUM(revenue)        AS 연간매출,
            SUM(target)         AS 연간목표,
            CASE
                WHEN SUM(target) > 0
                THEN ROUND((SUM(revenue)::numeric / SUM(target) * 100), 1)
                ELSE NULL
            END AS 연간달성률,
            COUNT(*)            AS 기록월수
        FROM sales_monthly
        WHERE department = %s AND year = %s
        GROUP BY department, year;
    """

    # --- Process ---
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor

        conn = _get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (department, year))
            row = cur.fetchone()
        conn.close()

        if row is None:
            return json.dumps(
                {"오류": f"'{department}' {year}년 연간 매출 데이터가 없습니다."},
                ensure_ascii=False,
            )
        return json.dumps(dict(row), ensure_ascii=False, default=str)

    except psycopg2.OperationalError:
        logger.warning("PostgreSQL 미연결 — Mock 연간 매출 데이터를 계산합니다.")
        # Mock 데이터에서 해당 부서/연도 데이터를 합산
        monthly_data = [
            v for k, v in _MOCK_SALES_MONTHLY.items()
            if k.startswith(f"{department}_{year}_")
        ]
        if not monthly_data:
            return json.dumps(
                {"오류": f"'{department}' {year}년 연간 매출 데이터가 없습니다. (Mock 데이터)"},
                ensure_ascii=False,
            )

        total_revenue = sum(d["매출액"] for d in monthly_data)
        total_target = sum(d["목표액"] for d in monthly_data)
        annual_rate = round(total_revenue / total_target * 100, 1) if total_target > 0 else None

        return json.dumps(
            {
                "부서": department,
                "연도": year,
                "연간매출": total_revenue,
                "연간목표": total_target,
                "연간달성률": annual_rate,
                "기록월수": len(monthly_data),
                "비고": "Mock 데이터 기반 집계",
            },
            ensure_ascii=False,
        )

    # --- Output ---
    # JSON 문자열 반환


# ============================================================
# 도구 목록 (에이전트에 전달)
# ============================================================

DB_TOOLS = [
    get_employee_info,
    get_leave_balance,
    get_department_sales,
    get_employee_list,
    get_annual_sales,
]
