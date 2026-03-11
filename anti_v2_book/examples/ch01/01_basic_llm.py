# pip install -r requirements.txt
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
import time

def step1_init_model() -> ChatOllama:
    """Ollama 로컬 모델 초기화"""
    print("[1] 로컬 DeepSeek R1 모델을 준비합니다...")
    # Ollama가 로컬(기본 11434 포트)에서 돌고 있어야 합니다.
    chat_model = ChatOllama(model="deepseek-r1:latest", temperature=0.6)
    return chat_model

def step2_ask_question(chat_model: ChatOllama, user_question: str) -> str:
    """질문 전달 및 답변 받기"""
    print(f"\n[2] 모델에게 질문을 던집니다: '{user_question}'")
    
    messages = [
        SystemMessage(content="당신은 친절한 인공지능 어시스턴트입니다. 한국어로 대답하세요."),
        HumanMessage(content=user_question)
    ]
    
    print("답변을 기다리는 중... (로컬 사양에 따라 시간이 걸릴 수 있습니다.)\n")
    start_time = time.time()
    
    try:
        response = chat_model.invoke(messages)
        end_time = time.time()
        print(f"(응답 시간: {end_time - start_time:.2f}초)")
        return response.content
    except Exception as e:
        return f"요청 중 에러가 발생했습니다: {e}\n(Ollama가 켜져 있는지 확인하세요!)"

def step3_print_result(answer: str):
    """결과 출력"""
    print("\n[3] 모델의 답변:")
    print("-" * 50)
    print(answer)
    print("-" * 50)

if __name__ == "__main__":
    print("=== [기초 RAG 실습] 로컬 LLM 단독 구동 테스트 ===")
    
    # IPO 패턴으로 함수 호출
    model = step1_init_model()
    
    # 의도적으로 모델이 모를 만한 사내 정보를 질문 (할루시네이션 유도)
    question = "우리 회사 '안티그래비티 주식회사'의 2024년도 하계 휴가 지원금 정책에 대해 알려줘."
    
    answer_text = step2_ask_question(model, question)
    step3_print_result(answer_text)
    
    print("\n결론: 모델은 엄청난 그럴싸한 거짓말(Hallucination)을 하거나 모른다고 답합니다.")
    print("이것이 사내 문서 기반의 RAG가 필요한 이유입니다!")
