from pydantic import BaseModel
from typing import Optional, List
from fastapi import UploadFile, File


class DatasetUpdateRequestModel(BaseModel):
    name: str
    description: Optional[str] = None
    field_descriptions: Optional[List[dict]] = None
    filterable_columns: Optional[List[str]] = None


class DatasetCreateRequestModel(BaseModel):
    name: str
    description: Optional[str] = None
    file: UploadFile = File(...),


class DatabaseConnectionRequestModel(BaseModel):
    type: str
    host: str
    port: int
    username: str
    password: str
    database: str
    db_schema: Optional[str] = None
    table_names: Optional[list[str]] = None
