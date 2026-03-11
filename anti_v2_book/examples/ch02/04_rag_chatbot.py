import warnings
# 불필요한 LangChain 버전 경고 숨김 (실습 집중용)
warnings.filterwarnings("ignore")

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

def step1_load_retriever():
    """저장해둔 Vector DB 불러오기"""
    print("[1] 로컬 ChromaDB에서 사내 규정 데이터를 불러옵니다...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
    
    # 검색기(Retriever): 가장 질문과 유사한 내용 3개를 가져온다.
    return db.as_retriever(search_kwargs={"k": 3})

def step2_setup_rag_pipeline(retriever):
    """LangChain LCEL 기반 RAG 파이프라인 조립"""
    print("[2] Ollama(DeepSeek)와 검색기(Retriever)를 연결(RAG)합니다...")
    llm = ChatOllama(model="deepseek-r1:latest", temperature=0.1)
    
    # AI에게 역할 부여 및 검색 내용 포함 프롬프트 작성
    template = """당신은 안티그래비티 주식회사의 훌륭한 인사팀 어시스턴트입니다.
반드시 아래의 [사내 지식]을 기반으로 인사하며 친절하게 답변해주세요.
주어진 정보로 답을 알 수 없다면 "규정에서 찾을 수 없습니다"라고만 답변하세요. 지어내지 마세요(Hallucination 금지).

[사내 지식]
{context}

주임(질문자): {question}
답변:"""
    custom_prompt = PromptTemplate.from_template(template)
    
    # 문서를 텍스트로 합쳐주는 도우미 함수
    def format_docs(docs):
        # 출처(metadata)를 남겨두면 나중에 투명성을 입증할 수 있습니다.
        doc_texts = []
        for d in docs:
            doc_texts.append(f"({d.metadata.get('source', '알수없음')}):\n{d.page_content}")
        return "\n\n".join(doc_texts)

    # LCEL (LangChain Expression Language) 조립
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | custom_prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain

def step3_chat(rag_chain):
    """사용자 질의응답 터미널 챗봇"""
    print("\n[3] 셋업 완료! 사내 Q&A 봇이 가동되었습니다. (종료하려면 'exit' 입력)")
    print("-" * 50)
    
    while True:
        user_input = input("👤 질문: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        print("🤖 (규정 검색 후 추론 중...)")
        try:
            # 파이프라인 가동!
            answer = rag_chain.invoke(user_input)
            print("\n🤖 챗봇 답변:")
            print("=" * 40)
            print(answer)
            print("=" * 40)
        except Exception as e:
            print(f"에러가 났습니다: {e}\n(Ollama가 켜져있는지 확인하세요!)")

if __name__ == "__main__":
    retriever_obj = step1_load_retriever()
    rag_pipeline = step2_setup_rag_pipeline(retriever_obj)
    step3_chat(rag_pipeline)
