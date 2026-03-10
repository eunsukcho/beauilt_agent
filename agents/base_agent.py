"""
기본 에이전트 클래스

모든 에이전트가 상속받을 기본 클래스입니다.
공통 기능(LLM 초기화, 프롬프트 관리 등)을 제공합니다.
"""

# 표준 라이브러리
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import logging

# Third-party 라이브러리
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# 로컬 모듈
from config import get_settings
from vector_db import vector_store
from agents.web_search_agent import WebSearchAgent


class BaseAgent(ABC):
    """
    기본 에이전트 클래스

    모든 에이전트의 공통 기능을 제공합니다:
    - LLM 초기화
    - 벡터 DB 검색
    - 대화 히스토리 관리
    """

    def __init__(self, agent_name: str, system_prompt: str):
        """
        에이전트 초기화

        Args:
            agent_name: 에이전트 이름
            system_prompt: 시스템 프롬프트 (에이전트의 역할과 성격 정의)
        """
        self.agent_name = agent_name
        self.settings = get_settings()
        self.logger = logging.getLogger(f"beauilt-agent.{agent_name}")

        # OpenAI LLM 초기화
        # 최신 langchain-openai에서는 API 키를 env(OPENAI_API_KEY)로 읽는 방식이 안정적입니다.
        # (버전 호환성 이슈를 피하기 위해 직접 파라미터로 넘기지 않습니다)
        self.llm = ChatOpenAI(
            model=self.settings.openai_model,
            temperature=0.7,  # 창의성 정도 (0~1, 높을수록 창의적)
            api_key=self.settings.openai_api_key,
        )

        # 시스템 프롬프트 설정
        self.system_prompt = system_prompt

        # 대화 히스토리 저장
        self.conversation_history: List[Dict[str, str]] = []

        # 웹 검색 에이전트 초기화
        self.web_search_agent = WebSearchAgent()

    def search_knowledge_base(self, query: str, k: int = 5) -> List[str]:
        """
        벡터 DB에서 관련 정보 검색

        Args:
            query: 검색할 질문
            k: 반환할 문서 개수

        Returns:
            검색된 문서 내용 리스트
        """
        try:
            results = vector_store.similarity_search(query, k=k)
            return [doc.page_content for doc in results]
        except Exception as e:
            self.logger.error("벡터 DB 검색 오류: %s", e, exc_info=True)
            return []

    def search_with_fallback(self, query: str, k: int = 5) -> tuple[List[str], Optional[List[Dict[str, Any]]]]:
        """
        벡터 DB 검색 후 필요시 웹 검색 수행

        Args:
            query: 검색할 질문
            k: 벡터 DB에서 반환할 문서 개수

        Returns:
            (벡터 DB 결과, 웹 검색 결과) 튜플
        """
        # 먼저 벡터 DB에서 검색
        vector_results = self.search_knowledge_base(query, k=k)

        # 웹 검색이 필요한지 판단
        web_results = None
        if self.web_search_agent.should_search_web(vector_results, query):
            self.logger.debug("웹 검색 수행: 벡터 DB 결과 부족 또는 최신 정보 필요")
            web_results = self.web_search_agent.search(query, max_results=5)

        return vector_results, web_results

    def build_prompt(self, user_input: str, context: Optional[List[str]] = None,
                     web_context: Optional[List[Dict[str, Any]]] = None,
                     active_products: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        프롬프트 구성

        시스템 프롬프트, 컨텍스트, 웹 검색 결과, 사용자 입력을 조합하여 최종 프롬프트를 만듭니다.

        Args:
            user_input: 사용자 입력
            context: 벡터 DB에서 검색한 컨텍스트 정보
            web_context: 웹 검색 결과

        Returns:
            구성된 프롬프트
        """
        prompt_parts = [self.system_prompt]

        # 사용자 등록 제품 컨텍스트
        if active_products:
            prompt_parts.append("\n\n=== 사용자가 현재 사용 중인 제품 ===")
            for p in active_products:
                line = f"- [{p['category']}] {p['name']}"
                if p.get('brand'):
                    line += f" ({p['brand']})"
                line += f"  |  사용 시작: {p['started_at']}"
                if p.get('ingredients'):
                    line += f"  |  주요 성분: {p['ingredients']}"
                prompt_parts.append(line)
            prompt_parts.append("위 제품들을 참고하여 답변해주세요. 성분 충돌이나 루틴 개선이 필요하면 언급해주세요.")

        # 벡터 DB 컨텍스트 정보 추가
        if context:
            prompt_parts.append("\n\n=== 벡터 DB 참고 정보 ===")
            for i, ctx in enumerate(context, 1):
                prompt_parts.append(f"\n[참고 {i}]\n{ctx}")

        # 웹 검색 결과 추가
        if web_context:
            prompt_parts.append("\n\n=== 웹 검색 결과 ===")
            prompt_parts.append(self.web_search_agent.format_search_results(web_context))

        # 사용자 입력 추가
        prompt_parts.append(f"\n\n=== 사용자 질문 ===\n{user_input}")

        return "\n".join(prompt_parts)

    def add_to_history(self, user_input: str, ai_response: str):
        """
        대화 히스토리에 추가

        Args:
            user_input: 사용자 입력
            ai_response: AI 응답
        """
        self.conversation_history.append({
            "user": user_input,
            "assistant": ai_response
        })

    @abstractmethod
    def process(self, user_input: str, **kwargs) -> str:
        """
        사용자 입력을 처리하고 응답 생성 (추상 메서드)

        각 에이전트마다 다르게 구현해야 합니다.

        Args:
            user_input: 사용자 입력
            **kwargs: 추가 파라미터

        Returns:
            AI 응답
        """
        pass

    def generate_response(self, prompt: str, max_retries: int = 2) -> str:
        """
        LLM을 사용하여 응답 생성. 일시적 오류 시 최대 max_retries회 재시도.

        Args:
            prompt: 입력 프롬프트
            max_retries: 최대 재시도 횟수

        Returns:
            생성된 응답
        """
        messages = [SystemMessage(content=self.system_prompt)]
        for conv in self.conversation_history[-5:]:
            messages.append(HumanMessage(content=conv["user"]))
            messages.append(AIMessage(content=conv["assistant"]))
        messages.append(HumanMessage(content=prompt))

        for attempt in range(max_retries + 1):
            try:
                response = self.llm.invoke(messages)
                return response.content
            except Exception as e:
                if attempt < max_retries:
                    self.logger.warning(
                        "응답 생성 재시도 (%d/%d): %s", attempt + 1, max_retries, e
                    )
                else:
                    self.logger.error("응답 생성 실패: %s", e, exc_info=True)

        return "죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
