import os
import fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# 02_table_parsing.py 의 핵심 로직을 가져왔다고 가정 (단순화하여 통짜 문자열 생성)
def _extract_all_text_with_tables(pdf_path: str) -> str:
    """텍스트와 표(Markdown)를 모두 포함하여 단일 문자열로 추출"""
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        # 일반 텍스트
        full_text += page.get_text() + "\n"
        # 표 데이터 (마크다운)
        tables = page.find_tables()
        for idx, table in enumerate(tables):
            full_text += f"\n### [표 {idx+1}]\n"
            full_text += "| " + " | ".join(table.extract()[0]) + " |\n"
            full_text += "|" + "|".join(["---"] * len(table.extract()[0])) + "|\n"
            for row in table.extract()[1:]:
                safe_row = [str(c).strip() if c else "" for c in row]
                full_text += "| " + " | ".join(safe_row) + " |\n"
            full_text += "\n"
    return full_text

def step1_prepare_documents() -> list[Document]:
    """PDF 파싱 및 Document 객체 생성"""
    pdf_path = "data/dummy_rules.pdf"
    print(f"[1] '{pdf_path}' 에서 데이터를 정제하여 텍스트 덩어리를 만듭니다...")
    
    raw_text = _extract_all_text_with_tables(pdf_path)
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_text(raw_text)
    
    docs = []
    for i, c in enumerate(chunks):
        # 출처(metadata)를 남기는 것이 핵심입니다.
        docs.append(Document(page_content=c, metadata={"source": "하계_휴가_규정.pdf", "chunk_id": i}))
    
    print(f" -> 총 {len(docs)}개의 조각(Chunk)으로 나누었습니다.")
    return docs

def step2_create_vector_db(docs: list[Document]):
    """ChromaDB 생성 및 로컬 저장"""
    db_path = "./chroma_db"
    print(f"\n[2] Vector DB(Chroma)에 저장소 '{db_path}'를 구축합니다...")
    
    # 무료 고성능 다국어 로컬 임베딩 모델 사용 (BGE-M3 등도 가능)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=db_path
    )
    print(" -> 벡터화 및 저장 완료!")

if __name__ == "__main__":
    print("=== [CH02-3] 사내 규정 Vector DB 구축 실습 ===")
    document_chunks = step1_prepare_documents()
    step2_create_vector_db(document_chunks)
    print("\n완벽합니다! 이제 AI의 망막에 사내 규정이 각인(저장)되었습니다.")
