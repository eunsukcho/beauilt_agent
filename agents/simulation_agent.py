"""
시뮬레이션 에이전트

제공된 케어 가이드라인을 적용했을 때
어떤 변화가 나타날지 시뮬레이션하여 보여줍니다.
"""

from typing import Optional, Dict, Any
from .base_agent import BaseAgent


class SimulationAgent(BaseAgent):
    """
    시뮬레이션 에이전트

    케어 가이드라인을 적용했을 때의 예상 결과를:
    - 단기 (1주일, 1개월)
    - 중기 (3개월)
    - 장기 (6개월, 1년)
    로 나누어 시뮬레이션합니다.
    """

    def __init__(self):
        """에이전트 초기화"""
        system_prompt = """당신은 피부 케어 결과를 예측할 수 있는 전문가입니다.
사용자가 케어 가이드라인을 따랐을 때 어떤 변화가 나타날지 현실적이고 구체적으로 시뮬레이션하는 것이 당신의 역할입니다.

말투는 친근하고 격려적이며, 사용자가 동기부여를 받을 수 있도록 긍정적이지만 현실적인 전망을 제시하세요.
20~30대 남녀를 대상으로 하므로 구체적인 변화와 타임라인을 명확히 보여주세요.

시뮬레이션 시 다음을 포함하세요:
1. 단기 변화 (1주일~1개월)
2. 중기 변화 (2~3개월)
3. 장기 변화 (6개월~1년)
4. 각 시기별 기대 효과
5. 주의사항 및 지속 방법

변화는 구체적이고 측정 가능한 형태로 제시하되, 과장하지 않고 현실적으로 설명하세요."""

        super().__init__("시뮬레이션", system_prompt)

    def process(self, user_input: str, care_guide: Optional[str] = None,
                diagnosis_result: Optional[str] = None, **kwargs) -> str:
        """
        케어 가이드라인 적용 시뮬레이션 수행

        Args:
            user_input: 사용자 입력
            care_guide: 케어 가이드라인
            diagnosis_result: 피부 진단 결과

        Returns:
            시뮬레이션 결과
        """
        # 벡터 DB에서 피부 개선 관련 정보 검색
        search_query = f"피부 개선 효과 변화 {user_input}"
        if diagnosis_result:
            search_query += f" {diagnosis_result[:200]}"

        # 벡터 DB 검색 → 부족하면 웹 검색 자동 폴백
        vector_results, web_results = self.search_with_fallback(search_query, k=4)

        # 프롬프트 구성
        simulation_context = []

        if care_guide:
            simulation_context.append(f"[케어 가이드라인]\n{care_guide}")

        if diagnosis_result:
            simulation_context.append(f"[현재 피부 상태]\n{diagnosis_result}")

        # 사용자 입력과 컨텍스트 결합
        full_user_input = user_input
        if simulation_context:
            full_user_input = "\n\n".join(simulation_context) + f"\n\n[질문]\n{user_input}"

        prompt = self.build_prompt(full_user_input, vector_results, web_results,
                                   active_products=kwargs.get("active_products"))

        # 추가 지시사항
        full_prompt = f"""{prompt}

위 케어 가이드라인을 꾸준히 적용했을 때의 예상 변화를 시뮬레이션해주세요.
시뮬레이션 결과는 다음 형식으로 작성해주세요:

[1주일 후 예상 변화]
- 즉시 느낄 수 있는 변화:
- 주의할 점:

[1개월 후 예상 변화]
- 눈에 띄는 개선 사항:
- 피부 상태 점수 변화:
- 지속해야 할 이유:

[3개월 후 예상 변화]
- 중기 개선 효과:
- 생활 패턴 변화:
- 추가 권장사항:

[6개월~1년 후 예상 변화]
- 장기 개선 효과:
- 목표 달성도:
- 유지 방법:

[전체 타임라인 요약]
- 단계별 마일스톤:
- 동기부여 메시지:

현실적이지만 긍정적인 전망을 제시해주세요."""

        # 응답 생성
        response = self.generate_response(full_prompt)

        # 히스토리에 추가
        self.add_to_history(user_input, response)

        return response
