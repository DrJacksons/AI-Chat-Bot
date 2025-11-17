from typing import List

import sqlglot
from sqlglot import select
from sqlglot.optimizer.normalize_identifiers import normalize_identifiers
from sqlglot.optimizer.qualify_columns import quote_identifiers

from data_inteligence.data_loader.semantic_layer_schema import SemanticLayerSchema


class BaseQueryBuilder:
    def __init__(self, schema: SemanticLayerSchema):
        self.schema = schema

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
                column_expr