from typing import Any

import pandas as pd

from .base import BaseResponse


class DataFrameResponse(BaseResponse):
    def __init__(self, value: Any = None, error: str = None):
        value = self.format_value(value)
        super().__init__(value, "dataframe", error)

    def format_value(self, value):
        return pd.DataFrame(value) if isinstance(value, dict) else value
