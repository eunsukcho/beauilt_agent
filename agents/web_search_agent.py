"""
웹 검색 에이전트

벡터 DB에서 찾을 수 없는 정보를 웹에서 검색하는 에이전트입니다.
"""

# 표준 라이브러리
from typing import List, Dict, Any

# Third-party 라이브러리
from ddgs import DDGS
from langchain_openai import ChatOpenAI

# 로컬 모듈
from config import get_settings


class WebSearchAgent:
    """
    웹 검색 에이전트

    벡터 DB 검색 결과가 부족하거나 최신 정보가 필요할 때
    웹에서 정보를 검색합니다.
    """

    def __init__(self):
        """에이전트 초기화"""
        self.settings = get_settings()

        # LLM 초기화
        self.llm = ChatOpenAI(
            model=self.settings.openai_model,
            temperature=0.7,
            api_key=self.settings.openai_api_key,
        )

        # 웹 검색 도구 초기화
        # DuckDuckGo 검색은 ddgs 라이브러리를 직접 사용합니다.
        # (LangChain의 DuckDuckGoSearchRun은 문자열을 반환하는 경우가 있어 파싱이 불안정)

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        웹에서 정보 검색

        Args:
            query: 검색할 질문
            max_results: 최대 결과 개수

        Returns:
            검색 결과 리스트 (title, url, snippet 등)
        """
        try:
            # 검색 쿼리 최적화 (피부 관리 관련 키워드 추가)
            optimized_query = self._optimize_query(query)

            # 웹 검색 실행 (구조화된 결과 반환)
            results: List[Dict[str, Any]] = []
            with DDGS() as ddgs:
                for item in ddgs.text(
                    optimized_query,
                    max_results=max_results,
                    safesearch="moderate",
                    region="kr-kr",
                ):
                    # ddgs 결과 키는 환경/버전에 따라 다를 수 있어 안전하게 꺼냅니다.
                    results.append(
                        {
                            "title": item.get("title", "") or item.get("heading", ""),
                            "url": item.get("href", "") or item.get("url", ""),
                            "snippet": item.get("body", "") or item.get("snippet", "") or item.get("content", ""),
                        }
                    )

            return results
        except Exception as e:
            print(f"웹 검색 중 오류 발생: {e}")
            return []

    def _optimize_query(self, query: str) -> str:
        """
        검색 쿼리 최적화

        피부 관리 관련 키워드를 추가하여 검색 정확도를 높입니다.

        Args:
            query: 원본 쿼리

        Returns:
            최적화된 쿼리
        """
        # 피부 관리 관련 키워드 추가
        skin_care_keywords = ["피부 관리", "스킨케어", "화장품"]

        # 쿼리에 이미 키워드가 포함되어 있는지 확인
        has_keyword = any(keyword in query for keyword in skin_care_keywords)

        if not has_keyword:
            # 키워드가 없으면 추가
            optimized = f"{query} 피부 관리"
        else:
            optimized = query

        return optimized

    def format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """
        검색 결과를 텍스트로 포맷팅

        Args:
            results: 검색 결과 리스트

        Returns:
            포맷팅된 텍스트
        """
        if not results:
            return "웹 검색 결과를 찾을 수 없습니다."

        formatted_text = "=== 웹 검색 결과 ===\n\n"
        for i, result in enumerate(results, 1):
            formatted_text += f"[결과 {i}]\n"
            if result.get("title"):
                formatted_text += f"제목: {result['title']}\n"
            if result.get("snippet"):
                formatted_text += f"내용: {result['snippet']}\n"
            if result.get("url"):
                formatted_text += f"출처: {result['url']}\n"
            formatted_text += "\n"

        return formatted_text

    def should_search_web(self, vector_db_results: List[str], query: str) -> bool:
        """
        웹 검색이 필요한지 판단

        Args:
            vector_db_results: 벡터 DB 검색 결과
            query: 사용자 쿼리

        Returns:
            웹 검색 필요 여부
        """
        # 벡터 DB 결과가 없거나 너무 적으면 웹 검색
        if not vector_db_results or len(vector_db_results) < 2:
            return True

        # 최신 정보가 필요한 키워드가 있으면 웹 검색
        recent_keywords = ["최신", "새로운", "2024", "2025", "최근", "trend", "new"]
        if any(keyword in query.lower() for keyword in recent_keywords):
            return True

        # 벡터 DB 결과의 관련성이 낮으면 웹 검색
        # (간단한 휴리스틱: 결과가 짧거나 키워드가 많이 포함되지 않으면)
        total_length = sum(len(result) for result in vector_db_results)
        if total_length < 500:  # 결과가 너무 짧으면
            return True

        return False
