from enum import Enum

from pydantic.v1 import BaseSettings, PostgresDsn


class EnvironmentType(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"


class BaseConfig(BaseSettings):
    class Config:
        case_sensitive = True


class Config(BaseConfig):
    DEBUG: int = 0
    DEFAULT_LOCALE: str = "en_US"
    ENVIRONMENT: str = EnvironmentType.DEVELOPMENT
    POSTGRES_URL: PostgresDsn = (
        "postgresql+asyncpg://test:testqwer123@127.0.0.1:5432/chatbot"
    )
    OPENAI_API_KEY: str = None
    RELEASE_VERSION: str = "0.1.0"
    SHOW_SQL_ALCHEMY_QUERIES: int = 0
    SECRET_KEY: str = "super-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24
    EMAIL = "test@pandabi.ai"
    PASSWORD = "qwer@123"
    DEFAULT_ORGANIZATION = "PandaBI"
    DEFAULT_SPACE = "pandasai"


config: Config = Config()