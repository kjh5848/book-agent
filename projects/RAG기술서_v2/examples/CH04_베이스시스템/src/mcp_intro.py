"""
MCP(Model Context Protocol) 개념 소개 — 커넥트HR

MCP는 LLM이 외부 도구/데이터에 접근하는 표준 프로토콜입니다.
이 파일은 실제 MCP 서버 없이, 함수를 LangChain Tool로 래핑하여
MCP의 "도구 호출(Tool Call)" 패턴을 체험합니다.

핵심 흐름:
    사용자 질문 → LLM이 도구 선택 → 도구 실행 → 결과 반환 → 최종 답변

챕터 4.4: MCP(Model Context Protocol) 개념 소개
"""

import os
import json
import sys
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from langchain.tools import tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import Ollama

# 환경 변수 로딩
load_dotenv()


# ============================================================
# 상수
# ============================================================

DB_CONFIG: dict[str, Any] = {
    "host":     os.getenv("POSTGRES_HOST", "localhost"),
    "port":     int(os.getenv("POSTGRES_PORT", "5432")),
    "dbname":   os.getenv("POSTGRES_DB", "connecthr"),
    "user":     os.getenv("POSTGRES_USER", "admin"),
    "password": os.getenv("POSTGRES_PASSWORD", "password"),
}

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "deepseek-r1:1.5b")


# ============================================================
# MCP 스타일 도구 정의 (LangChain @tool 데코레이터)
# ============================================================
# MCP에서 각 도구는 이름(name), 설명(description), 입력 스키마를 가집니다.
# LangChain @tool 데코레이터가 이 역할을 합니다.

@tool
def get_employee_info(employee_name: str) -> str:
    """직원 이름으로 직원 정보를 조회합니다.

    Args:
        employee_name: 조회할 직원 이름 (예: '이서연')

    Returns:
        직원 정보 JSON 문자열. 직원이 없으면 오류 메시지.
    """
    # --- Input ---
    query = """
        SELECT id, name, department, hire_date::text, base_salary, email, is_active
        FROM employees
        WHERE name = %s
        LIMIT 1;
    """

    # --- Process ---
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (employee_name,))
            row = cur.fetchone()
        conn.close()
    except psycopg2.OperationalError:
        return json.dumps(
            {"오류": "데이터베이스 연결 실패. docker-compose up -d 를 먼저 실행하십시오."},
            ensure_ascii=False
        )

    if row is None:
        return json.dumps(
            {"오류": f"'{employee_name}' 직원을 찾을 수 없습니다."},
            ensure_ascii=False
        )

    # --- Output ---
    return json.dumps(dict(row), ensure_ascii=False, default=str)


@tool
def get_leave_balance(employee_name: str, year: int = 2025) -> str:
    """직원 이름과 연도로 연차 잔액을 조회합니다.

    Args:
        employee_name: 직원 이름 (예: '이서연')
        year:          조회 연도 (기본값: 2025)

    Returns:
        연차 잔액 JSON 문자열 (총일수, 사용일수, 잔여일수).
    """
    # --- Input ---
    query = """
        SELECT
            e.name             AS 이름,
            lb.year            AS 연도,
            lb.total_days      AS 총_연차,
            lb.used_days       AS 사용_연차,
            (lb.total_days - lb.used_days) AS 잔여_연차
        FROM leave_balance lb
        JOIN employees e ON e.id = lb.employee_id
        WHERE e.name = %s
          AND lb.year = %s;
    """

    # --- Process ---
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (employee_name, year))
            row = cur.fetchone()
        conn.close()
    except psycopg2.OperationalError:
        return json.dumps(
            {"오류": "데이터베이스 연결 실패. docker-compose up -d 를 먼저 실행하십시오."},
            ensure_ascii=False
        )

    if row is None:
        return json.dumps(
            {"오류": f"'{employee_name}'의 {year}년 연차 정보가 없습니다."},
            ensure_ascii=False
        )

    # --- Output ---
    return json.dumps(dict(row), ensure_ascii=False, default=str)


@tool
def get_department_sales(department: str, year: int = 2025) -> str:
    """부서명과 연도로 월별 매출 현황을 조회합니다.

    Args:
        department: 부서명 (예: '영업팀')
        year:       조회 연도 (기본값: 2025)

    Returns:
        월별 매출 리스트 JSON 문자열.
    """
    # --- Input ---
    query = """
        SELECT
            month       AS 월,
            revenue     AS 매출액,
            target      AS 목표액,
            CASE
                WHEN target IS NOT NULL AND target > 0
                THEN ROUND((revenue / target * 100)::numeric, 1)
                ELSE NULL
            END AS 달성률
        FROM sales_monthly
        WHERE department = %s
          AND year = %s
        ORDER BY month;
    """

    # --- Process ---
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (department, year))
            rows = cur.fetchall()
        conn.close()
    except psycopg2.OperationalError:
        return json.dumps(
            {"오류": "데이터베이스 연결 실패. docker-compose up -d 를 먼저 실행하십시오."},
            ensure_ascii=False
        )

    if not rows:
        return json.dumps(
            {"오류": f"'{department}'의 {year}년 매출 데이터가 없습니다."},
            ensure_ascii=False
        )

    # --- Output ---
    return json.dumps([dict(r) for r in rows], ensure_ascii=False, default=str)


# ============================================================
# 도구 목록 (MCP에서는 이 목록을 LLM에 전달)
# ============================================================

MCP_TOOLS = [get_employee_info, get_leave_balance, get_department_sales]


# ============================================================
# 데모: 도구 직접 호출 (MCP 패턴 체험)
# ============================================================

def demo_direct_tool_call() -> None:
    """MCP 도구를 직접 호출하는 데모를 실행합니다.

    LLM 없이 도구를 직접 호출하여 MCP 도구의 동작 방식을 확인합니다.
    """
    print("\n" + "=" * 60)
    print("  [데모 1] MCP 도구 직접 호출 (LLM 없이)")
    print("=" * 60)

    # --- Input ---
    test_cases = [
        ("이서연 직원 정보 조회",      get_employee_info,    {"employee_name": "이서연"}),
        ("박민준 2025년 연차 잔액",    get_leave_balance,    {"employee_name": "박민준", "year": 2025}),
        ("영업팀 2025년 매출 현황",    get_department_sales, {"department": "영업팀", "year": 2025}),
    ]

    # --- Process ---
    for title, tool_func, kwargs in test_cases:
        print(f"\n[질문] {title}")
        print(f"[도구] {tool_func.name}")
        print(f"[입력] {json.dumps(kwargs, ensure_ascii=False)}")

        result = tool_func.invoke(kwargs)
        parsed = json.loads(result)
        print(f"[결과] {json.dumps(parsed, ensure_ascii=False, indent=2)}")

    # --- Output ---
    print("\n[완료] 직접 도구 호출 데모가 종료되었습니다.")


def demo_agent_tool_call() -> None:
    """LangChain ReAct 에이전트를 통한 MCP 패턴 데모를 실행합니다.

    LLM이 질문을 분석하여 적절한 도구를 선택하고 호출하는
    MCP의 핵심 흐름을 체험합니다.

    Note:
        Ollama(deepseek-r1)가 실행 중이어야 합니다.
        Ollama가 없으면 이 데모를 건너뜁니다.
    """
    print("\n" + "=" * 60)
    print("  [데모 2] LangChain 에이전트를 통한 MCP 패턴")
    print("  (Ollama가 실행 중일 때만 동작합니다)")
    print("=" * 60)

    # --- Input ---
    questions = [
        "이서연 씨의 2025년 잔여 연차가 며칠인지 알려줘.",
        "영업팀의 2025년 1월 매출이 목표를 달성했나요?",
    ]

    # --- Process ---
    # LLM 초기화 시도
    try:
        llm = Ollama(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)
        # 연결 테스트
        llm.invoke("안녕")
    except Exception as e:
        print(f"[건너뜀] Ollama에 연결할 수 없습니다: {e}")
        print("         Ollama를 실행한 뒤 다시 시도하십시오.")
        return

    # ReAct 프롬프트 구성
    react_prompt = PromptTemplate.from_template(
        """당신은 커넥트HR 사내 데이터를 조회하는 AI 비서입니다.
주어진 도구를 활용하여 사용자의 질문에 정확히 답하십시오.

사용 가능한 도구:
{tools}

도구 이름 목록:
{tool_names}

질문: {input}
{agent_scratchpad}"""
    )

    agent = create_react_agent(llm, MCP_TOOLS, react_prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=MCP_TOOLS,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True,
    )

    for question in questions:
        print(f"\n[질문] {question}")
        try:
            result = executor.invoke({"input": question})
            print(f"[답변] {result.get('output', '응답 없음')}")
        except Exception as e:
            print(f"[오류] 에이전트 실행 중 문제가 발생했습니다: {e}")

    # --- Output ---
    print("\n[완료] 에이전트 데모가 종료되었습니다.")


# ============================================================
# 진입점
# ============================================================

def main() -> None:
    """MCP 개념 소개 데모 메인 함수.

    1. 도구 직접 호출 (DB 연결만 필요)
    2. LangChain 에이전트를 통한 MCP 패턴 (Ollama 필요)
    """
    print("커넥트HR MCP(Model Context Protocol) 개념 데모")
    print()
    print("MCP 핵심 흐름:")
    print("  사용자 질문 → LLM이 도구 선택 → 도구 실행 → 결과 반환 → 최종 답변")
    print()
    print(f"등록된 MCP 도구 목록 ({len(MCP_TOOLS)}개):")
    for t in MCP_TOOLS:
        print(f"  - {t.name}: {t.description[:50]}...")

    # 데모 1: 도구 직접 호출
    demo_direct_tool_call()

    # 데모 2: 에이전트 통한 MCP 패턴 (Ollama 필요)
    demo_agent_tool_call()


if __name__ == "__main__":
    main()
