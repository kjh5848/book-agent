"""
CH09 LangChain 최종 연결 — MCP 도구 모듈.

CH04 FastAPI 서버의 REST API를 호출하는 LangChain Tool 3종을 제공합니다.
각 Tool은 @tool 데코레이터로 LangChain Agent가 자동 선택할 수 있도록 등록됩니다.

전제 조건:
    - CH04 rag-infra docker-compose up 으로 FastAPI 서버가 실행 중이어야 합니다.
    - .env의 FASTAPI_BASE_URL 에 서버 URL을 설정하십시오 (기본: http://localhost:8000).

도구 목록:
    - get_leave_balance    : 직원 잔여 연차 조회
    - get_sales_summary    : 부서별/분기별 매출 집계 조회
    - get_employee_info    : 직원 기본 정보 조회
"""

import os

import requests
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

# FastAPI 서버 베이스 URL (환경 변수로 재정의 가능)
_FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000").rstrip("/")

# HTTP 요청 타임아웃 (초)
_HTTP_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "60"))


def _get(endpoint: str, params: dict | None = None) -> dict:
    """FastAPI 서버에 GET 요청을 보내고 JSON 응답을 반환합니다.

    서버가 응답하지 않거나 오류 상태 코드를 반환하면 오류 메시지를 포함한
    딕셔너리를 반환하며, 예외를 외부로 전파하지 않습니다.

    Args:
        endpoint: 요청할 API 엔드포인트 경로 (예: "/employees/1/leave-balance").
        params: URL 쿼리 파라미터 딕셔너리 (선택).

    Returns:
        dict: API 응답 JSON 파싱 결과 또는 오류 정보 딕셔너리.
    """
    # --- Input ---
    url = f"{_FASTAPI_BASE_URL}{endpoint}"

    # --- Process ---
    try:
        response = requests.get(url, params=params, timeout=_HTTP_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {
            "error": (
                f"FastAPI 서버에 연결할 수 없습니다: {url}\n"
                "CH04 rag-infra 디렉토리에서 'docker-compose up -d' 명령을 실행하십시오."
            )
        }
    except requests.exceptions.Timeout:
        return {"error": f"요청 시간이 초과되었습니다 (timeout={_HTTP_TIMEOUT}s): {url}"}
    except requests.exceptions.HTTPError as exc:
        return {"error": f"HTTP 오류 발생: {exc.response.status_code} — {exc}"}
    except Exception as exc:
        return {"error": f"예상치 못한 오류가 발생했습니다: {exc}"}

    # --- Output ---


@tool
def get_leave_balance(employee_name: str) -> str:
    """직원의 잔여 연차를 조회합니다.

    CH04 FastAPI 서버의 GET /employees/{id}/leave-balance 엔드포인트를 호출합니다.
    이름으로 직원을 먼저 검색한 후 해당 직원의 연차 잔여 일수를 조회합니다.

    Args:
        employee_name: 조회할 직원의 이름 (예: "김철수").

    Returns:
        str: 잔여 연차 정보 문자열.
             예: "김철수 님의 잔여 연차: 5일 (총 15일 중 10일 사용)"
             오류 발생 시 오류 메시지 문자열을 반환합니다.
    """
    # --- Input ---
    # --- Process ---
    # 1단계: 이름으로 직원 ID 조회
    search_result = _get("/employees", params={"name": employee_name})

    if "error" in search_result:
        return search_result["error"]

    employees = search_result if isinstance(search_result, list) else search_result.get("employees", [])
    if not employees:
        return f"'{employee_name}' 이름의 직원을 찾을 수 없습니다. 이름을 정확히 입력하십시오."

    # 첫 번째 매칭 직원의 ID 사용
    employee = employees[0]
    employee_id = employee.get("id") or employee.get("employee_id")
    if not employee_id:
        return f"직원 정보에서 ID를 확인할 수 없습니다: {employee}"

    # 2단계: 연차 잔여 조회
    leave_result = _get(f"/employees/{employee_id}/leave-balance")

    if "error" in leave_result:
        return leave_result["error"]

    remaining = leave_result.get("remaining_days", leave_result.get("remaining", "알 수 없음"))
    total = leave_result.get("total_days", leave_result.get("total", "알 수 없음"))
    used = leave_result.get("used_days", leave_result.get("used", "알 수 없음"))

    # --- Output ---
    return (
        f"{employee_name} 님의 잔여 연차: {remaining}일 "
        f"(총 {total}일 중 {used}일 사용)"
    )


@tool
def get_sales_summary(department: str = "", quarter: str = "") -> str:
    """부서별, 분기별 매출 집계를 조회합니다.

    CH04 FastAPI 서버의 GET /sales/summary 엔드포인트를 호출합니다.
    department와 quarter를 비워두면 전체 집계를 반환합니다.

    Args:
        department: 부서명 (비워두면 전체 부서 집계, 예: "마케팅").
        quarter: 분기 문자열 (비워두면 전체 기간, 예: "2024-Q4").

    Returns:
        str: 매출 집계 정보 문자열.
             예: "마케팅 부서 2024-Q4 매출: 1,200,000,000원"
             오류 발생 시 오류 메시지 문자열을 반환합니다.
    """
    # --- Input ---
    params: dict = {}
    if department:
        params["department"] = department
    if quarter:
        params["quarter"] = quarter

    # --- Process ---
    result = _get("/sales/summary", params=params if params else None)

    if "error" in result:
        return result["error"]

    # 응답 형태에 따라 유연하게 처리
    if isinstance(result, list):
        if not result:
            label = f"{department or '전체'} 부서 {quarter or '전체 기간'}"
            return f"{label} 매출 데이터가 없습니다."
        lines = []
        for item in result:
            dept = item.get("department", "알 수 없음")
            q = item.get("quarter", "")
            amount = item.get("total_sales", item.get("amount", 0))
            amount_str = f"{amount:,.0f}" if isinstance(amount, (int, float)) else str(amount)
            lines.append(f"{dept} {q}: {amount_str}원")
        return "\n".join(lines)

    # 단일 딕셔너리 응답 처리
    dept_label = result.get("department", department or "전체")
    quarter_label = result.get("quarter", quarter or "전체 기간")
    total = result.get("total_sales", result.get("amount", result.get("total", 0)))
    total_str = f"{total:,.0f}" if isinstance(total, (int, float)) else str(total)

    # --- Output ---
    return f"{dept_label} 부서 {quarter_label} 매출: {total_str}원"


@tool
def get_employee_info(employee_name: str) -> str:
    """직원의 기본 정보(부서, 직급)를 조회합니다.

    CH04 FastAPI 서버의 GET /employees?name={name} 엔드포인트를 호출합니다.

    Args:
        employee_name: 조회할 직원의 이름.

    Returns:
        str: 직원의 부서, 직급, 입사일 등 기본 정보 문자열.
             예: "김철수 | 부서: 마케팅 | 직급: 대리 | 입사일: 2020-03-02"
             직원을 찾을 수 없으면 안내 메시지를 반환합니다.
    """
    # --- Input ---
    # --- Process ---
    result = _get("/employees", params={"name": employee_name})

    if "error" in result:
        return result["error"]

    employees = result if isinstance(result, list) else result.get("employees", [])
    if not employees:
        return f"'{employee_name}' 이름의 직원을 찾을 수 없습니다. 이름을 정확히 입력하십시오."

    employee = employees[0]
    name = employee.get("name", employee_name)
    dept = employee.get("department", employee.get("dept", "알 수 없음"))
    position = employee.get("position", employee.get("job_title", "알 수 없음"))
    hire_date = employee.get("hire_date", employee.get("joined_at", "알 수 없음"))
    email = employee.get("email", "")

    info_parts = [
        f"{name}",
        f"부서: {dept}",
        f"직급: {position}",
        f"입사일: {hire_date}",
    ]
    if email:
        info_parts.append(f"이메일: {email}")

    # --- Output ---
    return " | ".join(info_parts)


# MCP 도구 목록 (agent.py에서 사용)
MCP_TOOLS: list = [get_leave_balance, get_sales_summary, get_employee_info]
