from langchain_core.tools import tool
from typing import List, Dict, Any
from app.services.vector_service import vector_service

@tool
def search_documents(query: str) -> List[Dict[str, Any]]:
    """
    사내 규정, 가이드라인, 정책 등 비정형 문서 내용을 검색합니다.
    휴가 규정, 보안 수칙, 업무 가이드 등을 찾을 때 사용합니다.
    
    Args:
        query (str): 검색할 질문 또는 키워드
    """
    # VectorService의 기존 메서드 재사용
    results = vector_service.search_unstructured(query, k=3)
    
    # 결과 포맷팅 (Agent가 이해하기 쉽도록)
    formatted = []
    for doc in results:
        formatted.append({
            "content": doc['content'],
            "source": doc['source'],
            "score": doc['score']
        })
        
    return formatted
