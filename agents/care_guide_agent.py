"""
케어 가이드라인 제공 에이전트

사용자의 피부 상태와 종합 분석 결과를 바탕으로
구체적인 피부 케어 가이드라인을 제공합니다.
"""

from typing import Optional, Dict, Any
from .base_agent import BaseAgent


class CareGuideAgent(BaseAgent):
    """
    케어 가이드라인 제공 에이전트

    피부 진단과 분석 결과를 바탕으로:
    - 일일 루틴
    - 주간 케어
    - 제품 추천
    - 주의사항
    등을 포함한 실용적인 가이드라인을 제공합니다.
    """

    def __init__(self):
        """에이전트 초기화"""
        system_prompt = """당신은 실전 경험이 풍부한 피부 관리 전문가입니다.
사용자의 피부 상태에 맞는 구체적이고 실용적인 케어 가이드라인을 제공하는 것이 당신의 역할입니다.

말투는 친근하고 실용적이며, 사용자가 바로 적용할 수 있도록 구체적으로 안내하세요.
20~30대 남녀를 대상으로 하므로 현실적이고 지속 가능한 루틴을 제안하세요.

가이드라인 제공 시 다음을 포함하세요:
1. 아침/저녁 스킨케어 루틴
2. 제품 사용 순서와 방법
3. 주간/월간 케어 팁
4. 피해야 할 행동
5. 예상 소요 시간과 예산 고려사항

가이드라인은 단계별로 명확하게 제시하고, 각 단계의 이유를 설명해주세요."""

        super().__init__("케어가이드", system_prompt)

    def process(self, user_input: str, diagnosis_result: Optional[str] = None,
                analysis_result: Optional[str] = None, **kwargs) -> str:
        """
        케어 가이드라인 생성

        Args:
            user_input: 사용자 입력
            diagnosis_result: 피부 진단 결과
            analysis_result: 종합 분석 결과

        Returns:
            케어 가이드라인
        """
        # 벡터 DB에서 케어 방법 관련 정보 검색
        search_query = f"피부 케어 루틴 가이드 {user_input}"
        if diagnosis_result:
            search_query += f" {diagnosis_result[:200]}"

        # 벡터 DB 검색 → 부족하면 웹 검색 자동 폴백
        vector_results, web_results = self.search_with_fallback(search_query, k=5)

        # 프롬프트 구성
        guide_context = []

        if diagnosis_result:
            guide_context.append(f"[피부 진단 결과]\n{diagnosis_result}")

        if analysis_result:
            guide_context.append(f"[종합 분석 결과]\n{analysis_result}")

        # 사용자 입력과 컨텍스트 결합
        full_user_input = user_input
        if guide_context:
            full_user_input = "\n\n".join(guide_context) + f"\n\n[요청사항]\n{user_input}"

        prompt = self.build_prompt(full_user_input, vector_results, web_results,
                                   active_products=kwargs.get("active_products"))

        # 추가 지시사항
        full_prompt = f"""{prompt}

위 정보를 바탕으로 사용자에게 맞는 실용적인 케어 가이드라인을 작성해주세요.
가이드라인은 다음 형식으로 작성해주세요:

[아침 루틴]
1. 단계별 케어 방법:
2. 추천 제품 유형:
3. 소요 시간:

[저녁 루틴]
1. 단계별 케어 방법:
2. 추천 제품 유형:
3. 소요 시간:

[주간 케어 팁]
- 특별 케어 (마스크, 팩 등):
- 주의사항:

[제품 선택 가이드]
- 피부 타입에 맞는 성분:
- 피해야 할 성분:

[예산 고려사항]
- 필수 제품:
- 선택 제품:

각 단계의 이유와 효과를 간단히 설명해주세요."""

        # 응답 생성
        response = self.generate_response(full_prompt)

        # 히스토리에 추가
        self.add_to_history(user_input, response)

        return response
