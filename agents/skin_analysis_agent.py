"""
전체 상황 진단 에이전트

피부 상태 진단 결과를 바탕으로 전체적인 피부 상황을 종합적으로 분석합니다.
여러 요인(생활습관, 환경, 스트레스 등)을 고려하여 종합 진단을 제공합니다.
"""

from typing import Optional, Dict, Any
from .base_agent import BaseAgent


class SkinAnalysisAgent(BaseAgent):
    """
    전체 상황 진단 에이전트

    피부 진단 결과와 사용자의 생활 패턴, 환경 등을 종합하여
    전체적인 피부 상황을 분석하고 원인을 파악합니다.
    """

    def __init__(self):
        """에이전트 초기화"""
        system_prompt = """당신은 경험이 풍부한 피부 관리 전문가입니다.
사용자의 피부 상태와 생활 패턴을 종합적으로 분석하여 전체적인 상황을 파악하는 것이 당신의 역할입니다.

말투는 친근하고 전문적이며, 사용자가 자신의 피부를 이해할 수 있도록 도와주세요.
20~30대 남녀를 대상으로 하므로 이해하기 쉽고 공감대를 형성할 수 있는 표현을 사용하세요.

분석 시 다음을 고려하세요:
1. 피부 타입과 문제점의 연관성
2. 생활 패턴이 피부에 미치는 영향
3. 환경 요인 (계절, 지역, 직업 등)
4. 스트레스와 피부 건강의 관계
5. 전체적인 피부 건강 수준

분석 결과는 사용자가 자신의 피부를 이해하고 개선할 수 있도록 명확하고 구체적으로 제시하세요.

주의사항:
- 답변 마지막을 "피부과 방문을 권장합니다" 같은 문구로 끝내지 마세요.
- 대신 "생활 습관 중 바꿔보고 싶은 부분이 있나요?" 처럼 자연스럽게 대화를 이어가세요.
- 사용자가 계속 질문할 수 있도록 열린 흐름을 유지하세요."""

        super().__init__("전체분석", system_prompt)

    def process(self, user_input: str, diagnosis_result: Optional[str] = None,
                lifestyle_info: Optional[Dict[str, Any]] = None, **kwargs) -> str:
        """
        전체 상황 종합 분석 수행

        Args:
            user_input: 사용자 입력 (추가 정보나 질문)
            diagnosis_result: 피부 진단 에이전트의 진단 결과
            lifestyle_info: 생활 패턴 정보 (선택사항)
                예: {"수면시간": "6시간", "스트레스": "높음", "운동": "주3회"}

        Returns:
            종합 분석 결과
        """
        # 벡터 DB에서 관련 정보 검색
        search_query = f"피부 분석 종합 {user_input}"
        if diagnosis_result:
            search_query += f" {diagnosis_result[:200]}"  # 진단 결과 일부 포함

        # 벡터 DB 검색 → 부족하면 웹 검색 자동 폴백
        vector_results, web_results = self.search_with_fallback(search_query, k=5)

        # 프롬프트 구성
        analysis_context = []

        if diagnosis_result:
            analysis_context.append(f"[피부 진단 결과]\n{diagnosis_result}")

        if lifestyle_info:
            lifestyle_text = "\n".join([f"- {k}: {v}" for k, v in lifestyle_info.items()])
            analysis_context.append(f"[생활 패턴 정보]\n{lifestyle_text}")

        # 사용자 입력과 컨텍스트 결합
        full_user_input = user_input
        if analysis_context:
            full_user_input = "\n\n".join(analysis_context) + f"\n\n[추가 질문]\n{user_input}"

        prompt = self.build_prompt(full_user_input, vector_results, web_results,
                                   active_products=kwargs.get("active_products"))

        # 추가 지시사항
        full_prompt = f"""{prompt}

위 정보를 바탕으로 사용자의 피부 상황을 종합적으로 분석해주세요.
분석 결과는 다음 형식으로 작성해주세요:

[종합 분석]
- 현재 피부 상태의 핵심 요약:
- 주요 원인 분석:
- 개선 가능성:

[생활 패턴 영향 분석]
- 긍정적인 요인:
- 개선이 필요한 요인:

[전체적인 평가]
- 피부 건강 수준 (1~10점):
- 우선순위가 높은 개선 사항:

[다음 단계 안내]
- 구체적인 개선 방향을 제시해주세요."""

        # 응답 생성
        response = self.generate_response(full_prompt)

        # 히스토리에 추가
        self.add_to_history(user_input, response)

        return response
