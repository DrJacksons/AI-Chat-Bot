from typing import List

import sqlglot
from sqlglot import select
from sqlglot.optimizer.normalize_identifiers import normalize_identifiers
from sqlglot.optimizer.qualify_columns import quote_identifiers

from data_inteligence.data_loader.semantic_layer_schema import SemanticLayerSchema
from data_inteligence.query_builders.sql_transformation_manager import SQLTransformationManager


class BaseQueryBuilder:
    def __init__(self, schema: SemanticLayerSchema):
        self.schema = schema
        self.transformation_manager = SQLTransformationManager()

    def validate_query_builder(self):
        """验证查询构建器生成的查询是否有效"""
        try:
            sqlglot.parse_one(self.build_query())
        except Exception as error:
            raise ValueError(
                f"Failed to generate a valid SQL query from the provided schema: {error}"
            )

    def build_query(self) -> str:
        """构建查询"""
        query = select(*self._get_columns()).from_(self._get_table_expression())
       
        if self.schema.group_by:
            query = query.group_by(*[normalize_identifiers(col) for col in self.schema.group_by])
        if self._check_distinct():
            query = query.distinct()
        if self.schema.order_by:
            query = query.order_by(*self.schema.order_by)
        if self.schema.limit:
            query = query.limit(self.schema.limit)

        return query.transform(quote_identifiers).sql(pretty=True)

    def get_head_query(self, n=5):
        query = select(*self._get_columns()).from_(self._get_table_expression())

        if self._check_distinct():
            query = query.distinct()
        # Add GROUP BY if there are aggregations
        if self.schema.group_by:
            query = query.group_by(
                *[normalize_identifiers(col) for col in self.schema.group_by]
            )
        # Add LIMIT
        query = query.limit(n)

        return query.transform(quote_identifiers).sql(pretty=True)

    def get_row_count(self):
        """获取数据集的行数"""
        return select("COUNT(*)").from_(self._get_table_expression()).sql(pretty=True)

    def _get_columns(self) -> List[str]:
        """获取数据集中的所有列名"""
        if not self.schema.columns:
            return ["*"]

        columns = []
        for col in self.schema.columns:
            if col.expression:
                column_expr = col.expression
            else:
                column_expr = normalize_identifiers(col.name).sql()
            
            # 用于针对此列的任何转换
            if self.schema.transformations:
                column_expr = self.transformation_manager.apply_column_transformations(
                    column_expr, col.name, self.schema.transformations
                )
                col.alias = col.alias or normalize_identifiers(col.name).sql()

            # Add alias if specified 
            if col.alias:
                column_expr = f"{column_expr} AS {normalize_identifiers(col.alias).sql()}"
            columns.append(column_expr)
        
        return columns

    def _get_table_expression(self) -> str:
        return normalize_identifiers(self.schema.name).sql(pretty=True)

    def _check_distinct(self) -> bool:
        """检查是否需要添加 DISTINCT 关键字"""
        if not self.schema.transformations:
            return False
        
        if any(transformation.type == 'remove_duplicates' for transformation in self.schema.transformations):
            return True

        return False
    
    @staticmethod
    def check_compatible_sources(sources: List[Source]) -> bool:
        base_source = sources[0]
        return all(base_source.is_compatible_source(source) for source in sources[1:])