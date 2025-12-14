from typing import Optional, List
from pydantic import BaseModel, UUID4

class CreateRoleRequest(BaseModel):
    name: str
    description: Optional[str] = None
    workspace_id: Optional[UUID4] = None

class UpdateRoleRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class AddPermissionRequest(BaseModel):
    permission_id: UUID4
