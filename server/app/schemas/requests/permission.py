from typing import Optional
from pydantic import BaseModel

class CreatePermissionRequest(BaseModel):
    code: str
    resource: Optional[str] = None
    action: Optional[str] = None
    description: str

class UpdatePermissionRequest(BaseModel):
    code: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    description: Optional[str] = None
