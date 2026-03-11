"""
MCP Agent: MCP 서버를 통해 사내 DB를 자연어로 조회하는 AI 에이전트
LangChain + MCP Client를 사용하여 터미널에서 대화형으로 동작합니다.
"""
import asyncio
import os
import sys
import json
from typing import Any

from dotenv import load_dotenv

# 프로젝트 루트를 경로에 추가
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

load_dotenv()

# MCP 및 LangChain 라이브러리 임포트
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_core.tools import Tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate

def get_llm():
    """환경변수에 따라 LLM 인스턴스를 반환합니다."""
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    model_name = os.getenv("LLM_MODEL_NAME", "deepseek-r1:8b")

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=model_name, temperature=0)
    else:
        from langchain_ollama import ChatOllama
        return ChatOllama(model=model_name, base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"), temperature=0)

class MCPToolWrapper:
    """MCP 도구를 LangChain Tool로 변환하는 래퍼"""
    def __init__(self, session: ClientSession, tool_info):
        self.session = session
        self.name = tool_info.name
        self.description = tool_info.description or f"MCP Tool: {tool_info.name}"
        self.input_schema = tool_info.inputSchema

    async def _call(self, **kwargs) -> str:
        result = await self.session.call_tool(self.name, kwargs)
        return "\n".join([c.text for c in result.content if hasattr(c, "text")]) if result.content else str(result.content)

    def to_langchain_tool(self) -> Tool:
        def sync_call(input_str: str) -> str:
            try:
                params = json.loads(input_str)
            except:
                params = {"query": input_str}
            return asyncio.run(self._call(**params))

        return Tool(name=self.name, description=self.description, func=sync_call)

REACT_PROMPT = PromptTemplate.from_template("""다음은 AI 비서가 사용할 수 있는 도구 목록입니다:
{tools}

다음 형식을 사용하여 질문에 답변하세요:
Question: 사용자의 질문
Thought: 질문을 해결하기 위한 생각
Action: 사용할 도구 이름 (중 하나: [{tool_names}])
Action Input: 도구에 전달할 JSON 형식의 입력
Observation: 도구 실행 결과
... (생각/동기/관찰 반복)
Thought: 이제 답변을 알 수 있습니다
Final Answer: 사용자의 질문에 대한 최종 답변 (한국어로 작성)

질문: {input}
Thought:{agent_scratchpad}""")

async def run_agent():
    mcp_server_path = os.path.join(PROJECT_ROOT, "mcp", "mcp_server.py")
    server_params = StdioServerParameters(command=sys.executable, args=[mcp_server_path])

    print("🤖 MCP 에이전트 시작...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            lc_tools = [MCPToolWrapper(session, t).to_langchain_tool() for t in tools_result.tools]

            llm = get_llm()
            agent = create_react_agent(llm, lc_tools, REACT_PROMPT)
            agent_executor = AgentExecutor(agent=agent, tools=lc_tools, verbose=True, handle_parsing_errors=True)

            print("✅ 연결 완료! 질문을 입력하세요 (종료: exit)")
            while True:
                user_input = input("\n🧑 질문: ").strip()
                if user_input.lower() in ("exit", "quit"): break
                result = await agent_executor.ainvoke({"input": user_input})
                print(f"\n🤖 답변: {result['output']}")

if __name__ == "__main__":
    asyncio.run(run_agent())
