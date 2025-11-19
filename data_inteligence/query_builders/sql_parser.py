from typing import List, Optional

import sqlglot 
from sqlglot import ParseError, parse_one, exp  
from sqlglot.optimizer.qualify_columns import quote_identifiers


class SQLParser:
    @staticmethod
    def replace_table_and_column_names(query, table_mapping):
        """
        通过用新表名或子查询替换表名来转换SQL查询。

        Args:
            query (str): Original SQL query
            table_mapping (dict): Dictionary mapping original table names to either:
                           - actual table names (str)
                           - subqueries (str)
        """
        parsed_mapping = {}
        for key, value in table_mapping.items():
            try:
                parsed_mapping[key] = parse_one(value)
            except ParseError:
                raise ValueError(f"{value} is not a valid SQL expression")
        
        def transform_node(node):
            # 处理table节点
            if isinstance(node, exp.Table):
                original_name = node.name
                if original_name in table_mapping:
                    alias = node.alias or original_name
                    mapped_value = parsed_mapping[original_name]
                    if isinstance(mapped_value, exp.Alias):
                        return exp.Subquery(
                            this=mapped_value.this.this,
                            alias=alias,
                        )
                    elif isinstance(mapped_value, exp.Column):
                        return exp.Table(this=mapped_value.this, alias=alias)
                    return exp.Subquery(this=mapped_value, alias=alias)
            return node

        # 解析sql查询
        parsed = parse_one(query)

        # 遍历AST节点并应用转换函数
        transformed = parsed.transform(transform_node)
        transformed = transformed.transform(quote_identifiers)

        # 转换为字符串
        return transformed.sql(pretty=True)

    @staticmethod
    def transpile_sql_dialect(
        query: str, to_dialect: str, from_dialect: Optional[str] = None
    ):
        """转换sql查询方言"""
        placeholder = "___PLACEHOLDER___"
        query = query.replace("%s", placeholder)
        query = (
            parse_one(query, read=from_dialect) if from_dialect else parse_one(query)
        )
        result = query.sql(dialect=to_dialect, pretty=True)

        if to_dialect == "duckdb":
            return result.replace(placeholder, "?")

        return result.replace(placeholder, "%s")

    @staticmethod
    def extract_table_names(sql_query: str, dialect: str = "postgres") -> List[str]:
        """从sql查询中提取所有表名"""
        parsed = sqlglot.parse(sql_query, dialect=dialect)
        table_names = []
        cte_names = set()

        for stmt in parsed:
            # 识别和存储CTE名称
            for cte in stmt.find_all(exp.With):
                for cte_expr in cte.expressions:
                    cte_names.add(cte_expr.alias_or_name)
            
            # 提取表名，排除CTE
            for node in stmt.find_all(exp.Table):
                if node.name not in cte_names:  # Ignore CTE names
                    table_names.append(node.name)

        return table_names
            




