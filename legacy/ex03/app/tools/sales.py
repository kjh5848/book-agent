from langchain_core.tools import tool
from typing import List, Dict, Any, Union
from database import get_db_connection, crud

@tool
def get_sales_sum(dept: str = None) -> Union[Dict[str, Any], str]:
    """
    부서별 매출 합계 및 실적 정보를 조회합니다.
    
    Args:
        dept (str, optional): 조회할 부서명 (예: "영업팀"). 
                            없으면 전체 부서 매출을 합산하거나 리스트를 반환할 수 있으나, 
                            현재는 특정 부서 또는 전체 목록을 제공합니다.
    """
    conn = get_db_connection()
    try:
        sales = crud.list_sales(conn, limit=100)
        
        target_sales = sales
        if dept:
            target_sales = [s for s in sales if dept in s['dept']]
            
        if not target_sales:
            return f"{dept if dept else '전체'} 매출 데이터가 없습니다."
            
        total_amount = sum(s['amount'] for s in target_sales)
        
        return {
            "dept": dept if dept else "전체",
            "total_amount": total_amount,
            "count": len(target_sales),
            # 상세 내역은 너무 길 수 있으므로 상위 5개만 예시로 포함
            "recent_records": target_sales[:5]
        }
    finally:
        conn.close()
