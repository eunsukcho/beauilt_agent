"""
채팅 처리 공통 로직

main.py(CLI)와 streamlit_app.py(웹)에서 공통으로 사용하는
워크플로우 실행, 응답 추출, 맥락 관리 로직을 모아둡니다.
"""

import logging
from typing import Any, Dict, List, Optional

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from config import get_settings
from workflow.state import AgentState

logger = logging.getLogger("beauilt-agent.chat")

# ── 상수 ──────────────────────────────────────────────────────────────────────

_NEW_DIAGNOSIS_KEYWORDS = ["진단", "피부 상태", "피부 타입", "어떤 피부", "새로"]

_FOLLOWUP_PATTERNS = [
    "그럼", "그런데", "그러면", "그래서", "그렇다면",
    "그거", "그게", "그건", "그것",
    "또", "추가로", "더", "또한",
    "질문", "궁금", "알고 싶", "궁금한데",
    "?", "요", "까", "까요", "되나요", "될까요",
]

# 상태 키 우선순위 — 가장 마지막 단계 결과부터 반환
_RESPONSE_PRIORITY = [
    "simulation_result",
    "ingredient_analysis_result",
    "care_guide",
    "analysis_result",
    "diagnosis_result",
]

DEFAULT_RESPONSE = (
    "안녕하세요! 피부 관리 전문가입니다.\n\n"
    "어떤 도움이 필요하신가요?\n"
    "- 피부 상태를 진단해드릴 수 있습니다\n"
    "- 피부 케어 가이드라인을 제공해드릴 수 있습니다\n"
    "- 성분 분석도 도와드릴 수 있습니다\n\n"
    "원하시는 기능을 말씀해주시면 더 구체적으로 도와드리겠습니다!"
)

_FOLLOWUP_SYSTEM_PROMPT = (
    "당신은 전문 피부 관리사입니다.\n"
    "사용자의 추가 질문에 대해 이전 대화 맥락을 참고하여 친근하고 정확하게 답변해주세요.\n"
    "말투는 따뜻하고 친근하며, 20~30대 남녀를 대상으로 합니다.\n"
    "이전에 제공한 정보와 일관성을 유지하면서 구체적으로 답변해주세요.\n"
    "질문에 대한 핵심 답변을 먼저 제시하고, 필요시 간단한 설명을 추가해주세요."
)

# ── 입력 검증 ─────────────────────────────────────────────────────────────────

MAX_INPUT_LENGTH = 2000


def validate_user_input(user_input: str) -> str:
    """
    사용자 입력 검증 및 정제

    Args:
        user_input: 원본 사용자 입력

    Returns:
        공백이 제거된 정제된 입력

    Raises:
        ValueError: 빈 입력이거나 길이 초과 시
    """
    text = user_input.strip()
    if not text:
        raise ValueError("입력 내용이 없습니다.")
    if len(text) > MAX_INPUT_LENGTH:
        raise ValueError(f"입력이 너무 깁니다. {MAX_INPUT_LENGTH}자 이내로 입력해주세요.")
    return text


# ── 추가 질문 판단 ────────────────────────────────────────────────────────────

def is_followup_question(user_input: str, has_history: bool) -> bool:
    """
    추가 질문(후속 질문)인지 판단

    Args:
        user_input: 사용자 입력
        has_history: 이전 대화 히스토리 존재 여부

    Returns:
        추가 질문이면 True
    """
    if not has_history:
        return False
    if any(kw in user_input.lower() for kw in _NEW_DIAGNOSIS_KEYWORDS):
        return False
    if len(user_input.strip()) < 50 or any(p in user_input for p in _FOLLOWUP_PATTERNS):
        return True
    return False


# ── 워크플로우 실행 ───────────────────────────────────────────────────────────

def build_initial_state(
    user_input: str,
    previous_context: Dict[str, Any],
    conversation_history: Optional[List[Dict[str, str]]] = None,
    active_products: Optional[List[Dict[str, Any]]] = None,
) -> AgentState:
    """
    워크플로우 초기 상태(AgentState) 생성

    Args:
        user_input: 검증된 사용자 입력
        previous_context: 이전 진단/분석/가이드 결과
        conversation_history: 최근 대화 히스토리

    Returns:
        초기 AgentState
    """
    return {
        "user_input": user_input,
        "diagnosis_result": previous_context.get("diagnosis_result"),
        "analysis_result": previous_context.get("analysis_result"),
        "care_guide": previous_context.get("care_guide"),
        "simulation_result": None,
        "ingredient_analysis_result": None,
        "web_search_results": None,
        "current_step": "",
        "final_response": None,
        "lifestyle_info": None,
        "conversation_history": conversation_history[-5:] if conversation_history else None,
        "routing_target": None,
        "user_intent": None,
        "active_products": active_products,
        "error": None,
    }


def run_workflow(workflow, initial_state: AgentState) -> Optional[Dict[str, Any]]:
    """
    워크플로우 실행 후 마지막 노드 출력 반환

    LangGraph stream()은 각 단계마다 {"노드명": state} 를 yield 합니다.
    마지막으로 yield 된 값의 state 가 최종 결과입니다.

    Args:
        workflow: 컴파일된 LangGraph 워크플로우
        initial_state: 초기 상태

    Returns:
        마지막 노드의 출력 state, 또는 None
    """
    last_node_output = None
    for output in workflow.stream(initial_state):
        # output = {"노드명": state_dict} — 항상 키가 하나
        last_node_output = next(iter(output.values()))
    return last_node_output


def extract_response(last_node_output: Dict[str, Any]) -> Optional[str]:
    """
    상태에서 우선순위에 따라 최종 응답 추출

    Args:
        last_node_output: 마지막 노드 출력 상태

    Returns:
        추출된 응답 문자열, 또는 None
    """
    for key in _RESPONSE_PRIORITY:
        value = last_node_output.get(key)
        if value:
            return value
    return None


def update_context(
    previous_context: Dict[str, Any],
    last_node_output: Dict[str, Any],
) -> None:
    """
    이전 컨텍스트를 최신 노드 출력으로 업데이트 (in-place)

    Args:
        previous_context: 업데이트할 컨텍스트 딕셔너리
        last_node_output: 마지막 노드 출력 상태
    """
    for key in ("diagnosis_result", "analysis_result", "care_guide"):
        if last_node_output.get(key):
            previous_context[key] = last_node_output[key]


# ── 추가 질문 처리 ────────────────────────────────────────────────────────────

def handle_followup_question(
    user_input: str,
    previous_context: Dict[str, Any],
    recent_messages: List[Dict[str, str]],
) -> str:
    """
    추가 질문 처리 — 이전 맥락을 참고하여 LLM이 직접 답변

    Args:
        user_input: 사용자 입력
        previous_context: 이전 진단/케어 가이드 결과
        recent_messages: 최근 대화 목록 [{"role": "user"/"assistant", "content": "..."}]

    Returns:
        AI 응답
    """
    settings = get_settings()
    llm = ChatOpenAI(model=settings.openai_model, temperature=0.7, api_key=settings.openai_api_key)

    context_parts = []
    if previous_context.get("diagnosis_result"):
        context_parts.append(f"[이전 진단 결과]\n{previous_context['diagnosis_result']}")
    if previous_context.get("care_guide"):
        context_parts.append(f"[이전 케어 가이드]\n{previous_context['care_guide']}")

    messages: list = [SystemMessage(content=_FOLLOWUP_SYSTEM_PROMPT)]
    for msg in recent_messages:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))

    context_text = "\n".join(context_parts) if context_parts else "없음"
    messages.append(HumanMessage(content=(
        f"이전 대화 맥락:\n{context_text}\n\n"
        f"사용자의 추가 질문: {user_input}\n\n"
        "위 맥락을 참고하여 사용자의 질문에 직접적이고 구체적으로 답변해주세요. "
        "이전에 제공한 정보와 모순되지 않도록 주의하세요."
    )))

    try:
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        logger.error("추가 질문 처리 오류: %s", e, exc_info=True)
        return "죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
