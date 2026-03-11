"""
[실습 5 - Vector Database 적재 (Ingestion)]
앞서 변환된 parsed_data/ 폴더 내의 모든 마크다운(.md) 파일들을 읽어들여 
Langchain의 RecursiveCharacterTextSplitter로 청킹(Chunking)한 후, ChromaDB에 저장합니다.
"""
import os
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
# 실습의 편의를 위해 환경변수 없는 무료 SentenceTransformer 임베딩 사용
from langchain_huggingface import HuggingFaceEmbeddings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MD_DIR = os.path.join(BASE_DIR, '../parsed_data')
DB_DIR = os.path.join(BASE_DIR, '../chroma_db')

def ingest_markdowns_to_db():
    print(f"🔄 마크다운 문서 로드 중... ({MD_DIR})")
    if not os.path.exists(MD_DIR):
        print("❌ 변환된 마크다운 데이터가 없습니다. 1~4번 스크립트를 먼저 실행하세요.")
        return

    # 1. 마크다운 파일 일괄 분할 (Chunking)
    # RAG에 최적화되도록 제목(#, ##)을 기준으로 1차 분할
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    
    all_chunks = []
    
    for filename in os.listdir(MD_DIR):
        if not filename.endswith('.md'): continue
        
        file_path = os.path.join(MD_DIR, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        md_splits = markdown_splitter.split_text(text)
        
        # 파일명을 메타데이터에 추가
        for split in md_splits:
            split.metadata['source'] = filename
            
        all_chunks.extend(md_splits)

    print(f"✅ 총 {len(all_chunks)}개의 청크(Chunk)가 생성되었습니다.")
    
    # 길이가 너무 긴 청크를 대비해 2차 분할
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    final_splits = text_splitter.split_documents(all_chunks)

    # 2. Vector DB (Chroma) 저장
    print("🧠 임베딩 모델 로드 및 벡터DB 저장 시작...")
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3") # 다국어 지원 뛰어난 임베딩 모델
    
    vectorstore = Chroma.from_documents(
        documents=final_splits,
        embedding=embeddings,
        persist_directory=DB_DIR
    )
    print(f"🎉 성공적으로 Chroma DB에 적재되었습니다! (경로: {DB_DIR})")

if __name__ == "__main__":
    ingest_markdowns_to_db()
