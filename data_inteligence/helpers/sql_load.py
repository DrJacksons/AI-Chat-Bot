import pandas as pd
import warnings
from typing import Optional
from data_inteligence.data_loader.semantic_layer_schema import SQLConnectionConfig


def load_from_mysql(
    connection_info: SQLConnectionConfig, query: str, params: Optional[list] = None
):
    import pymysql

    conn = pymysql.connect(
        host=connection_info.host,
        user=connection_info.user,
        password=connection_info.password,
        database=connection_info.database,
        port=connection_info.port,
    )
    # Suppress warnings of SqlAlchemy
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        return pd.read_sql(query, conn, params=params)


def load_from_postgres(
    connection_info: SQLConnectionConfig, query: str, params: Optional[list] = None
):
    import psycopg2

    # 如果没有指定schema，默认使用public schema
    schema = connection_info.schema or "public"
    conn = psycopg2.connect(
        host=connection_info.host,
        user=connection_info.user,
        password=connection_info.password,
        dbname=connection_info.database,
        port=connection_info.port,
        options=f"-c search_path={schema}",
    )
    # Suppress warnings of SqlAlchemy
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        return pd.read_sql(query, conn, params=params)


def load_from_oracle(
    connection_info: SQLConnectionConfig, query: str, params: Optional[list] = None
):
    import cx_Oracle

    dsn = cx_Oracle.makedsn(
        connection_info.host, connection_info.port, service_name=connection_info.database
    )
    conn = cx_Oracle.connect(
        user=connection_info.user,
        password=connection_info.password,
        dsn=dsn,
    )
    # Suppress warnings of SqlAlchemy
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        return pd.read_sql(query, conn, params=params)
