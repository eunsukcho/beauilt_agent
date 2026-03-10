"""
LangGraph 워크플로우 그래프 구성

라우팅 전략:
- 모든 분기 결정은 router.py의 LLM이 설정한 routing_target 값을 기준으로 합니다.
- graph.py에서 별도로 키워드 매칭을 하지 않아 라우팅 로직이 한 곳에만 존재합니다.

워크플로우 흐름:
  router → diagnosis → analysis → care_guide → (END or simulation)
         ↘ ingredient_analysis → END
         ↘ care_guide → END
         ↘ simulation → END
"""

from langgraph.graph import StateGraph, END

from workflow.state import AgentState
from workflow.nodes import (
    diagnosis_node,
    analysis_node,
    care_guide_node,
    simulation_node,
    ingredient_analysis_node,
)
from workflow.router import initial_router, route_by_intent


def route_after_diagnosis(state: AgentState) -> str:
    """
    진단 완료 후 다음 노드 결정.
    router.py가 이미 결정한 routing_target을 그대로 사용합니다.
    """
    if state.get("routing_target") == "ingredient_analysis":
        return "ingredient_analysis"
    return "analysis"


def route_after_care_guide(state: AgentState) -> str:
    """
    케어 가이드 완료 후 다음 노드 결정.
    router.py가 이미 결정한 routing_target을 그대로 사용합니다.
    """
    if state.get("routing_target") == "simulation":
        return "simulation"
    return "end"


def create_workflow() -> StateGraph:
    """
    LangGraph 워크플로우 생성 및 컴파일
    """
    workflow = StateGraph(AgentState)

    # 노드 등록
    workflow.add_node("router", initial_router)
    workflow.add_node("diagnosis", diagnosis_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("care_guide", care_guide_node)
    workflow.add_node("simulation", simulation_node)
    workflow.add_node("ingredient_analysis", ingredient_analysis_node)

    # 시작점
    workflow.set_entry_point("router")

    # router → routing_target 기반 분기
    workflow.add_conditional_edges(
        "router",
        route_by_intent,
        {
            "diagnosis": "diagnosis",
            "ingredient_analysis": "ingredient_analysis",
            "care_guide": "care_guide",
            "simulation": "simulation",
        },
    )

    # diagnosis → routing_target 기반 분기 (router 결정 재사용)
    workflow.add_conditional_edges(
        "diagnosis",
        route_after_diagnosis,
        {
            "analysis": "analysis",
            "ingredient_analysis": "ingredient_analysis",
        },
    )

    # analysis → care_guide (항상)
    workflow.add_edge("analysis", "care_guide")

    # care_guide → routing_target 기반 분기
    workflow.add_conditional_edges(
        "care_guide",
        route_after_care_guide,
        {
            "simulation": "simulation",
            "end": END,
        },
    )

    # 종료 엣지
    workflow.add_edge("simulation", END)
    workflow.add_edge("ingredient_analysis", END)

    return workflow.compile()


# 전역 그래프 인스턴스
workflow_graph = create_workflow()
