from enum import Enum
from typing import Optional, Any, Dict

from pydantic.v1 import BaseSettings, PostgresDsn


class EnvironmentType(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"


class BaseConfig(BaseSettings):
    class Config:
        case_sensitive = True


class RedisConfig(BaseSettings):
    """Redis 连接配置"""
    HOST: str
    PORT: int
    DB: int
    PASSWORD: Optional[str] = None

    def get_connection_params(self) -> Dict[str, Any]:
        """获取Redis连接参数字典"""
        params = {
            'host': self.host,
            'port': self.port,
            'db': self.db,
        }
        if self.password:
            params['password'] = self.password
        return params


class Config(BaseConfig):
    DEBUG: int = 0
    DEFAULT_LOCALE: str = "en_US"
    ENVIRONMENT: str = EnvironmentType.DEVELOPMENT
    POSTGRES_URL: PostgresDsn = (
        "postgresql+asyncpg://test:testqwer123@127.0.0.1:5432/chatbot"
    )
    # Redis 配置（嵌套配置类）
    REDIS: RedisConfig = RedisConfig(
        HOST="127.0.0.1",
        PORT=6379,
        DB=0,
        PASSWORD="qwer@123",
    )
    OPENAI_API_KEY: str = None
    RELEASE_VERSION: str = "0.1.0"
    SHOW_SQL_ALCHEMY_QUERIES: int = 0
    SECRET_KEY: str = "super-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24
    EMAIL: str = "admin@wenshuai.com"
    PASSWORD: str = "qwer@123"
    DEFAULT_SPACE: str = "admin"


config: Config = Config()
