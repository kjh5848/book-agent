# 환경 세팅 가이드 (CH02)
# pip install ollama langchain-community

import ollama

def step1_run_basic_llm() -> str:
    """
    Step 1: 기본 LLM(DeepSeek R1)을 로컬에서 호출해 테스트합니다.
    """
    print("🤖: DeepSeek R1 로컬 모델을 호출합니다...")
    response = ollama.chat(model='deepseek-r1:1.5b', messages=[
        {
            'role': 'user',
            'content': '우리 회사(안티그래비티)의 올해 연차 규정에 대해 알려줘.',
        },
    ])
    return response['message']['content']

def step2_run_mock_rag() -> str:
    """
    Step 2: 간단한 RAG 구조(지식 주입)를 흉내 내어 모델에 컨텍스트를 제공합니다.
    """
    print("🤖: 가짜 사내 문서를 주입하여 답변을 생성합니다...")
    # 가상의 사내 규정 내용 (실제로는 VectorDB에서 가져올 내용)
    company_context = "안티그래비티의 올해 연차는 기본 15일이며, 여름 휴가 3일이 별도로 부여됩니다."
    
    question = "우리 회사(안티그래비티)의 올해 연차 규정에 대해 알려줘."
    
    # 프롬프트에 컨텍스트를 함께 넣어서 질문
    prompt = f"""
    아래의 [사내 문서]를 바탕으로 질문에 답해줘. 없는 내용이면 모른다고 해.
    
    [사내 문서]
    {company_context}
    
    [질문]
    {question}
    """
    
    response = ollama.chat(model='deepseek-r1:1.5b', messages=[
        {
            'role': 'user',
            'content': prompt,
        },
    ])
    return response['message']['content']

if __name__ == "__main__":
    print("=== [테스트 1] 기본 LLM의 답변 (할루시네이션 확인) ===")
    print(step1_run_basic_llm())
    print("\n" + "="*50 + "\n")
    print("=== [테스트 2] 문맥이 주입된 RAG 답변 ===")
    print(step2_run_mock_rag())
