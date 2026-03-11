from typing import Any, Dict, List
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.services.llm_service import llm_service
from app.tools import list_employees, get_leave_balance, get_sales_sum, search_documents

class AgentService:
    def __init__(self):
        print("[AgentService] 초기화 중...", flush=True)
        # 1. 도구 목록 정의
        self.tools = [list_employees, get_leave_balance, get_sales_sum, search_documents]
        
        # 2. LLM에 도구 바인딩 (Tool Calling)
        # llm_service.llm은 이미 ChatOpenAI 또는 호환 객체여야 함
        if not llm_service.llm:
            print("[AgentService] 오류: LLM 서비스가 초기화되지 않았습니다.")
            return

        # 3. 프롬프트 정의
        prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "당신은 메타코딩의 유능한 AI 비서입니다. "
             "주어진 도구(Tools)를 활용하여 사용자의 질문에 정확하게 답변하세요. "
             "도구 사용이 불필요한 일상적인 대화에는 친절하게 응대하세요."
             "\n\n"
             "[도구 사용 가이드]\n"
             "- 직원 정보 조회: list_employees (부서명 필터 가능)\n"
             "- 휴가 잔여일: get_leave_balance (직원 이름 필수)\n"
             "- 매출 통계: get_sales_sum (부서명 옵션)\n"
             "- 사내 규정/문서: search_documents (키워드/문장 검색)\n"
             "\n"
             "질문에 답변하기 위해 필요한 도구를 스스로 판단하여 호출하세요."
            ),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        # 4. 에이전트 생성 (Tool Calling Agent)
        try:
            agent = create_tool_calling_agent(llm_service.llm, self.tools, prompt)
            
            # 5. 실행기(Executor) 생성
            self.agent_executor = AgentExecutor(
                agent=agent, 
                tools=self.tools, 
                verbose=True,      # 터미널에 중간 과정(생각) 출력
                handle_parsing_errors=True, # 파싱 에러 자동 처리
                return_intermediate_steps=True # 중간 과정(Tool 호출 기록) 반환
            )
            print("[AgentService] 에이전트 생성 완료.")
        except Exception as e:
            print(f"[AgentService] 초기화 중 오류: {e}")
            self.agent_executor = None

    def run_agent(self, query: str) -> Dict[str, Any]:
        """
        에이전트 실행 (질문 -> 도구 선택 -> 실행 -> 답변)
        반환값: {"output": 답변, "intermediate_steps": [(AgentAction, tool_output), ...]}
        """
        if not self.agent_executor:
            return {"output": "죄송합니다. 에이전트 서비스가 현재 이용 불가능합니다.", "intermediate_steps": []}
            
        try:
            # invoke 호출
            result = self.agent_executor.invoke({"input": query})
            return result
        except Exception as e:
            print(f"[AgentService] 실행 중 오류: {e}")
            return {"output": f"처리 중 오류가 발생했습니다: {str(e)}", "intermediate_steps": []}

# 싱글톤 인스턴스
agent_service = AgentService()
