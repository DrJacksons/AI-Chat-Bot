from __future__ import annotations

from typing import TYPE_CHECKING, Optional
import pandas as pd
import hashlib
from pandas._typing import Axes, Dtype
from data_inteligence.data_loader.semantic_layer_schema import SemanticLayerSchema, Source, Column

if TYPE_CHECKING:
    from agent_core.agent.dataframe_agent import DataFrameAgent


class DataFrame(pd.DataFrame):
    """
    数据框类，继承自pandas.DataFrame，用于存储和操作数据。

    Attributes:
        name (Optional[str]): Name of the dataframe
        description (Optional[str]): Description of the dataframe
        schema (Optional[SemanticLayerSchema]): Schema definition for the dataframe
        config (Config): Configuration settings
    """
    _metadata = [
        "_agent",
        "_column_hash",
        "_table_name",
        "config",
        "path",
        "schema",
    ]

    def __init__(
        self,
        data=None,
        columns: Axes | None = None,
        index: Axes | None = None,
        dtype: Dtype | None = None,
        copy: bool | None = None,
        **kwargs,
    ) -> None:
        _schema: Optional[SemanticLayerSchema] = kwargs.pop("schema", None)
        _path: Optional[str] = kwargs.pop("path", None)
        _table_name: Optional[str] = kwargs.pop("table_name", None)

        super().__init__(
            data=data,
            columns=columns,
            index=index,
            dtype=dtype,
            copy=copy
        )

        if _table_name:
            self._table_name = _table_name

        self._column_hash = self._calculate_column_hash()
        self.schema = _schema or DataFrame.get_default_schema(self)
        self.path = _path
        self._agent: Optional[DataFrameAgent] = None

    def __repr__(self) -> str:
        """返回Dataframe的字符串表示"""
        name_str = f"name='{self.schema.name}'"
        desc_str = (
            f"description='{self.schema.description}'"
            if self.schema.description
            else ""
        )
        metadata = ", ".join(filter(None, [name_str, desc_str]))

        return f"AI DataFrame({metadata})\n{super().__repr__()}"

    def _calculate_column_hash(self) -> str:
        """计算数据框列的哈希值"""
        column_string = ",".join(self.columns)
        return hashlib.md5(column_string.encode()).hexdigest()

    @property
    def column_hash(self):
        return self._column_hash

    @property
    def type(self) -> str:
        return "pd.DataFrame"

    @property
    def rows_count(self) -> int:
        return len(self)
    
    @property
    def columns_count(self) -> int:
        return len(self.columns)
    
    def get_dialect(self) -> str:
        source = self.schema.source or None
        if source:
            dialect = "duckdb" if source.type in LOCAL_SOURCE_TYPES else source.type
        else:
            dialect = "postgres"

        return dialect

    def get_head(self):
        return self.head()

    @staticmethod
    def get_column_type(column_dtype) -> Optional[str]:
        """根据数据框列的dtype返回对应的类型"""
        if pd.api.types.is_string_dtype(column_dtype):
            return "string"
        elif pd.api.types.is_integer_dtype(column_dtype):
            return "integer"
        elif pd.api.types.is_float_dtype(column_dtype):
            return "float"
        elif pd.api.types.is_datetime64_any_dtype(column_dtype):
            return "datetime"
        elif pd.api.types.is_bool_dtype(column_dtype):
            return "boolean"
        else:
            return None

    @classmethod
    def get_default_schema(cls, dataframe) -> SemanticLayerSchema:
        columns_list = [
            Column(name=str(name), type=DataFrame.get_column_type(dtype))
            for name, dtype in dataframe.dtypes.items()
        ]

        table_name = getattr(
            dataframe, "_table_name", f"table_{dataframe._column_hash}"
        )

        return SemanticLayerSchema(
            name=table_name,
            source=Source(
                type="parquet",
                path="data.parquet",
            ),
            columns=columns_list,
        )
