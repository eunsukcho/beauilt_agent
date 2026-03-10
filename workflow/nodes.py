"""
LangGraph 노드 정의

각 에이전트를 LangGraph 노드로 변환합니다.
노드는 상태(state)에서 필요한 값을 꺼내 에이전트를 호출하고,
결과를 상태에 저장하는 역할만 담당합니다.
"""

import logging
from workflow.state import AgentState
from agents import (
    SkinDiagnosisAgent,
    SkinAnalysisAgent,
    CareGuideAgent,
    SimulationAgent,
    IngredientAnalysisAgent,
)

logger = logging.getLogger("beauilt-agent.nodes")

# 에이전트 싱글톤 인스턴스
_diagnosis_agent = SkinDiagnosisAgent()
_analysis_agent = SkinAnalysisAgent()
_care_guide_agent = CareGuideAgent()
_simulation_agent = SimulationAgent()
_ingredient_agent = IngredientAnalysisAgent()


def diagnosis_node(state: AgentState) -> AgentState:
    """피부 진단 노드"""
    try:
        response = _diagnosis_agent.process(state.get("user_input", ""))
        state["diagnosis_result"] = response
        state["current_step"] = "diagnosis"
    except Exception as e:
        logger.error("진단 노드 오류: %s", e, exc_info=True)
        state["error"] = "진단 중 오류가 발생했습니다."
    return state


def analysis_node(state: AgentState) -> AgentState:
    """종합 분석 노드"""
    try:
        response = _analysis_agent.process(
            state.get("user_input", ""),
            diagnosis_result=state.get("diagnosis_result"),
            lifestyle_info=state.get("lifestyle_info"),
            active_products=state.get("active_products"),
        )
        state["analysis_result"] = response
        state["current_step"] = "analysis"
    except Exception as e:
        logger.error("분석 노드 오류: %s", e, exc_info=True)
        state["error"] = "분석 중 오류가 발생했습니다."
    return state


def care_guide_node(state: AgentState) -> AgentState:
    """케어 가이드 노드"""
    try:
        # 진단 결과가 없으면 먼저 간단히 진단 수행
        diagnosis_result = state.get("diagnosis_result")
        if not diagnosis_result:
            logger.debug("진단 결과 없음 — care_guide_node에서 간단 진단 수행")
            diagnosis_result = _diagnosis_agent.process(state.get("user_input", ""))
            state["diagnosis_result"] = diagnosis_result

        response = _care_guide_agent.process(
            state.get("user_input", ""),
            diagnosis_result=diagnosis_result,
            analysis_result=state.get("analysis_result"),
            active_products=state.get("active_products"),
        )
        state["care_guide"] = response
        state["current_step"] = "care_guide"
    except Exception as e:
        logger.error("케어 가이드 노드 오류: %s", e, exc_info=True)
        state["error"] = "케어 가이드 생성 중 오류가 발생했습니다."
    return state


def simulation_node(state: AgentState) -> AgentState:
    """시뮬레이션 노드"""
    try:
        response = _simulation_agent.process(
            state.get("user_input", ""),
            care_guide=state.get("care_guide"),
            diagnosis_result=state.get("diagnosis_result"),
        )
        state["simulation_result"] = response
        state["current_step"] = "simulation"
    except Exception as e:
        logger.error("시뮬레이션 노드 오류: %s", e, exc_info=True)
        state["error"] = "시뮬레이션 중 오류가 발생했습니다."
    return state


def ingredient_analysis_node(state: AgentState) -> AgentState:
    """성분 분석 노드"""
    try:
        response = _ingredient_agent.process(
            state.get("user_input", ""),
            diagnosis_result=state.get("diagnosis_result"),
            active_products=state.get("active_products"),
        )
        state["ingredient_analysis_result"] = response
        state["current_step"] = "ingredient_analysis"
    except Exception as e:
        logger.error("성분 분석 노드 오류: %s", e, exc_info=True)
        state["error"] = "성분 분석 중 오류가 발생했습니다."
    return state
