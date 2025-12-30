from .base import BaseResponse


class ErrorResponse(BaseResponse):
    """
    Class for handling error responses.
    """

    def __init__(
        self,
        value="抱歉，我无法回答你的问题。请重试。",
        last_code_executed: str = None,
        error: str = None,
    ):
        super().__init__(value, "error", last_code_executed, error)
