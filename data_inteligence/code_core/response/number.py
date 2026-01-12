from typing import Any

from .base import BaseResponse


class NumberResponse(BaseResponse):
    """
    Class for handling numerical responses.
    """

    def __init__(self, value: Any = None, error: str = None):
        super().__init__(value, "number", error)
