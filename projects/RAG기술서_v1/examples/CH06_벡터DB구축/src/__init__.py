"""
CH06 벡터 DB 구축 패키지.

PDF 문서를 수집하고, 청킹한 뒤 Ollama 임베딩으로
벡터화하여 ChromaDB에 저장하는 엔드투엔드 파이프라인을 제공합니다.

두 가지 파싱 방식을 지원합니다:
    규칙 기반: pdfplumber/PyMuPDF로 텍스트 직접 추출
    Vision LLM: PDF 페이지를 이미지로 변환 후 LLM이 Markdown으로 변환

모듈 목록:
    extractor:       PDF에서 텍스트를 추출합니다 (pdfplumber/PyMuPDF)
    vision_extractor: PDF 페이지를 Vision LLM으로 Markdown 변환합니다
    chunker:         텍스트를 검색에 적합한 청크로 분할합니다
    embedder:        Ollama REST API로 텍스트를 벡터로 변환합니다
    store:           ChromaDB에 벡터를 영속 저장하고 유사도 검색을 수행합니다
"""
