"""
뷰티 데일리팁 챗봇 메인 실행 파일 (CLI)

LangGraph 워크플로우를 사용하여 대화를 관리합니다.
"""

import logging
import sys

from workflow.graph import workflow_graph
from workflow.chat_handler import (
    DEFAULT_RESPONSE,
    build_initial_state,
    extract_response,
    handle_followup_question,
    is_followup_question,
    run_workflow,
    update_context,
    validate_user_input,
)

# 로깅 설정
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("beauilt-agent.main")

GOODBYE_MESSAGE = "이용해 주셔서 감사합니다! 건강한 피부 되세요!"
EXIT_COMMANDS = {"종료", "exit", "quit", "bye"}


class BeautyChatbot:
    """뷰티 데일리팁 챗봇 (CLI 버전)"""

    def __init__(self):
        self.workflow = workflow_graph
        self.conversation_history: list = []
        self.previous_context: dict = {
            "diagnosis_result": None,
            "analysis_result": None,
            "care_guide": None,
        }

        print("=" * 50)
        print("뷰티 데일리팁 챗봇에 오신 것을 환영합니다!")
        print("=" * 50)
        print("\n다음 기능을 이용하실 수 있습니다:")
        print("1. 피부 상태 진단")
        print("2. 전체 상황 분석")
        print("3. 케어 가이드라인 제공")
        print("4. 시뮬레이션 (변화 예측)")
        print("5. 성분 분석")
        print("\n팁: 피부 진단을 하시면 자동으로 분석과 가이드까지 제공됩니다!")
        print("팁: 이전 대화 맥락을 기억하므로 추가 질문도 가능합니다!")
        print("\n'종료' 또는 'exit'를 입력하시면 프로그램이 종료됩니다.")
        print("=" * 50)

    def process_user_input(self, user_input: str) -> str:
        """
        사용자 입력을 처리하고 응답 반환

        Args:
            user_input: 사용자 입력 (검증 전)

        Returns:
            AI 응답 문자열
        """
        # 입력 검증
        try:
            user_input = validate_user_input(user_input)
        except ValueError as e:
            return str(e)

        # 종료 명령
        if user_input.lower() in EXIT_COMMANDS:
            return GOODBYE_MESSAGE

        has_history = bool(self.conversation_history)
        is_followup = is_followup_question(user_input, has_history)

        initial_state = build_initial_state(
            user_input,
            self.previous_context,
            self.conversation_history,
        )

        try:
            last_node_output = run_workflow(self.workflow, initial_state)

            if not last_node_output:
                return DEFAULT_RESPONSE

            # 오류 처리
            if last_node_output.get("error"):
                logger.warning("워크플로우 오류: %s", last_node_output["error"])
                return "죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."

            # 추가 질문 처리
            if is_followup:
                answer = handle_followup_question(
                    user_input,
                    self.previous_context,
                    [{"role": "user" if i % 2 == 0 else "assistant", "content": m}
                     for conv in self.conversation_history[-3:]
                     for i, m in enumerate([conv["user"], conv["assistant"]])],
                )
                self.conversation_history.append({"user": user_input, "assistant": answer})
                return answer

            # 응답 추출
            response = extract_response(last_node_output)
            if response:
                update_context(self.previous_context, last_node_output)
                self.conversation_history.append({"user": user_input, "assistant": response})
                return response

            return DEFAULT_RESPONSE

        except Exception as e:
            logger.error("워크플로우 실행 오류: %s", e, exc_info=True)
            return "죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."

    def run(self):
        """챗봇 대화 루프"""
        while True:
            try:
                user_input = input("\n사용자: ").strip()
                if not user_input:
                    continue

                response = self.process_user_input(user_input)
                print(f"\n피부관리사: {response}\n")

                if response == GOODBYE_MESSAGE:
                    break

            except KeyboardInterrupt:
                print("\n\n프로그램을 종료합니다.")
                break
            except Exception as e:
                logger.error("대화 루프 오류: %s", e, exc_info=True)
                print("\n오류가 발생했습니다. 다시 시도해주세요.")


def main():
    """메인 함수"""
    try:
        chatbot = BeautyChatbot()
        chatbot.run()
    except Exception as e:
        logger.critical("프로그램 시작 실패: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
