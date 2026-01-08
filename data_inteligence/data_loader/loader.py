import yaml
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Optional
from .semantic_layer_schema import SemanticLayerSchema
from data_inteligence.exceptions import MethodNotImplementedError
from data_inteligence.dataframe.base import DataFrame
from data_inteligence.constants import LOCAL_SOURCE_TYPES


class DatasetLoader(ABC):
    def __init__(self, schema: SemanticLayerSchema, dataset_path: str):
        self.schema = schema
        self.dataset_path = dataset_path

    @property
    @abstractmethod
    def query_builder(self) -> str:
        """必须由子类实现的抽象属性"""
        pass

    @abstractmethod
    def execute_query(self, query: str, params: Optional[list] = None):
        pass

    @classmethod
    def create_loader_from_schema(
        cls, schema: SemanticLayerSchema, dataset_path: str
    ) -> "DatasetLoader":
        """
        Factory method to create the appropriate loader based on the dataset type.
        """

        if schema.source and schema.source.type in LOCAL_SOURCE_TYPES:
            from data_inteligence.data_loader.local_loader import LocalDatasetLoader

            loader = LocalDatasetLoader(schema, dataset_path)
        elif schema.view:
            from data_inteligence.data_loader.view_loader import ViewDatasetLoader

            loader = ViewDatasetLoader(schema, dataset_path)
        else:
            from data_inteligence.data_loader.sql_loader import SQLDatasetLoader

            loader = SQLDatasetLoader(schema, dataset_path)

        loader.query_builder.validate_query_builder()
        return loader

    @classmethod
    def create_loader_from_path(cls, dataset_path: str) -> "DatasetLoader":
        """
        Factory method to create the appropriate loader based on the dataset type.
        """
        schema = cls._read_schema_file(dataset_path)
        return DatasetLoader.create_loader_from_schema(schema, dataset_path)

    @staticmethod
    def _read_schema_file(dataset_path: str) -> SemanticLayerSchema:
        schema_path = Path(dataset_path) / "schema.yaml"

        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        schema_file = schema_path.read_text()
        raw_schema = yaml.safe_load(schema_file)
        return SemanticLayerSchema(**raw_schema)


    def load(self) -> DataFrame:
        """
        Load data into a DataFrame based on the provided dataset path or schema.

        Returns:
            DataFrame: A new DataFrame instance with loaded data.
        """
        raise MethodNotImplementedError("Loader未实例化")