import logging
from datetime import datetime
from fastapi import BackgroundTasks, Request


class Logging:
    def __init__(self, background_task: BackgroundTasks, request: Request):
        self.request = request
        self.method = request.method
        self.path = request.url.path
        self.client = request.client.host
        background_task.add_task(self._send_log)

    async def _send_log(self):
        logger = logging.getLogger("fastapi.request")
        if not logger.handlers:
            handler = logging.FileHandler("server/logs/fastapi_requests.log", encoding="utf-8")
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        
        logger.info(
            "%s %s from %s at %s",
            self.method,
            self.path,
            self.client,
            datetime.utcnow().isoformat(),
        )