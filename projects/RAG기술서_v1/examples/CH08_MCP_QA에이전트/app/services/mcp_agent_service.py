"""
MCP Client + LangChain ReAct Agent 서비스.

FastMCP 서버를 stdio 서브프로세스로 실행하고,
ClientSession을 통해 DB 도구를 수집한 후
LangChain ReAct Agent로 질문에 답변합니다.
"""

import asyncio
import json
import os
import sys
from typing import Any

from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate

from app.services.llm_service import llm_service

# MCP 서버 경로
_PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
_MCP_SERVER_PATH = os.path.join(_PROJECT_ROOT, "mcp", "mcp_server.py")

# ReAct 프롬프트 템플릿
REACT_PROMPT = PromptTemplate.from_template(
    """다음 도구를 활용하여 질문에 답변하세요.

사용 가능한 도구:
{tools}

답변 형식을 반드시 준수하세요:
Question: 입력된 질문
Thought: 다음에 무엇을 해야 할지 생각합니다
Action: 사용할 도구 이름 [{tool_names}] 중 하나
Action Input: 도구에 전달할 JSON 입력
Observation: 도구 실행 결과
...(Thought/Action/Action Input/Observation을 필요한 만큼 반복)
Thought: 이제 최종 답변을 알았습니다
Final Answer: 한국어로 작성한 최종 답변

시작하세요!

Question: {input}
Thought:{agent_scratchpad}"""
)


class MCPToolWrapper:
    """MCP 도구를 LangChain Tool로 변환하는 래퍼.

    MCP ClientSession의 tool_info를 받아서 LangChain이 인식할 수 있는
    Tool 객체로 변환합니다.

    Attributes:
        session: MCP ClientSession 객체.
        tool_name: MCP 도구명.
        tool_description: 도구 설명 문자열.
    """

    def __init__(self, session: Any, tool_info: Any) -> None:
        """
        MCP 세션과 도구 정보를 저장합니다.

        Args:
            session: MCP ClientSession 객체.
            tool_info: MCP 서버에서 반환된 도구 정보 객체.
        """
        # --- Input ---
        self.session = session
        self.tool_name = tool_info.name
        self.tool_description = tool_info.description or f"{tool_info.name} 도구"
        # --- Output ---

    async def _call(self, **kwargs: Any) -> str:
        """
        MCP 도구를 비동기로 호출합니다.

        Args:
            **kwargs: 도구에 전달할 인수.

        Returns:
            str: 도구 실행 결과 문자열 (JSON 또는 텍스트).
        """
        # --- Input ---
        # --- Process ---
        try:
            result = await self.session.call_tool(self.tool_name, arguments=kwargs)
            content = result.content
            if isinstance(content, list) and content:
                text = content[0].text if hasattr(content[0], "text") else str(content[0])
            else:
                text = str(content)
            # --- Output ---
            return text
        except Exception as exc:
            return f"도구 실행 오류: {exc}"

    def _sync_call(self, tool_input: str) -> str:
        """
        LangChain Tool에서 동기 호출하기 위한 래퍼입니다.

        JSON 문자열 또는 일반 문자열로 받은 입력을 파싱하여
        비동기 _call을 동기 방식으로 실행합니다.

        Args:
            tool_input: JSON 형태의 도구 입력 문자열.

        Returns:
            str: 도구 실행 결과 문자열.
        """
        # --- Input ---
        try:
            kwargs = json.loads(tool_input) if tool_input.strip() else {}
        except (json.JSONDecodeError, ValueError):
            kwargs = {"input": tool_input}

        # --- Process ---
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, self._call(**kwargs))
                    result = future.result(timeout=30)
            else:
                result = loop.run_until_complete(self._call(**kwargs))
        except Exception as exc:
            result = f"비동기 실행 오류: {exc}"

        # --- Output ---
        return result

    def to_langchain_tool(self) -> Tool:
        """
        LangChain Tool 객체로 변환합니다.

        Returns:
            Tool: LangChain에서 사용 가능한 Tool 객체.
        """
        # --- Input ---
        # --- Process ---
        # --- Output ---
        return Tool(
            name=self.tool_name,
            description=self.tool_description,
            func=self._sync_call,
        )


class MCPAgentService:
    """MCP Client와 LangChain ReAct Agent를 결합한 서비스.

    FastMCP 서버를 stdio 서브프로세스로 실행하고,
    등록된 DB 도구를 활용하여 자연어 질문에 답변합니다.
    """

    def _collect_tools_sync(self) -> list[Tool]:
        """
        MCP 서버에서 도구 목록을 동기 방식으로 수집합니다.

        Returns:
            list[Tool]: LangChain Tool 객체 리스트.
        """
        # --- Input ---
        # --- Process ---
        async def _async_collect() -> list[Tool]:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client

            server_params = StdioServerParameters(
                command=sys.executable,
                args=[_MCP_SERVER_PATH],
                env=None,
            )

            tools: list[Tool] = []
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools_response = await session.list_tools()
                    for tool_info in tools_response.tools:
                        wrapper = MCPToolWrapper(session, tool_info)
                        tools.append(wrapper.to_langchain_tool())
            return tools

        return asyncio.run(_async_collect())

    def run_agent(self, query: str) -> dict:
        """
        MCP Agent를 실행하여 질문에 답변합니다.

        FastMCP 서버를 stdio 서브프로세스로 실행한 후
        ClientSession.list_tools()로 도구를 수집하고,
        LangChain ReAct Agent로 질문에 답변합니다.

        Args:
            query: 사용자 질의 문자열.

        Returns:
            dict: {
                "answer": 최종 답변 문자열,
                "steps": [{"tool": 도구명, "input": 입력값, "output": 결과값}]
            }
        """
        # --- Input ---
        steps: list[dict] = []
        answer = ""

        # --- Process ---
        try:
            async def _async_run() -> dict:
                from mcp import ClientSession, StdioServerParameters
                from mcp.client.stdio import stdio_client

                server_params = StdioServerParameters(
                    command=sys.executable,
                    args=[_MCP_SERVER_PATH],
                    env=None,
                )

                async with stdio_client(server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        tools_response = await session.list_tools()

                        langchain_tools: list[Tool] = []
                        wrappers: list[MCPToolWrapper] = []
                        for tool_info in tools_response.tools:
                            wrapper = MCPToolWrapper(session, tool_info)
                            wrappers.append(wrapper)
                            langchain_tools.append(wrapper.to_langchain_tool())

                        agent = create_react_agent(
                            llm=llm_service.llm,
                            tools=langchain_tools,
                            prompt=REACT_PROMPT,
                        )

                        executor = AgentExecutor(
                            agent=agent,
                            tools=langchain_tools,
                            verbose=True,
                            max_iterations=8,
                            handle_parsing_errors=True,
                            return_intermediate_steps=True,
                        )

                        result = executor.invoke({"input": query})
                        final_answer = result.get("output", "답변을 생성하지 못했습니다.")

                        agent_steps: list[dict] = []
                        for action, observation in result.get("intermediate_steps", []):
                            agent_steps.append(
                                {
                                    "tool": action.tool,
                                    "input": action.tool_input,
                                    "output": str(observation),
                                }
                            )

                        return {"answer": final_answer, "steps": agent_steps}

            result_dict = asyncio.run(_async_run())
            answer = result_dict.get("answer", "")
            steps = result_dict.get("steps", [])

        except Exception as exc:
            answer = f"MCP Agent 실행 중 오류가 발생했습니다: {exc}"

        # --- Output ---
        return {"answer": answer, "steps": steps}


# 싱글톤 인스턴스
mcp_agent_service = MCPAgentService()
