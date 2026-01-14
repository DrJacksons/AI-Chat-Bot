from pydantic import BaseModel
from typing import Optional


class WorkspaceCreateRequestModel(BaseModel):
    name: str
    description: Optional[str] = None