import sys
import os

# 프로젝트 루트 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.vector_service import vector_service

def check():
    print("🔎 VectorDB 메타데이터 검증 중...", flush=True)
    if not vector_service.vector_db:
        print("❌ DB가 초기화되지 않았습니다.")
        return

    # ChromaDB 컬렉션에 직접 접근하여 데이터 조회
    try:
        collection = vector_service.vector_db._collection
        count = collection.count()
        print(f"📊 총 저장된 청크 수: {count}", flush=True)
        
        if count == 0:
            print("❌ 저장된 데이터가 없습니다.")
            return

        # 샘플 데이터 5개 조회
        peek = collection.peek(limit=5)
        
        print("\n[샘플 데이터 확인]")
        for i in range(len(peek['ids'])):
            print(f"\n--- Chunk {i+1} ---")
            print(f"📂 Source: {peek['metadatas'][i].get('source_filename', 'N/A')}")
            print(f"🏷️  Metadata: {peek['metadatas'][i]}")
    except Exception as e:
        print(f"❌ 검증 중 오류 발생: {e}")

if __name__ == "__main__":
    check()
