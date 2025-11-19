from pathlib import Path

from ..data_loader.semantic_layer_schema import SemanticLayerSchema
from .base_query_builder import BaseQueryBuilder


class LocalQueryBuilder(BaseQueryBuilder):
    def __init__(self, schema: SemanticLayerSchema, dataset_path: str):
        super().__init__(schema)
        self.dataset_path = dataset_path

    def _get_table_expression(self) -> str:
        filepath = Path(self.dataset_path) / self.schema.source.path
        abspath = filepath.resolve()
        source_type = self.schema.source.type

        if source_type == "parquet":
            return f"read_parquet('{abspath}')"
        elif source_type == "csv":
            return f"read_csv('{abspath}')"
        elif source_type == "xlsx" or source_type == "xls":
            return f"read_excel('{abspath}')"
        else:
            raise ValueError(f"Unsupported file format: {source_type}")
