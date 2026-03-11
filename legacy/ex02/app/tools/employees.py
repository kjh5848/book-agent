from langchain_core.tools import tool
from typing import List, Dict, Any
from database import get_db_connection, crud

@tool
def list_employees(dept: str = None) -> List[Dict[str, Any]]:
    """
    직원 목록을 조회합니다. 
    특정 부서(dept)를 지정하면 해당 부서의 직원만 조회합니다.
    
    Args:
        dept (str, optional): 조회할 부서명 (예: "영업팀", "인사팀"). 없으면 전체 직원을 조회합니다.
    """
    conn = get_db_connection()
    try:
        employees = crud.list_employees(conn)
        
        if dept:
            filtered = [e for e in employees if dept in e['dept']]
            return filtered
        
        return employees
    finally:
        conn.close()
