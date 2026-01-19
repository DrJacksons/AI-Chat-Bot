from loguru import logger
from .factory import Factory

app_logger = logger.bind(name="fastapi_app")

__all__ = ["Factory", "app_logger"]
