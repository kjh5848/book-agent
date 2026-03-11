import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

def embed_md_file(md_path, db_dir, metadata=None):
    """
    MD 파일을 읽어 텍스트 분할 후 임베딩 및 벡터 DB 저장
    :param metadata: 파일 단위 메타데이터 (dict, optional)
    """
    print(f"[Embed Strategy] Processing {md_path}...")
    
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        
    if not content:
        print(f"  [Warning] Skipping {md_path}: No content to embed.")
        return
        
    # 1. 텍스트 분할 (Semantic Chunking을 위한 기본 단계)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_text(content)
    
    # 2. 임베딩 모델 설정
    embed_model = HuggingFaceEmbeddings(
        model_name="jhgan/ko-sroberta-multitask",
        model_kwargs={'device': 'cpu'}
    )
    
    # 3. 벡터 DB 저장 (Chroma)
    # ID 생성: 파일명_청크인덱스 (중복 방지용)
    file_name = os.path.basename(md_path)
    ids = [f"{file_name}_{i}" for i in range(len(chunks))]
    
    # 메타데이터 구성
    metadatas = []
    for i in range(len(chunks)):
        chunk_meta = {"source": file_name, "chunk_index": i}
        if metadata:
            chunk_meta.update(metadata)  # 전달받은 메타데이터 병합
        metadatas.append(chunk_meta)
    
    # 기존 DB 로드 또는 새로 생성
    vectordb = Chroma(
        persist_directory=db_dir,
        embedding_function=embed_model
    )
    
    # 데이터 추가 (ID가 같으면 업데이트 효과)
    vectordb.add_texts(
        texts=chunks,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"  -> Embedded {len(chunks)} chunks to {db_dir} (with IDs)")

if __name__ == "__main__":
    # Test code
    # 이 파일이 직접 실행될 때(python scripts/embedding/embed_strategy.py)만 실행되는 구간입니다.
    # 현재는 별도의 테스트 로직이 필요 없어 pass(아무것도 하지 않음)로 두었습니다.
    pass
