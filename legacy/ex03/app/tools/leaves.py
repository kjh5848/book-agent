from langchain_core.tools import tool
from typing import Dict, Any, Union
from database import get_db_connection, crud

@tool
def get_leave_balance(employee_name: str) -> Union[Dict[str, Any], str]:
    """
    특정 직원의 휴가 잔여일 및 사용 내역을 조회합니다.
    
    Args:
        employee_name (str): 조회할 직원의 이름 (예: "홍길동")
    """
    conn = get_db_connection()
    try:
        # 1. 직원 ID 찾기 (이름으로 검색)
        employees = crud.list_employees(conn)
        target_emp = next((e for e in employees if e['name'] == employee_name), None)
        
        if not target_emp:
            return f"직원 '{employee_name}'을(를) 찾을 수 없습니다."
            
        # 2. 휴가 정보 조회
        leave = crud.get_leave_by_employee(conn, target_emp['id'])
        if not leave:
            return f"{employee_name} 님의 휴가 정보가 존재하지 않습니다."
            
        return {
            "employee_name": employee_name,
            "dept": target_emp['dept'],
            "total_leaves": leave['total'],
            "used_leaves": leave['used'],
            "remaining_leaves": leave['remaining']
        }
    finally:
        conn.close()
