from typing import Optional, Dict, Any
from pydantic import BaseModel

class CreateDepartmentRequest(BaseModel):
    name: str
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class UpdateDepartmentRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
