from typing import List, Optional
from urllib.parse import quote_plus

from server.app.schemas.requests.datasets import DatabaseConnectionRequestModel
from server.core.utils.dataframe import convert_dataframe_to_dict
from data_inteligence.data_loader.semantic_layer_schema import Column, SemanticLayerSchema
from data_inteligence.data_loader.sql_loader import SQLDatasetLoader


def build_connection_url(
    connection: DatabaseConnectionRequestModel, db_type: str
) -> str:
    password = quote_plus(connection.password)
    user = quote_plus(connection.username)
    host = connection.host
    port = connection.port
    database = connection.database

    if db_type == "postgres":
        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    if db_type == "mysql":
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    if db_type == "sqlserver":
        return f"mssql+pyodbc://{user}:{password}@{host}:{port}/{database}"
    if db_type == "oracle":
        return f"oracle+cx_oracle://{user}:{password}@{host}:{port}/?service_name={database}"

    return ""


class DatabaseProcessor:
    def __init__(self, db_type: str, schema: SemanticLayerSchema):
        self.db_type = db_type
        self.schema = schema
        self.loader = SQLDatasetLoader(schema, "")

    @staticmethod
    def map_mysql_to_pandas_type(mysql_type: str) -> str:
        value = mysql_type.lower()
        if value in ("tinyint", "smallint", "mediumint", "int", "integer", "bigint"):
            return "integer"
        if value in ("float", "double", "decimal"):
            return "float"
        if value in ("char", "varchar", "text", "tinytext", "mediumtext", "longtext"):
            return "string"
        if value in ("date", "datetime", "timestamp", "time", "year"):
            return "datetime"
        if value in ("boolean", "bool"):
            return "boolean"
        if value in ("binary", "varbinary", "blob", "tinyblob", "mediumblob", "longblob"):
            return "string"
        if value in ("enum", "set"):
            return "string"
        return "string"

    @staticmethod
    def map_postgresql_to_pandas_type(pg_type: str) -> str:
        value = pg_type.lower()
        if any(t in value for t in ("smallint", "integer", "bigint", "serial", "smallserial", "bigserial")):
            return "integer"
        if any(t in value for t in ("decimal", "numeric", "real", "double precision", "float")):
            return "float"
        if any(t in value for t in ("character", "char", "varchar", "text")):
            return "string"
        if any(t in value for t in ("timestamp", "date", "time", "interval")):
            return "datetime"
        if "boolean" in value:
            return "boolean"
        if any(t in value for t in ("bytea", "blob")):
            return "string"
        if any(t in value for t in ("json", "jsonb")):
            return "string"
        if "[]" in value:
            return "string"
        return "string"

    @staticmethod
    def map_oracle_to_pandas_type(oracle_type: str) -> str:
        value = oracle_type.upper()
        if value in ("NUMBER", "INTEGER", "INT", "SMALLINT"):
            return "integer"
        if value in ("FLOAT", "BINARY_FLOAT", "BINARY_DOUBLE", "REAL"):
            return "float"
        if value.startswith("NUMBER(") and "," in value:
            return "float"
        if value.startswith("NUMBER(") and "," not in value:
            return "integer"
        if value in ("VARCHAR2", "VARCHAR", "CHAR", "NCHAR", "NVARCHAR2", "CLOB", "NCLOB", "LONG"):
            return "string"
        if value in (
            "DATE",
            "TIMESTAMP",
            "TIMESTAMP WITH TIME ZONE",
            "TIMESTAMP WITH LOCAL TIME ZONE",
            "INTERVAL YEAR TO MONTH",
            "INTERVAL DAY TO SECOND",
        ):
            return "datetime"
        if value in ("BLOB", "BFILE", "RAW", "LONG RAW"):
            return "string"
        if value in ("ROWID", "UROWID"):
            return "string"
        if value == "XMLTYPE":
            return "string"
        return "string"

    def get_table_head(self):
        head = self.loader.load_head()
        return convert_dataframe_to_dict(head)

    def parse_comment(
        self,
        table_name: str,
        db_name: Optional[str] = None
    ) -> SemanticLayerSchema:
        if self.db_type == "mysql":
            return self._parse_mysql_comments(table_name, db_name)
        if self.db_type in ("postgresql", "postgres"):
            return self._parse_postgres_comments(table_name, db_name)
        if self.db_type == "oracle":
            return self._parse_oracle_comments(table_name)
        return self.schema

    def _parse_mysql_comments(
        self,
        table_name: str,
        db_name: Optional[str],
    ) -> List[Column]:
        loader = self.loader
        schema = self.schema

        table_comment_query = f"""
                SELECT table_comment
                FROM INFORMATION_SCHEMA.TABLES
                WHERE table_name = '{table_name}'
            """
        table_comment_df = loader.execute_query(table_comment_query)
        if not table_comment_df.empty and table_comment_df.iloc[0, 0]:
            schema.description = table_comment_df.iloc[0, 0]

        column_query = f"""
                SELECT
                    COLUMN_NAME, DATA_TYPE, COLUMN_COMMENT
                FROM
                    INFORMATION_SCHEMA.COLUMNS
                WHERE
                    TABLE_NAME = '{table_name}' AND TABLE_SCHEMA = '{db_name}'
            """
        columns_df = loader.execute_query(column_query)

        columns_info: List[Column] = []
        for _, row in columns_df.iterrows():
            column_name = row["COLUMN_NAME"]
            data_type = row["DATA_TYPE"]
            comment = row["COLUMN_COMMENT"]
            column_type = self.map_mysql_to_pandas_type(data_type)
            columns_info.append(
                Column(
                    name=column_name,
                    type=column_type,
                    description=comment if comment else "",
                )
            )
        schema.columns = columns_info
        return schema

    def _parse_postgres_comments(
        self,
        table_name: str,
        db_name: Optional[str],
    ) -> List[Column]:
        loader = self.loader
        schema = self.schema
        schema_name = db_name if db_name else "public"

        table_comment_query = f"""
                SELECT d.description
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                LEFT JOIN pg_description d ON d.objoid = c.oid AND d.objsubid = 0
                WHERE c.relname = '{table_name}' AND n.nspname = '{schema_name}'
            """
        table_comment_df = loader.execute_query(table_comment_query)
        if not table_comment_df.empty and table_comment_df.iloc[0, 0]:
            schema.description = table_comment_df.iloc[0, 0]

        column_query = f"""
                SELECT 
                    a.attname as column_name,
                    pg_catalog.format_type(a.atttypid, a.atttypmod) as data_type,
                    (SELECT pg_catalog.col_description(c.oid, a.attnum) FROM pg_catalog.pg_class c WHERE c.oid = a.attrelid AND c.relname = '{table_name}') as column_comment
                FROM 
                    pg_catalog.pg_attribute a
                WHERE 
                    a.attrelid = (SELECT c.oid FROM pg_catalog.pg_class c LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace WHERE c.relname = '{table_name}' AND n.nspname = '{schema_name}')
                    AND a.attnum > 0 
                    AND NOT a.attisdropped
                ORDER BY a.attnum
            """
        columns_df = loader.execute_query(column_query)

        columns_info: List[Column] = []
        for _, row in columns_df.iterrows():
            column_name = row["column_name"]
            data_type = row["data_type"]
            comment = row["column_comment"]
            column_type = self.map_postgresql_to_pandas_type(data_type)
            columns_info.append(
                Column(
                    name=column_name,
                    type=column_type,
                    description=comment if comment else "",
                )
            )
        schema.columns = columns_info
        return schema

    def _parse_oracle_comments(
        self,
        table_name: str,
    ) -> List[Column]:
        loader = self.loader
        schema = self.schema

        table_comment_query = f"""
                SELECT comments
                FROM user_tab_comments
                WHERE table_name = UPPER('{table_name}')
            """
        table_comment_df = loader.execute_query(table_comment_query)
        if not table_comment_df.empty and table_comment_df.iloc[0, 0]:
            schema.description = table_comment_df.iloc[0, 0]

        column_query = f"""
                SELECT 
                    utc.column_name,
                    utc.data_type,
                    ucc.comments as column_comment
                FROM 
                    user_tab_columns utc
                LEFT JOIN 
                    user_col_comments ucc ON utc.table_name = ucc.table_name AND utc.column_name = ucc.column_name
                WHERE 
                    utc.table_name = UPPER('{table_name}')
                ORDER BY 
                    utc.column_id
            """
        columns_df = loader.execute_query(column_query)

        columns_info: List[Column] = []
        for _, row in columns_df.iterrows():
            column_name = row["COLUMN_NAME"]
            data_type = row["DATA_TYPE"]
            comment = row["COLUMN_COMMENT"]
            column_type = self.map_oracle_to_pandas_type(data_type)
            columns_info.append(
                Column(
                    name=column_name,
                    type=column_type,
                    description=comment if comment else "",
                )
            )
        schema.columns = columns_info
        return schema
