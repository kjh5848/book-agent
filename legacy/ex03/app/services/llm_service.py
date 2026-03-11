import os
import json
from jinja2 import Environment, FileSystemLoader

class LLMService:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "ollama").lower()
        
        # 프로바이더별 기본 모델 설정
        default_model = "gpt-4o-mini" if self.provider == "openai" else "deepseek-r1:8b"
        
        # .env의 LLM_MODEL_NAME이 최우선 적용됩니다. 없으면 위 기본값을 사용합니다.
        self.model_name = os.getenv("LLM_MODEL_NAME", default_model)
        
        # Jinja2 템플릿 환경 설정
        base_dir = os.path.dirname(__file__)
        template_dir = os.path.join(base_dir, "prompts")
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        print(f"[LLMService] 초기화 중 (제공자: {self.provider}, 모델: {self.model_name})")
        
        # 엔진 초기화
        self._init_engine()

    def _init_engine(self):
        if self.provider == "openai":
            from langchain_openai import ChatOpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            # OpenAI 최신 Reasoning 모델(o1, o3, o4 등)은 temperature=1 고정 필수
            # gpt-4o 등 일반 모델은 0으로 설정하여 결정적 답변 유도
            temperature = 1 if self.model_name.startswith("o") else 0
            self.llm = ChatOpenAI(model=self.model_name, openai_api_key=api_key, temperature=temperature)
        else:
            # Ollama (Tool Calling 지원을 위해 ChatOllama 사용 권장)
            # langchain-ollama 패키지 사용 (최신)
            try:
                from langchain_ollama import ChatOllama
            except ImportError:
                print("[LLMService] 경고: langchain_ollama가 설치되지 않았습니다. pip install langchain-ollama를 권장합니다.")
                # 대체: 구 버전 import
                from langchain_community.chat_models import ChatOllama

            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            self.llm = ChatOllama(base_url=ollama_url, model=self.model_name)

    def render_prompt(self, template_name: str, **kwargs) -> str:
        """템플릿을 렌더링합니다."""
        template = self.jinja_env.get_template(template_name)
        return template.render(**kwargs)

    def invoke(self, prompt: str) -> str:
        """LLM을 직접 호출합니다."""
        try:
            # ChatOpenAI와 Ollama의 호출 방식 통일 (invoke 사용)
            if hasattr(self.llm, "invoke"):
                response = self.llm.invoke(prompt)
            else:
                response = self.llm(prompt)
                
            # ChatOpenAI 응답 처리 (객체로 올 경우 대비)
            if hasattr(response, "content"):
                response = response.content
            
            # 사고 과정(CoT) 제거 (DeepSeek-R1 등)
            if isinstance(response, str) and "<think>" in response and "</think>" in response:
                response = response.split("</think>")[-1].strip()
            return response
        except Exception as e:
            print(f"[LLMService] 호출 오류: {e}")
            return f"오류 발생: {str(e)}"

    def generate_answer(self, query: str, context: str) -> str:
        """템플릿을 사용하여 답변을 생성합니다."""
        rendered_prompt = self.render_prompt("answer_prompt.j2", query=query, context=context)
        return self.invoke(rendered_prompt)

    def classify_intent(self, query: str) -> dict:
        """라우터 템플릿을 사용하여 질문의 의도를 분석합니다."""
        rendered_prompt = self.render_prompt("router_prompt.j2", query=query)
        response = self.invoke(rendered_prompt)
        
        try:
            # JSON만 추출 (모델이 추가 설명을 붙일 경우 대비)
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            return {"route": "hybrid", "reason": "JSON 파싱 실패"}
        except:
            return {"route": "hybrid", "reason": "분석 오류 발생"}

# 싱글톤 인스턴스
llm_service = LLMService()
