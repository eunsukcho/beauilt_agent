"""
Chroma 벡터 스토어 모듈

문서 임베딩 저장, 추가, 유사 문서 검색 기능을 제공합니다.
- initialize_vector_store(): DB 초기화 또는 기존 DB 로드
- add_documents(): 문서를 청크로 분할하여 저장
- similarity_search(): 쿼리와 유사한 문서 검색
"""

# 표준 라이브러리
from pathlib import Path
from typing import List, Optional

# Third-party 라이브러리
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 로컬 모듈
from config import get_settings

# 설정 로드
_settings = get_settings()

# 벡터 DB 저장 경로 (절대 경로로 변환)
_project_root = Path(__file__).parent.parent
persist_directory = str(_project_root / _settings.vector_db_path.lstrip("./"))

# 전역 벡터 스토어 인스턴스
_vector_store: Optional[Chroma] = None

# 텍스트 분할기: 긴 문서를 겹치는 청크로 나눠 검색 정확도를 높임
_text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", ".", " ", ""],
)


def initialize_vector_store() -> Chroma:
    """
    벡터 스토어 초기화

    기존 DB가 있으면 로드하고, 없으면 새로 생성합니다.

    Returns:
        초기화된 Chroma 벡터 스토어
    """
    global _vector_store

    embeddings = OpenAIEmbeddings(api_key=_settings.openai_api_key)

    _vector_store = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
        collection_name="beauilt_knowledge",
    )

    return _vector_store


def _get_store() -> Chroma:
    """벡터 스토어 인스턴스 반환. 초기화되지 않은 경우 자동으로 초기화."""
    global _vector_store
    if _vector_store is None:
        initialize_vector_store()
    return _vector_store


def add_documents(documents: List[Document]) -> None:
    """
    문서를 벡터 DB에 추가

    긴 문서는 자동으로 청크로 분할한 뒤 임베딩을 생성하여 저장합니다.

    Args:
        documents: 추가할 Document 객체 리스트
    """
    store = _get_store()

    # 긴 문서를 청크로 분할
    split_docs = _text_splitter.split_documents(documents)
    print(f"  {len(documents)}개 문서 → {len(split_docs)}개 청크로 분할")

    store.add_documents(split_docs)

    print(f"  벡터 DB 저장 완료: {persist_directory}")


def similarity_search(query: str, k: int = 5) -> List[Document]:
    """
    쿼리와 유사한 문서 검색

    Args:
        query: 검색할 질문 또는 키워드
        k: 반환할 문서 개수

    Returns:
        유사도 순으로 정렬된 Document 객체 리스트
    """
    store = _get_store()
    return store.similarity_search(query, k=k)
