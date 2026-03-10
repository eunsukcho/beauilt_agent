"""
설정 파일 모듈

pydantic-settings의 BaseSettings가 환경변수와 .env 파일을 자동으로 읽습니다.
우선순위: 환경변수 > .env 파일 > 클래스 기본값
"""

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정 클래스"""

    # OpenAI 설정
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    # 라우터는 단순 의도 분류만 하므로 저렴한 모델 사용
    openai_router_model: str = "gpt-4o-mini"

    @field_validator("openai_api_key")
    @classmethod
    def check_api_key(cls, v: str) -> str:
        if not v.strip():
            raise ValueError(
                "OPENAI_API_KEY가 설정되지 않았습니다. "
                ".env 파일 또는 환경변수에 OPENAI_API_KEY를 설정해주세요."
            )
        return v

    # 벡터 DB 설정
    vector_db_path: str = "./vector_db"

    # 웹 검색 설정 (없으면 DuckDuckGo 사용)
    tavily_api_key: str = ""

    # 접근 제어
    app_password: str = ""
    max_requests_per_session: int = 30

    # 디버그 설정
    debug: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False


# 전역 설정 인스턴스
settings = Settings()


def get_settings() -> Settings:
    return settings
