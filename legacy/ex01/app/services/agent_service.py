from typing import Any, Dict, List
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.services.llm_service import llm_service
from app.tools import search_documents

class AgentService:
    def __init__(self):
        print("[AgentService] 초기화 중 (Phase 1: Pure RAG)...", flush=True)
        # 1. 도구 목록 정의 (문서 검색만 허용)
        self.tools = [search_documents]
        
        # 2. LLM에 도구 바인딩 (Tool Calling)
        if not llm_service.llm:
            print("[AgentService] 오류: LLM 서비스가 초기화되지 않았습니다.")
            return

        # 3. 프롬프트 정의
        prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "당신은 메타코딩의 사내 규정 안내 AI 비서입니다. "
             "오직 사내 문서 검색 도구(search_documents)를 활용하여 사용자의 질문에 답변하세요. "
             "문서에 없는 개인 정보(휴가 잔여량 등)나 실시간 매출 통계에 대해서는 '문서에서 찾을 수 없다'고 답변하거나, "
             "나중에 시스템이 업데이트되면 연동될 예정이라고 안내하세요."
             "\n\n"
             "[도구 사용 가이드]\n"
             "- 사내 규정/문서: search_documents (키워드/문장 검색)\n"
             "\n"
             "직접적인 DB 조회 로직이 없으므로, 모든 정보는 제공된 문서 검색 도구를 통해서만 얻어야 합니다."
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
