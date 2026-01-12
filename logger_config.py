from loguru import logger
import os


def setup_loggers():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # 清除默认的 stderr handler（可选，避免控制台重复输出）
    logger.remove()

    # 1. FastAPI 主服务日志
    logger.add(
        f"{log_dir}/app.log",
        rotation="100 MB",
        retention="30 days",
        enqueue=True,          # 关键：多进程安全
        filter=lambda record: record["extra"].get("name") == "fastapi_app",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        backtrace=True,
        diagnose=True
    )

    # 2. Agent模块日志
    logger.add(
        f"{log_dir}/agent.log",
        rotation="50 MB",
        retention="7 days",
        enqueue=True,          # 同样开启多进程安全
        filter=lambda record: record["extra"].get("name") == "agent",
        format="{time:HH:mm:ss} | {level: <8} | {function}:{line} - {message}"
    )

    return logger