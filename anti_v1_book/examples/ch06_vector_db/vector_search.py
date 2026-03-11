# 환경 세팅 가이드 (CH06)
# pip install chromadb sentence-transformers langchain-huggingface

import os
from langchain_huggingface import HuggingFaceEmbeddings
import chromadb
from chromadb.config import Settings

# --- [1. 임베딩 모델 준비 (HuggingFace)] ---
def step1_get_embedding_model():
    """한국어 처리에 탁월한 오픈소스 임베딩 모델을 로드합니다."""
    print("🧠: 한국어 임베딩 모델을 로드 중입니다...")
    # BAAI/bge-m3 또는 ko-sroberta-multitask 등 가벼운 모델 사용 (여기서는 실습용)
    embeddings = HuggingFaceEmbeddings(model_name="jhgan/ko-sroberta-multitask")
    return embeddings

# --- [2. ChromaDB 클라이언트 설정 및 초기화] ---
def step2_init_vector_db():
    """로컬 디렉토리에 저장되는 ChromaDB 클라이언트를 생성합니다."""
    print("🗄️: Vector DB (Chroma) 초기화를 시작합니다...")
    
    # DB가 저장될 폴더 경로 지정
    db_path = "./anti_v1_book/examples/ch06_vector_db/chroma_storage"
    os.makedirs(db_path, exist_ok=True)
    
    client = chromadb.PersistentClient(path=db_path)
    
    # 컬렉션(테이블 개념) 생성 또는 가져오기
    collection = client.get_or_create_collection(
        name="company_rules",
        metadata={"hnsw:space": "cosine"} # 코사인 유사도 사용
    )
    return collection

# --- [3. 가상 문서 데이터 적재 (인덱싱)] ---
def step3_insert_documents(collection, embed_model):
    """사내 문서 데이터를 임베딩하여 Vector DB에 저장합니다."""
    print("📄: 사내 문서 청크(Chunk)를 DB에 적재합니다...")
    
    documents = [
        "신입 사원은 입사 후 1개월 간 OJT를 필수로 받아야 합니다.",
        "법인 카드 결제 한도는 식대 기준 1인당 월 30만 원입니다.",
        "여름 휴가는 7월부터 8월 사이에 자유롭게 3일을 사용할 수 있습니다.",
        "서버실 출입은 사전 승인된 개발팀 및 인프라팀 인원만 가능합니다."
    ]
    
    # 텍스트를 벡터로 변환 (임베딩)
    embeddings = embed_model.embed_documents(documents)
    
    # 고유 ID 생성
    ids = [f"doc_{i}" for i in range(len(documents))]
    
    collection.add(
        documents=documents,
        embeddings=embeddings,
        ids=ids
    )
    print(f"✅ 총 {collection.count()}개의 문서 적재 완료!")

# --- [4. 유사도 검색 쿼리 실행] ---
def step4_search_rule(collection, embed_model, query: str):
    """질문과 가장 유사한 사내 문서를 Vector DB에서 찾아냅니다."""
    print(f"\n🔍 질문: '{query}'")
    
    # 질문을 벡터로 변환
    query_vector = embed_model.embed_query(query)
    
    # DB에서 가장 유사한 상위 2개 추출
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=2
    )
    
    print("-" * 30)
    print("💡 [검색 결과 Top 2]")
    for i, doc in enumerate(results['documents'][0]):
        distance = results['distances'][0][i]
        print(f"{i+1}. (단위거리: {distance:.4f}) {doc}")
    print("-" * 30)

if __name__ == "__main__":
    # IPO 패턴에 따라 순차적 실행
    embed_model = step1_get_embedding_model()
    collection = step2_init_vector_db()
    
    # 데이터 적재 (최초 1회만 실행하는 과정)
    step3_insert_documents(collection, embed_model)
    
    # 검색 테스트
    step4_search_rule(collection, embed_model, "신입사원 교육은 어떻게 되나요?")
    step4_search_rule(collection, embed_model, "여름 휴가 규정 알려주세요.")
