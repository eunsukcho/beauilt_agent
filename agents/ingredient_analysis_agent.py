"""
성분별 적합도 분석 에이전트

사용자의 피부 타입과 상태에 따라
각 성분의 적합도를 분석하고 추천합니다.

데이터 소스 우선순위:
1. 벡터 DB (data/ingredient_cards/ 의 성분 카드)
2. DuckDuckGo 웹 검색 (벡터 DB 결과가 부족할 때 자동 폴백)
3. LLM 자체 지식 (GPT-4o의 화장품 성분 학습 데이터)
"""

from typing import Optional, List
from .base_agent import BaseAgent


class IngredientAnalysisAgent(BaseAgent):
    """
    성분별 적합도 분석 에이전트

    사용자의 피부 상태를 바탕으로:
    - 추천 성분
    - 주의 성분
    - 성분별 적합도 점수
    - 성분 조합 팁
    등을 제공합니다.
    """

    def __init__(self):
        """에이전트 초기화"""
        system_prompt = """당신은 화장품 성분 전문가입니다.
사용자의 피부 타입과 상태에 맞는 성분을 분석하고 추천하는 것이 당신의 역할입니다.

말투는 친근하고 전문적이며, 복잡한 성분 정보를 쉽게 이해할 수 있도록 설명하세요.
20~30대 남녀를 대상으로 하므로 실용적이고 구체적인 정보를 제공하세요.

성분 분석 시 다음을 포함하세요:
1. 피부 타입별 추천 성분
2. 피부 문제별 효과적인 성분
3. 주의해야 할 성분
4. 성분 조합 팁
5. 제품 선택 시 체크리스트

성분의 효능과 작용 원리를 간단히 설명하고, 실제 제품 선택에 도움이 되도록 구체적으로 안내하세요."""

        super().__init__("성분분석", system_prompt)

    def process(self, user_input: str, diagnosis_result: Optional[str] = None,
                ingredient_list: Optional[List[str]] = None, **kwargs) -> str:
        """
        성분별 적합도 분석 수행

        벡터 DB(성분 카드) → 웹 검색 순으로 정보를 수집한 뒤 LLM이 분석합니다.

        Args:
            user_input: 사용자 입력 (성분 질문 또는 제품 정보)
            diagnosis_result: 피부 진단 결과
            ingredient_list: 분석할 성분 리스트 (선택사항)

        Returns:
            성분 분석 결과
        """
        # 검색 쿼리 구성: 성분명이 있으면 포함
        search_query = f"화장품 성분 효능 {user_input}"
        if ingredient_list:
            search_query += f" {' '.join(ingredient_list)}"
        if diagnosis_result:
            search_query += f" {diagnosis_result[:200]}"

        # 벡터 DB 검색 → 부족하면 웹 검색 자동 폴백
        vector_results, web_results = self.search_with_fallback(search_query, k=5)

        # 프롬프트 컨텍스트 구성
        analysis_context = []

        if diagnosis_result:
            analysis_context.append(f"[피부 진단 결과]\n{diagnosis_result}")

        if ingredient_list:
            analysis_context.append(f"[분석 요청 성분]\n{', '.join(ingredient_list)}")

        full_user_input = user_input
        if analysis_context:
            full_user_input = "\n\n".join(analysis_context) + f"\n\n[질문]\n{user_input}"

        prompt = self.build_prompt(full_user_input, vector_results, web_results,
                                   active_products=kwargs.get("active_products"))

        full_prompt = f"""{prompt}

위 정보를 바탕으로 사용자의 피부에 맞는 성분을 분석해주세요.
분석 결과는 다음 형식으로 작성해주세요:

[추천 성분 TOP 5]
1. 성분명:
   - 적합도: /10점
   - 효능:
   - 추천 이유:
   - 주의사항:

[주의 성분]
- 피해야 할 성분:
- 이유:
- 대체 성분:

[성분 조합 가이드]
- 함께 사용하면 좋은 성분:
- 함께 사용하면 안 되는 성분:
- 사용 순서:

[제품 선택 체크리스트]
- 확인해야 할 성분:
- 피해야 할 성분:
- 성분 함량 고려사항:

각 성분의 효능과 작용 원리를 간단히 설명해주세요."""

        response = self.generate_response(full_prompt)
        self.add_to_history(user_input, response)

        return response
