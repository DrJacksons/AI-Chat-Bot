import json
import pandas as pd
from typing import Optional, List

from data_inteligence.dataframe import DataFrame
from data_inteligence.helpers.codecs import check_filename_contain_zh
from data_inteligence.helpers.sql_sanitizer import sanitize_file_name


def convert_dataframe_to_dict(df: pd.DataFrame):
    json_data = json.loads(
        df.to_json(
            orient="split",
            date_format="iso",
            default_handler=str,
            force_ascii=False,
        )
    )
    return {"headers": json_data["columns"], "rows": json_data["data"]}


def load_df(data: dict):
    return pd.DataFrame(data["rows"], columns=data["headers"])


def read_csv(filepath: str, filterable_columns: Optional[List[str]] = None) -> DataFrame:
    # read_csv支持usecols传入callable
    if filterable_columns:
        exclude = set(filterable_columns)
        data = pd.read_csv(filepath, usecols=lambda c: c not in exclude)
    else:
        data = pd.read_csv(filepath)
    # Check file name whether contains Chinese char
    if check_filename_contain_zh(filepath):
        df = DataFrame(data)
    else:
        table = f"table_{sanitize_file_name(filepath)}"
        df = DataFrame(data, _table_name=table)
    return df


def read_excel(filepath: str, filterable_columns: Optional[List[str]] = None) -> DataFrame:
    # pandas的read_excel不支持usecols为callable，这里先读取再丢弃不需要的列
    data = pd.read_excel(filepath)
    if filterable_columns:
        data = data.drop(columns=filterable_columns, errors='ignore')
    # Check file name whether contains Chinese char
    if check_filename_contain_zh(filepath):
        df = DataFrame(data)
    else:
        table = f"table_{sanitize_file_name(filepath)}"
        df = DataFrame(data, _table_name=table)
    return df
