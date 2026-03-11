"""
LLM 초기화 서비스.

환경 변수 LLM_PROVIDER(ollama|openai)와 LLM_MODEL_NAME으로 LLM을 선택합니다.
Jinja2 프롬프트 템플릿 렌더링을 담당하며 답변 생성과 인텐트 분류를 제공합니다.

사용 모델:
    - ollama : ChatOllama (DeepSeek-R1, Llama3 등 로컬 모델)
    - openai : ChatOpenAI (gpt-4o, gpt-4o-mini 등)
"""

import json
import os

from jinja2 import Environment, FileSystemLoader


class LLMService:
    """LLM 초기화 및 프롬프트 렌더링 서비스."""

    def __init__(self) -> None:
        """
        환경 변수를 읽어 LLM 제공자와 모델을 초기화합니다.

        환경 변수:
            LLM_PROVIDER   : "ollama" 또는 "openai" (기본값: "ollama")
            LLM_MODEL_NAME : 모델 이름 (기본값: "deepseek-r1:1.5b")
            OLLAMA_BASE_URL: Ollama 서버 주소 (기본값: "http://localhost:11434")
            OPENAI_API_KEY : OpenAI API 키 (openai 사용 시 필수)

        Jinja2 Environment는 app/prompts/ 디렉토리를 로더로 사용합니다.
        """
        self.provider = os.getenv("LLM_PROVIDER", "ollama").lower()

        default_model = "gpt-4o-mini" if self.provider == "openai" else "deepseek-r1:1.5b"
        self.model_name = os.getenv("LLM_MODEL_NAME", default_model)

        # Jinja2 템플릿 환경 — app/prompts/ 디렉토리 기준
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_dir = os.path.join(base_dir, "prompts")
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

        print(f"[LLMService] 초기화 중 (제공자: {self.provider}, 모델: {self.model_name})")
        self._init_engine()

    def _init_engine(self) -> None:
        """
        LLM 제공자에 따라 ChatOllama 또는 ChatOpenAI 엔진을 초기화합니다.

        Raises:
            ImportError: 필요한 패키지가 설치되지 않은 경우.
            ValueError: OPENAI_API_KEY가 설정되지 않은 경우.
        """
        if self.provider == "openai":
            from langchain_openai import ChatOpenAI

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "OPENAI_API_KEY 환경 변수가 설정되지 않았습니다. "
                    ".env 파일에 OPENAI_API_KEY=sk-proj-... 를 추가하십시오."
                )
            # OpenAI Reasoning 모델(o1, o3 등)은 temperature=1 고정 필수
            temperature = 1 if self.model_name.startswith("o") else 0
            self.llm = ChatOpenAI(
                model=self.model_name,
                openai_api_key=api_key,
                temperature=temperature,
            )
        else:
            # Ollama 제공자 (기본값)
            try:
                from langchain_ollama import ChatOllama
            except ImportError as exc:
                raise ImportError(
                    "langchain-ollama 패키지가 설치되지 않았습니다. "
                    "pip install langchain-ollama 를 실행하십시오."
                ) from exc

            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            self.llm = ChatOllama(base_url=ollama_url, model=self.model_name)

    def render_prompt(self, template_name: str, **kwargs: str) -> str:
        """
        Jinja2 템플릿을 렌더링하여 프롬프트 문자열을 반환합니다.

        Args:
            template_name: 템플릿 파일명 (예: "router_prompt.j2").
            **kwargs: 템플릿에 전달할 변수 (예: query="질문 내용").

        Returns:
            str: 렌더링된 프롬프트 문자열.
        """
        template = self.jinja_env.get_template(template_name)
        return template.render(**kwargs)

    def invoke(self, prompt: str) -> str:
        """
        LLM을 호출하고 응답 문자열을 반환합니다.

        ChatOllama와 ChatOpenAI 모두 .invoke() 메서드로 통일합니다.
        DeepSeek-R1 등의 <think>...</think> 사고 과정 태그를 자동으로 제거합니다.

        Args:
            prompt: LLM에 전달할 프롬프트 문자열.

        Returns:
            str: LLM 응답 텍스트 (사고 과정 제거 후).
        """
        try:
            response = self.llm.invoke(prompt)

            # 응답 객체에서 텍스트 추출 (ChatOpenAI, ChatOllama 공통)
            if hasattr(response, "content"):
                response = response.content

            # DeepSeek-R1 등의 <think>...</think> 사고 과정 제거
            if isinstance(response, str) and "<think>" in response and "</think>" in response:
                response = response.split("</think>")[-1].strip()

            return str(response)
        except Exception as exc:
            print(f"[LLMService] LLM 호출 오류: {exc}")
            return f"LLM 호출 중 오류가 발생했습니다: {str(exc)}"

    def generate_answer(self, query: str, context: str) -> str:
        """
        answer_prompt.j2 템플릿을 사용하여 최종 답변을 생성합니다.

        Args:
            query: 사용자 질문 문자열.
            context: 검색 결과로 구성된 컨텍스트 문자열.

        Returns:
            str: LLM이 생성한 답변 문자열.
        """
        rendered_prompt = self.render_prompt("answer_prompt.j2", query=query, context=context)
        return self.invoke(rendered_prompt)

    def classify_intent(self, query: str) -> dict:
        """
        router_prompt.j2 템플릿을 사용하여 질문의 인텐트를 분류합니다.

        LLM 응답에서 JSON을 추출하여 라우팅 전략을 반환합니다.
        JSON 파싱 실패 시 기본값 "hybrid"로 대체합니다.

        Args:
            query: 사용자 질문 문자열.

        Returns:
            dict: {
                "route": "unstructured" | "hybrid",
                "reason": 분류 사유 문자열
            }
        """
        rendered_prompt = self.render_prompt("router_prompt.j2", query=query)
        response = self.invoke(rendered_prompt)

        try:
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            return {"route": "hybrid", "reason": "JSON 파싱 실패 — hybrid로 대체"}
        except Exception:
            return {"route": "hybrid", "reason": "인텐트 분석 오류 — hybrid로 대체"}


# 싱글톤 인스턴스
llm_service = LLMService()
