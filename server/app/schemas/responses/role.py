from typing import Optional, List
from pydantic import BaseModel, UUID4, Field
from datetime import datetime

class PermissionResponse(BaseModel):
    id: UUID4
    code: str
    resource: Optional[str]
    action: Optional[str]
    description: Optional[str]
    
    class Config:
        from_attributes = True

class RoleResponse(BaseModel):
    id: UUID4
    name: str
    description: Optional[str]
    workspace_id: Optional[UUID4]
    is_system_role: bool
    created_at: Optional[datetime]
    permissions: List[PermissionResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
