"""
문서를 벡터 DB에 추가하는 스크립트

"피부 관리의 기초" 같은 긴 문서를 벡터 DB에 추가할 때 사용합니다.
"""

# 표준 라이브러리
import sys
from pathlib import Path

# 프로젝트 루트 경로를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Third-party 라이브러리
from langchain_core.documents import Document

# 로컬 모듈
from vector_db import vector_store


def load_document_from_file(file_path: str, source_name: str = "피부관리교본") -> list:
    """
    파일에서 문서를 읽어서 Document 객체로 변환

    Args:
        file_path: 문서 파일 경로 (.txt, .md 등)
        source_name: 문서 출처 이름

    Returns:
        Document 객체 리스트
    """
    file_path_obj = Path(file_path)

    if not file_path_obj.exists():
        print(f"[ERROR] 파일을 찾을 수 없습니다: {file_path}")
        return []

    try:
        # 파일 읽기
        with open(file_path_obj, "r", encoding="utf-8") as f:
            content = f.read()

        # Document 객체 생성
        # 긴 문서는 자동으로 청크로 나뉩니다 (vector_store.add_documents에서 처리)
        document = Document(
            page_content=content,
            metadata={
                "source": source_name,
                "type": "교본",
                "file": file_path_obj.name,
                "title": file_path_obj.stem
            }
        )

        print(f"[OK] {file_path_obj.name} 로드 완료 ({len(content)}자)")
        return [document]

    except Exception as e:
        print(f"[FAIL] {file_path_obj.name} 로드 실패: {e}")
        return []


def load_document_from_text(text: str, title: str, source_name: str = "피부관리교본") -> list:
    """
    텍스트 문자열에서 직접 Document 객체 생성

    Args:
        text: 문서 내용
        title: 문서 제목
        source_name: 문서 출처 이름

    Returns:
        Document 객체 리스트
    """
    document = Document(
        page_content=text,
        metadata={
            "source": source_name,
            "type": "교본",
            "title": title
        }
    )

    print(f"[OK] '{title}' 문서 생성 완료 ({len(text)}자)")
    return [document]


def add_document_to_vector_db(file_path: str = None, text: str = None, title: str = None):
    """
    문서를 벡터 DB에 추가

    Args:
        file_path: 문서 파일 경로 (선택사항)
        text: 문서 내용 텍스트 (선택사항)
        title: 문서 제목 (text 사용 시 필수)
    """
    print("=" * 50)
    print("문서를 벡터 DB에 추가합니다...")
    print("=" * 50)

    # 벡터 스토어 초기화
    vector_store.initialize_vector_store()

    # 문서 로드
    documents = []

    if file_path:
        # 파일에서 로드
        documents = load_document_from_file(file_path, source_name="피부관리교본")
    elif text and title:
        # 텍스트에서 직접 생성
        documents = load_document_from_text(text, title, source_name="피부관리교본")
    else:
        print("[ERROR] file_path 또는 (text + title)을 제공해야 합니다.")
        return

    if not documents:
        print("[ERROR] 문서를 로드할 수 없습니다.")
        return

    # 벡터 DB에 추가
    print("\n벡터 DB에 문서 추가 중...")
    vector_store.add_documents(documents)

    print("\n[SUCCESS] 문서가 벡터 DB에 추가되었습니다!")
    print("=" * 50)


if __name__ == "__main__":
    # 사용 예시 1: 파일에서 로드
    # python scripts/add_document.py --file "data/피부관리의기초.md"

    # 사용 예시 2: 텍스트 직접 입력
    # python scripts/add_document.py --text "문서 내용..." --title "피부 관리의 기초"

    import argparse

    parser = argparse.ArgumentParser(description="문서를 벡터 DB에 추가")
    parser.add_argument("--file", type=str, help="추가할 문서 파일 경로")
    parser.add_argument("--text", type=str, help="추가할 문서 내용")
    parser.add_argument("--title", type=str, help="문서 제목 (--text 사용 시 필수)")

    args = parser.parse_args()

    if args.file:
        add_document_to_vector_db(file_path=args.file)
    elif args.text and args.title:
        add_document_to_vector_db(text=args.text, title=args.title)
    else:
        print("사용법:")
        print("  파일에서 추가: python scripts/add_document.py --file 'data/피부관리의기초.md'")
        print("  텍스트 직접: python scripts/add_document.py --text '내용...' --title '제목'")
        print("\n또는 이 스크립트를 수정하여 직접 문서를 추가하세요.")
