from typing import Dict, Any
from .llm_service import llm_service
from .vector_service import vector_service
from .db_service import db_service

from .agent_service import agent_service

class QAService:
    """
    하이브리드 Q&A 오케스트레이터 서비스.
    개별 전문 서비스(LLM, Vector, DB)를 조합하여 통합 검색 및 답변을 제공합니다.
    (v2: AgentService를 통한 Tool Calling 지원 추가)
    """
    def __init__(self):
        print("[QAService] 오케스트레이터 초기화 완료.")

    def hybrid_search(self, query: str) -> Dict[str, Any]:
        """지능형 라우팅을 적용한 하이브리드 검색 (v1: 수동 라우팅)"""
        # 1. 질문 의도 분석 (Router 호출)
        analysis = llm_service.classify_intent(query)
        route = analysis.get("route", "hybrid")
        print(f"[QAService] 라우팅 결정: {route} (사유: {analysis.get('reason')})")
        
        unstructured = []
        structured = {"employees": [], "sales": [], "leaves": []}
        
        # 2. 분석된 경로에 따라 선택적 검색 수행
        if route in ["unstructured", "hybrid"]:
            unstructured = vector_service.search_unstructured(query)
            
        if route in ["structured", "hybrid"]:
            structured = db_service.search_structured(query)
        
        return {
            "query": query,
            "unstructured": unstructured,
            "structured": structured,
            "route": route
        }

    def get_ai_answer(self, query: str, search_results: Dict[str, Any]) -> str:
        """검색 결과를 바탕으로 AI 답변 생성 및 컨텍스트 구성 (v1)"""
        
        # 1. 컨텍스트 구성
        context_parts = []
        
        # 비정형 데이터 추가
        if search_results["unstructured"]:
            context_parts.append("[사내 문서 내용]")
            for doc in search_results["unstructured"]:
                context_parts.append(f"- {doc['content']} (출처: {doc['source']})")
        
        # 정형 데이터 추가
        structured = search_results["structured"]
        if structured["employees"] or structured["sales"] or structured["leaves"]:
            context_parts.append("\n[시스템 데이터베이스 정보]")
            
            if structured["employees"]:
                count = len(structured["employees"])
                emp_list = ", ".join([f"{e['name']}({e['dept']})" for e in structured["employees"][:20]]) # 최대 20명까지만 나열
                if count > 20:
                    emp_list += f" 외 {count - 20}명"
                context_parts.append(f"- 검색된 직원 수: 총 {count}명")
                context_parts.append(f"- 직원 목록: {emp_list}")
                
            if structured["leaves"]:
                context_parts.append("- 휴가 잔여: " + ", ".join([f"{l['employee_name']}: {l['remaining']}일" for l in structured["leaves"]]))
                
            if structured["sales"]:
                sales = structured["sales"]
                total_amount = sum(s['amount'] for s in sales)
                context_parts.append(f"- 검색된 매출 건수: 총 {len(sales)}건")
                context_parts.append(f"- 매출 총합계: {total_amount:,}원")
                context_parts.append("- 매출 상세 내역:")
                for s in sales[:10]: # 상세 내역은 10건까지만
                    context_parts.append(f"  * {s['date']} {s['dept']}: {s['amount']:,}원 ({s['description'] or '설명 없음'})")
                if len(sales) > 10:
                    context_parts.append(f"  ...외 {len(sales) - 10}건 생략")
 
        context_text = "\n".join(context_parts)
        
        # 2. 템플릿 기반 답변 생성 호출
        return llm_service.generate_answer(query, context_text)

    def run_agent_mode(self, query: str) -> Dict[str, Any]:
        """
        MCP 에이전트 모드 실행 (v2: Tool Calling Agent)
        LangChain Agent가 스스로 도구를 선택/실행하여 답변합니다.
        
        반환값:
        {
            "answer": str,
            "unstructured": List[Dict],
            "structured": Dict[str, List]
        }
        """
        print(f"[QAService] 에이전트 모드 실행: {query}")
        
        # 1. 에이전트 실행
        result = agent_service.run_agent(query)
        answer = result.get("output", "답변을 생성할 수 없습니다.")
        steps = result.get("intermediate_steps", [])
        
        # 2. 근거 데이터 파싱
        unstructured = []
        structured = {"employees": [], "sales": [], "leaves": []}
        
        for action, observation in steps:
            tool_name = action.tool
            print(f"[QAService] 도구 사용 감지: {tool_name}")
            
            if tool_name == "search_documents":
                # 문서 검색 결과 (observation은 보통 문자열 형태의 리스트)
                # 실제로는 문자열로 반환되므로, 가공이 필요할 수 있음
                # 여기서는 원본 내용을 그대로 'content'에 담음
                if isinstance(observation, list):
                    unstructured.extend(observation)
                else:
                    unstructured.append({"content": str(observation), "source": "Agent Search"})
                    
            elif tool_name == "list_employees":
                if isinstance(observation, list):
                    structured["employees"].extend(observation)
                elif isinstance(observation, str) and "[" in observation:
                    # 문자열로 된 리스트 파싱 시도 (간단히 처리)
                    try:
                        import ast
                        data = ast.literal_eval(observation)
                        if isinstance(data, list):
                            structured["employees"].extend(data)
                    except:
                        pass
                        
            elif tool_name == "get_leave_balance":
                # 단일 딕셔너리 또는 문자열
                if isinstance(observation, dict):
                    structured["leaves"].append(observation)
                elif isinstance(observation, str) and "{" in observation:
                    try:
                        import ast
                        data = ast.literal_eval(observation)
                        if isinstance(data, dict):
                            structured["leaves"].append(data)
                    except:
                        pass
                        
            elif tool_name == "get_sales_sum":
                # 매출 정보 (보통 문자열이나 딕셔너리로 옴)
                if isinstance(observation, dict):
                    structured["sales"].append(observation)
                elif isinstance(observation, list):
                    structured["sales"].extend(observation)
                elif isinstance(observation, str):
                   # 문자열 메시지인 경우 임시 처리
                   structured["sales"].append({"description": str(observation), "amount": 0, "date": "-", "dept": "-"})

        return {
            "answer": answer,
            "unstructured": unstructured,
            "structured": structured
        }

# 싱글톤 인스턴스
qa_service = QAService()
