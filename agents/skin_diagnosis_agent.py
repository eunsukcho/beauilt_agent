"""
피부 상태 진단 에이전트

사용자의 피부 상태를 진단하는 에이전트입니다.
사용자가 설명한 증상이나 상태를 바탕으로 피부 타입과 문제점을 파악합니다.
"""

from typing import Optional
from .base_agent import BaseAgent


class SkinDiagnosisAgent(BaseAgent):
    """
    피부 상태 진단 에이전트

    사용자가 설명한 피부 상태를 분석하여:
    - 피부 타입 (지성, 건성, 복합성, 민감성 등)
    - 주요 피부 문제 (트러블, 건조함, 색소침착 등)
    - 피부 상태 점수
    등을 진단합니다.
    """

    def __init__(self):
        """에이전트 초기화"""
        system_prompt = """당신은 전문 피부 관리사입니다.
사용자의 피부 상태를 정확하게 진단하는 것이 당신의 역할입니다.

말투는 친근하고 따뜻하며, 마치 직접 케어해주는 것처럼 다정하게 대화하세요.
20~30대 남녀를 대상으로 하므로 너무 딱딱하지 않고 친근한 톤을 유지하세요.

진단 시 다음 항목들을 체크하세요:
1. 피부 타입 (지성, 건성, 복합성, 민감성, 중성)
2. 주요 피부 문제 (트러블, 건조함, 색소침착, 주름, 모공, 홍조 등)
3. 피부 상태의 심각도 (1~10점 척도)
4. 개선이 필요한 부분

진단 결과는 사용자가 이해하기 쉽게 설명하고, 격려의 말을 함께 전달하세요."""

        super().__init__("피부진단", system_prompt)

    def process(self, user_input: str, **kwargs) -> str:
        """
        피부 상태 진단 수행

        Args:
            user_input: 사용자가 설명한 피부 상태

        Returns:
            진단 결과 및 조언
        """
        # 벡터 DB 검색 → 부족하면 웹 검색 자동 폴백
        vector_results, web_results = self.search_with_fallback(
            f"피부 타입 진단 {user_input}", k=3
        )

        # 프롬프트 구성
        prompt = self.build_prompt(user_input, vector_results, web_results,
                                   active_products=kwargs.get("active_products"))

        # 추가 지시사항
        full_prompt = f"""{prompt}

위 정보를 바탕으로 사용자의 피부 상태를 진단해주세요.
진단 결과는 다음 형식으로 작성해주세요:

[피부 타입]
- 타입:
- 특징:

[주요 피부 문제]
- 문제점:
- 심각도:

[종합 진단]
- 현재 상태 요약:
- 개선 포인트:

[격려 메시지]
- 따뜻한 격려와 함께 다음 단계를 안내해주세요."""

        # 응답 생성
        response = self.generate_response(full_prompt)

        # 히스토리에 추가
        self.add_to_history(user_input, response)

        return response
