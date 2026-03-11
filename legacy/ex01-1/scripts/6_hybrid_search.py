"""
[실습 6 - Vector Search Test (유사도 검색)]
적재된 ChromaDB에 쿼리(질문)를 날려 가장 내용이 유사한 원문 조각을 찾아옵니다.
"""
import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, '../chroma_db')

def search_database(query):
    if not os.path.exists(DB_DIR):
        print("❌ 벡터DB 폴더가 없습니다. 5번 ingest 스크립트를 먼저 실행하세요.")
        return

    print("🧠 임베딩 모델 로드 중...")
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
    
    print(f"📂 Chroma DB 로드 중... ({DB_DIR})")
    vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    
    print(f"\n🔍 사용자 질문: '{query}'\n")
    print("-" * 50)
    
    # 유사도(Similarity) 기반 검색 수행 (상위 3개 반환)
    results = vectorstore.similarity_search_with_score(query, k=3)
    
    if not results:
        print("관련 문서를 찾지 못했습니다.")
        return
        
    for i, (doc, score) in enumerate(results, 1):
        # score는 거리를 나타낼 수 있으므로(낮을수록 유사), 거리가 반환될 경우 1-score 형태로 변환하여 표현하기도 함
        # ChromaDB의 default L2 distance일 경우 점수가 낮을수록 유사합니다.
        print(f"[결과 {i}] 출처: {doc.metadata.get('source', '알수없음')} | 거리(Distance): {score:.4f}")
        print(f"문서 내용: {doc.page_content.strip()[:100]}...\n")

if __name__ == "__main__":
    # 보안 규정 관련 질문 테스트
    test_query = "비밀번호 설정할 때 특수문자를 넣어야 하나요?"
    search_database(test_query)
