"""
벡터 DB 초기화 스크립트

피부 관리 교본과 교재를 벡터 DB에 추가하는 스크립트입니다.
실제 데이터 파일이 준비되면 이 스크립트를 실행하여 벡터 DB를 구축합니다.
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


def load_skin_type_cards() -> list:
    """
    피부 타입/상태 진단 카드 로드

    data/skin_type_cards/ 폴더의 마크다운 파일들을 읽어서 Document 객체로 변환합니다.

    Returns:
        Document 객체 리스트
    """
    cards_dir = project_root / "data" / "skin_type_cards"
    documents = []

    if not cards_dir.exists():
        print(f"[WARNING] 카드 폴더가 없습니다: {cards_dir}")
        return documents

    # 마크다운 파일 읽기
    md_files = sorted(cards_dir.glob("*.md"))

    for md_file in md_files:
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 파일명에서 카드 번호와 이름 추출
            filename = md_file.stem
            parts = filename.split("_", 1)
            card_num = parts[0] if len(parts) > 0 else ""
            card_name = parts[1] if len(parts) > 1 else filename

            documents.append(
                Document(
                    page_content=content,
                    metadata={
                        "source": "피부타입진단카드",
                        "type": "피부타입진단",
                        "card_number": card_num,
                        "card_name": card_name,
                        "file": md_file.name
                    }
                )
            )
            print(f"  [OK] {md_file.name} 로드 완료")
        except Exception as e:
            print(f"  [FAIL] {md_file.name} 로드 실패: {e}")

    return documents


def load_ingredient_cards() -> list:
    """
    성분 정보 카드 로드

    data/ingredient_cards/ 폴더의 마크다운 파일들을 읽어서 Document 객체로 변환합니다.

    Returns:
        Document 객체 리스트
    """
    cards_dir = project_root / "data" / "ingredient_cards"
    documents = []

    if not cards_dir.exists():
        print(f"[WARNING] 성분 카드 폴더가 없습니다: {cards_dir}")
        return documents

    # 마크다운 파일 읽기
    md_files = sorted(cards_dir.glob("*.md"))

    for md_file in md_files:
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 파일명에서 카드 번호와 이름 추출
            filename = md_file.stem
            parts = filename.split("_", 1)
            card_num = parts[0] if len(parts) > 0 else ""
            card_name = parts[1] if len(parts) > 1 else filename

            documents.append(
                Document(
                    page_content=content,
                    metadata={
                        "source": "성분정보카드",
                        "type": "성분정보",
                        "card_number": card_num,
                        "card_name": card_name,
                        "file": md_file.name
                    }
                )
            )
            print(f"  [OK] {md_file.name} 로드 완료")
        except Exception as e:
            print(f"  [FAIL] {md_file.name} 로드 실패: {e}")

    return documents


def load_textbook_documents() -> list:
    """
    교본/교재 문서 로드

    data/ 폴더의 교본 문서들을 읽어서 Document 객체로 변환합니다.

    Returns:
        Document 객체 리스트
    """
    textbooks_dir = project_root / "data"
    documents = []

    # 교본 문서 파일 목록 (피부관리의기초.md 등)
    textbook_files = [
        "피부관리의기초.md",
    ]

    for filename in textbook_files:
        file_path = textbooks_dir / filename
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                documents.append(
                    Document(
                        page_content=content,
                        metadata={
                            "source": "피부관리교본",
                            "type": "교본",
                            "title": file_path.stem,
                            "file": file_path.name
                        }
                    )
                )
                print(f"  [OK] {file_path.name} 로드 완료")
            except Exception as e:
                print(f"  [FAIL] {file_path.name} 로드 실패: {e}")
        else:
            print(f"  [WARNING] 파일을 찾을 수 없습니다: {file_path}")

    return documents


def init_vector_db():
    """
    벡터 DB 초기화 및 문서 추가

    실제 데이터 파일이 준비되면 이 함수를 수정하여
    파일에서 데이터를 읽어와야 합니다.
    """
    print("벡터 DB 초기화를 시작합니다...")
    # 벡터 스토어 초기화
    vector_store.initialize_vector_store()

    # 피부 타입 진단 카드 로드
    print("\n피부 타입 진단 카드 로드 중...")
    card_documents = load_skin_type_cards()

    # 성분 정보 카드 로드
    print("\n성분 정보 카드 로드 중...")
    ingredient_documents = load_ingredient_cards()

    # 교본/교재 문서 로드
    print("\n교본/교재 문서 로드 중...")
    textbook_documents = load_textbook_documents()

    # 모든 문서 합치기
    all_documents = card_documents + ingredient_documents + textbook_documents

    # 벡터 DB에 문서 추가
    if all_documents:
        vector_store.add_documents(all_documents)
        print(f"\n[SUCCESS] 총 {len(all_documents)}개의 문서가 벡터 DB에 추가되었습니다.")
        print(f"   - 피부 타입 진단 카드: {len(card_documents)}개")
        print(f"   - 성분 정보 카드: {len(ingredient_documents)}개")
        print(f"   - 교본/교재 문서: {len(textbook_documents)}개")
    else:
        print("\n[WARNING] 추가할 문서가 없습니다.")

    print("\n벡터 DB 초기화가 완료되었습니다!")


if __name__ == "__main__":
    print("=" * 50)
    print("벡터 DB 초기화 스크립트")
    print("=" * 50)
    print("\n이 스크립트는 피부 관리 교본과 교재를 벡터 DB에 추가합니다.")
    print("실제 데이터 파일이 준비되면 load_sample_documents() 함수를 수정하세요.")
    print("=" * 50)
    print()

    try:
        init_vector_db()
    except Exception as e:
        print(f"\n[ERROR] 오류 발생: {e}")
        sys.exit(1)
