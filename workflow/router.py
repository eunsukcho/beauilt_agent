"""
초기 라우터 노드

사용자 질문의 의도를 파악하여 적절한 에이전트로 라우팅합니다.
의도 분류는 단순 작업이므로 저렴한 gpt-4o-mini를 사용합니다.
"""

import logging

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from workflow.state import AgentState
from config import get_settings

logger = logging.getLogger("beauilt-agent.router")

# LLM 인스턴스 캐싱 — 매 요청마다 새로 생성하지 않음
_settings = get_settings()
_router_llm = ChatOpenAI(model=_settings.openai_router_model, temperature=0.0, api_key=_settings.openai_api_key)

_VALID_INTENTS = {"diagnosis", "ingredient_analysis", "care_guide", "simulation"}

_SYSTEM_PROMPT = """당신은 사용자 질문의 의도를 분류하는 라우터입니다.
사용자의 질문을 보고 다음 중 하나로 분류해주세요:

1. "diagnosis" - 피부 상태 진단 요청
   예: "내 피부 타입이 뭐야?", "피부가 건조해요", "트러블이 자주 나요"

2. "ingredient_analysis" - 성분 분석/추천 요청
   예: "히알루론산 효능이 뭐야?", "나이아신아마이드 추천해줘", "세라마이드와 함께 써도 되나요?"

3. "care_guide" - 케어 가이드 요청 (이미 진단이 완료된 경우)
   예: "케어 가이드 알려줘", "루틴 추천해줘", "어떻게 관리해야 해요?"

4. "simulation" - 시뮬레이션 요청
   예: "이 루틴 적용하면 어떻게 될까요?", "변화 예측해줘"

응답은 반드시 위 4가지 중 하나의 단어만 출력하세요. 설명 없이 단어만 출력합니다."""


def initial_router(state: AgentState) -> AgentState:
    """
    사용자 질문의 의도를 파악하여 적절한 노드로 라우팅

    Args:
        state: 현재 상태

    Returns:
        routing_target이 설정된 상태
    """
    user_input = state.get("user_input", "").strip()

    # 이전 맥락이 있으면 진단 플로우로 바로 진행
    if state.get("conversation_history") or state.get("diagnosis_result"):
        state["routing_target"] = "diagnosis"
        return state

    try:
        messages = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=f"사용자 질문: {user_input}\n\n의도를 분류해주세요:"),
        ]

        response = _router_llm.invoke(messages)
        intent = response.content.strip().lower()

        if intent not in _VALID_INTENTS:
            logger.warning("알 수 없는 의도 '%s' → 기본값 'diagnosis' 로 폴백", intent)
            intent = "diagnosis"

        state["routing_target"] = intent
        state["user_intent"] = intent

    except Exception as e:
        logger.error("라우팅 오류: %s — 기본값 'diagnosis' 사용", e, exc_info=True)
        state["routing_target"] = "diagnosis"

    return state


def route_by_intent(state: AgentState) -> str:
    """
    routing_target 값에 따라 다음 노드 이름 반환

    Args:
        state: 현재 상태

    Returns:
        다음 노드 이름
    """
    return state.get("routing_target", "diagnosis")
