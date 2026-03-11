from typing import List, Dict, Any
from database import get_db_connection
from database import crud

class DBService:
    """
    정형 데이터 처리 서비스. 
    MCP 서버에 정의된 도구(Tools)들의 로직을 활용하여 데이터를 수집합니다.
    """
    def __init__(self):
        print("[DBService] MCP 도구 로직으로 초기화 중...")

    def search_structured(self, query: str) -> Dict[str, Any]:
        """
        MCP 도구가 제공하는 기능을 시뮬레이션하여 정형 데이터를 조회합니다.
        질문에 포함된 키워드에 따라 적절한 DB 조회 함수를 매핑합니다.
        """
        conn = get_db_connection()
        results = {"employees": [], "sales": [], "leaves": []}
        
        try:
            # 1. 직원 관련 정보 (tool: get_employee, list_employees)
            all_employees = crud.list_employees(conn)
            target_ids = []
            
            # "영업팀" 등 부서명으로 검색 시 해당 부서 전원 포함
            for emp in all_employees:
                # 1) 이름이 질문에 포함 (예: "홍길동 전화번호") -> emp['name'] in query
                # 2) 질문이 이름에 포함 (예: "홍길") -> query in emp['name']
                # 3) 부서명이 질문에 포함 (예: "영업팀 인원") -> emp['dept'] in query
                if (query in emp['name'] or emp['name'] in query) or \
                   (query in emp['dept'] or emp['dept'] in query):
                    results["employees"].append(emp)
                    target_ids.append(emp['id'])
                    
            # 2. 휴가 관련 정보
            if "휴가" in query or "연차" in query or target_ids:
                for emp_id in target_ids:
                    leave = crud.get_leave_by_employee(conn, emp_id)
                    if leave:
                        emp_name = next((e['name'] for e in results["employees"] if e['id'] == emp_id), "Unknown")
                        results["leaves"].append({
                            "employee_name": emp_name, 
                            "total": leave['total'], 
                            "used": leave['used'], 
                            "remaining": leave['remaining']
                        })
            
            # 3. 매출 관련 정보
            if "매출" in query or "실적" in query:
                all_sales = crud.list_sales(conn, limit=100)
                for sale in all_sales:
                    # 부서명(dept)이 검색어에 있거나, 검색어가 내용(description)에 있는 경우
                    if (sale['dept'] and sale['dept'] in query) or \
                       (sale['description'] and query in sale['description']):
                        results["sales"].append(sale)
                        
        finally:
            conn.close()
        return results

# 싱글톤 인스턴스
db_service = DBService()
