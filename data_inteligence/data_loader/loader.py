import yaml
from pathlib import Path
from abc import ABC, abstractmethod
from .semantic_layer_schema import SemanticLayerSchema


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
    def craete_loader_from_schema(cls, schema: SemanticLayerSchema, dataset_path: str):
        """Factory method to create the appropriate loader based on the dataset type."""
        return cls(schema, dataset_path)

    @classmethod
    def create_loader_from_path(cls, dataset_path: str) -> "DatasetLoader":
        """Factory method to create the appropriate loader based on the dataset type."""
        return cls(schema, dataset_path)

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