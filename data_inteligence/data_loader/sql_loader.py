from data_inteligence.data_loader.loader import DatasetLoader
from .semantic_layer_schema import SemanticLayerSchema
from data_inteligence.dataframe.virtual_dataframe import VirtualDataFrame


class SQLDatasetLoader(DatasetLoader):
    """
    Loader for SQL-based datasets.
    """
    def __init__(self, schema: SemanticLayerSchema, dataset_path: str):
        super().__init__(schema, dataset_path)
        self._query_builder: SqlQueryBuilder = SqlQueryBuilder(schema)
    
    @property
    def query_builder(self) -> SqlQueryBuilder:
        return self._query_builder

    def load(self) -> VirtualDataFrame:
        return VirtualDataFrame(
            schema=self.schema,
            data_loader=self,
            path=self.dataset_path,
        )
    
    def load_head(self) -> pd.DataFrame:
        query = self.query_builder.get_head_query()
        return self.execute_query(query)

    def get_row_count(self) -> int:
        query = self.query_builder.get_row_count()
        result = self.execute_query(query)
        # iloc[0, 0] 用于获取查询结果的第一个行第一个列的值
        return result.iloc[0, 0]
