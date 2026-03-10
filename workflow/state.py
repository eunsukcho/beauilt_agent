"""
LangGraph 상태 정의

워크플로우에서 사용하는 상태를 정의합니다.
"""

from typing import TypedDict, Optional, List, Dict, Any


class AgentState(TypedDict):
    """
    에이전트 워크플로우 상태

    모든 노드에서 공유되는 상태 정보를 저장합니다.
    """
    # 사용자 입력
    user_input: str

    # 각 에이전트의 결과
    diagnosis_result: Optional[str]
    analysis_result: Optional[str]
    care_guide: Optional[str]
    simulation_result: Optional[str]
    ingredient_analysis_result: Optional[str]

    # 웹 검색 결과
    web_search_results: Optional[List[Dict[str, Any]]]

    # 현재 단계
    current_step: str

    # 최종 응답
    final_response: Optional[str]

    # 추가 컨텍스트 (생활 패턴 등)
    lifestyle_info: Optional[Dict[str, Any]]

    # 대화 히스토리 (이전 대화 맥락 유지)
    conversation_history: Optional[List[Dict[str, str]]]

    # 라우팅 정보
    routing_target: Optional[str]  # 초기 라우터가 결정한 타겟 노드
    user_intent: Optional[str]  # 사용자 의도 (diagnosis, ingredient_analysis, care_guide, simulation)

    # 사용자 등록 제품 목록
    active_products: Optional[List[Dict[str, Any]]]

    # 에러 정보
    error: Optional[str]
