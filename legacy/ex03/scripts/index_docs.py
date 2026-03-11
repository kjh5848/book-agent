import os
import sys
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# 프로젝트 루트를 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# 설정 로드
DOCS_DIR = "docs"
PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./vector_db")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/ko-sroberta-multitask")

def index_documents():
    # 1. 문서 로드 (PDF) - 재귀적 탐색
    documents = []
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)
        print(f"'{DOCS_DIR}' 폴더가 생성되었습니다. PDF 문서를 해당 폴더에 넣어주세요.")
        return

    print(f"'{DOCS_DIR}' 폴더 내 PDF 파일 탐색 중...")
    pdf_files = []
    for root, dirs, files in os.walk(DOCS_DIR):
        for file in files:
            if file.endswith('.pdf'):
                full_path = os.path.join(root, file)
                pdf_files.append(full_path)
    
    if not pdf_files:
        print(f"'{DOCS_DIR}' 폴더 내에 PDF 파일이 없습니다.")
        return

    print(f"발견된 PDF 파일 {len(pdf_files)}개: {pdf_files}")
    for file_path in pdf_files:
        try:
            print(f"파일 로드 중: {os.path.basename(file_path)}")
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())
        except Exception as e:
            print(f"파일 로드 실패 ({file_path}): {e}")

    # 2. 텍스트 분할
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""]
    )
    splits = text_splitter.split_documents(documents)
    print(f"총 {len(splits)} 개의 텍스트 청크가 생성되었습니다.")

    # 3. 임베딩 모델 설정
    print(f"임베딩 모델 로딩 중: {EMBEDDING_MODEL_NAME}")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={'device': 'cpu'} # Mac의 경우 'mps' 가능하나 보편성을 위해 cpu 설정
    )

    # 4. Chroma DB에 저장
    print(f"벡터 DB 저장 중: {PERSIST_DIRECTORY}")
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=PERSIST_DIRECTORY
    )
    print("인덱싱이 완료되었습니다.")

if __name__ == "__main__":
    index_documents()
