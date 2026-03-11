# 환경 세팅 가이드 (CH07)
# pip install langchain langchain-community

from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# ch06_vector_db에서 작성한 함수를 재사용 (의존성 포함)
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ch06_vector_db.vector_search import step1_get_embedding_model, step2_init_vector_db

# --- [1. LLM 및 검색기(Retriever) 설정] ---
def step1_setup_components():
    """LLM과 VectorDB를 이용한 Retriever를 초기화합니다."""
    print("⚙️: RAG 컴포넌트들을 초기화합니다...")
    
    # 로컬 Ollama 모델 연결
    llm = Ollama(model="deepseek-r1:1.5b")
    
    # CH06에서 만든 VectorDB 로드
    collection = step2_init_vector_db()
    embed_model = step1_get_embedding_model()
    
    return llm, collection, embed_model

# --- [2. Retriever 래핑 및 프롬프트 정의] ---
def step2_create_rag_chain(llm, collection, embed_model):
    """LangChain을 활용하여 검색(Retrieval) + 생성(Generation) 체인을 엮습니다."""
    
    # 2-1. 커스텀 검색 함수 정의 (LangChain Retriever 호환용)
    def retrieve_documents(query: str) -> str:
        query_vector = embed_model.embed_query(query)
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=2 # 가장 유사한 2개 가져오기
        )
        # 검색된 문서들을 하나의 텍스트 덩어리로 합침
        docs_str = "\n".join(results['documents'][0])
        return docs_str
    
    # 2-2. RAG 전용 프롬프트 템플릿
    template = """당신은 친절하고 정확한 사내 AI 업무 비서입니다.
    아래에 제공된 [사내 문서 내용]만을 기반으로 [질문]에 답변하세요.
    만약 문서에 답이 없다면, "해당 내용은 사내 문서에서 찾을 수 없습니다"라고 정중하게 말하세요.
    
    [사내 문서 내용]
    {context}
    
    [질문]
    {question}
    
    답변:"""
    
    prompt = PromptTemplate.from_template(template)
    
    # 2-3. 파이프라인(Chain) 조립 (LCEL 문법)
    rag_chain = (
        {"context": retrieve_documents, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser() # 출력결과를 문자열로 깔끔하게 파싱
    )
    
    return rag_chain

# --- [3. 완벽한 RAG 시스템 실행] ---
def step3_run_rag(chain, query: str):
    """최종 조립된 RAG 체인에 질문을 던지고 결과를 받습니다."""
    print(f"\n🙋‍♂️ 사용자 질문: {query}")
    print("🤖 AI 답변:")
    
    # 스트리밍 방식(글자 단위 출력)으로 응답을 받아옵니다.
    for chunk in chain.stream(query):
        print(chunk, end="", flush=True)
    print("\n")

if __name__ == "__main__":
    print("=" * 50)
    print("[사내 문서 기반 RAG Q&A 엔진 구동]")
    print("=" * 50)
    
    # 1. 구성 요소 초기화
    llm, collection, embed_model = step1_setup_components()
    
    # 2. 체인 생성
    rag_chain = step2_create_rag_chain(llm, collection, embed_model)
    
    # 3. 질문 테스트
    step3_run_rag(rag_chain, "여름 휴가 언제 쓸 수 있어?")
    step3_run_rag(rag_chain, "우리 회사 연봉 협상 기준은 어떻게 돼?")
