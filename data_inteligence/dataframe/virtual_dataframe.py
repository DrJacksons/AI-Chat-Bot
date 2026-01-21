from __future__ import annotations

from typing import TYPE_CHECKING, Optional
import pandas as pd

from data_inteligence.dataframe.base import DataFrame

if TYPE_CHECKING:
    from data_inteligence.data_loader.sql_loader import SQLDatasetLoader
    

class VirtualDataFrame(DataFrame):
    _metadata = [
        "_agent",
        "_column_hash",
        "_head",
        "_loader",
        "config",
        "head",
        "path",
        "schema",
    ]

    def __init__(self, *args, **kwargs):
        self._loader: Optional[SQLDatasetLoader] = kwargs.pop("data_loader", None)
        if not self._loader:
            raise NameError("Data loader is required for virtualization!")
        self._head = None

        super().__init__(
            *args,
            **kwargs,
        )

    def head(self):
        if self._head is None:
            self._head = self._loader.load_head()
        return self._head

    def sample(self):
        """
        随机获取10条数据，用于llm提取description
        1、随机获取10条数据，要求包含有空值的行，无空值的行
        2、对表格数据的空值进行处理
        3、若某些行的内容过多，请截断，小于200字
        """
        # 随机获取10条数据，要求包含有空值的行和无空值的行
        df = self._loader
        nan_rows = df[df.isnull().any(axis=1)]  # 含空值的行
        non_nan_rows = df[~df.isnull().any(axis=1)]  # 无空值的行

        # 判断是否有含空值的行，如果没有则只从非空行中抽样
        if not nan_rows.empty:
            num_has_nan = min(4, len(nan_rows))  # 最多取5条含空值的行
            has_nan_sample = nan_rows.sample(n=num_has_nan)
        else:
            has_nan_sample = pd.DataFrame()  # 空DataFrame

        # 无论有没有空值，都从非空行中抽样
        num_no_nan = min(10 - len(has_nan_sample), len(non_nan_rows))  # 补足到10条
        no_nan_sample = non_nan_rows.sample(n=num_no_nan) if num_no_nan > 0 else pd.DataFrame()

        # 合并并打乱顺序
        sample_df = pd.concat([has_nan_sample, no_nan_sample]).sample(frac=1).reset_index(drop=True)

        # 空值处理：统一转为字符串避免 dtype 冲突
        for column in sample_df.columns:
            col = sample_df[column]
            sample_df.loc[:, column] = col.astype('string').fillna('None')

        # 如果某些行的内容过多，请截断，小于200字
        sample_df = sample_df.map(lambda x: x[:200] if isinstance(x, str) else x)
        # 展示全部
        pd.set_option('display.max_columns', None)
        return sample_df

    @property
    def rows_count(self) -> int:
        return self._loader.get_row_count()

    @property
    def query_builder(self):
        return self._loader.query_builder

    def execute_sql_query(self, query: str) -> pd.DataFrame:
        return self._loader.execute_query(query)

