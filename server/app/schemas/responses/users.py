from typing import List, Optional, Any, Dict
from pydantic import UUID4, BaseModel, Field

from server.app.schemas.responses.department import DepartmentBase
from server.app.schemas.responses.space import SpaceBase


class UserResponse(BaseModel):
    email: str = Field(..., example="john.doe@example.com")
    username: str = Field(..., example="john.doe")
    uuid: UUID4 = Field(..., example="a3b8f042-1e16-4f0a-a8f0-421e16df0a2f")

    class Config:
        orm_mode = True


class UserInfo(BaseModel):
    email: str = Field(..., example="john.doe@example.com")
    last_name: str = Field(..., example="john.doe")
    id: UUID4 = Field(..., example="a3b8f042-1e16-4f0a-a8f0-421e16df0a2f")
    department: DepartmentBase = Field(...)
    space: SpaceBase = Field(...)
    roles: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    features: Dict[str, Any] | None

    class Config:
        orm_mode = True


class WorkspaceUserResponse(BaseModel):
    id: UUID4
    last_name: Optional[str]
    email: Optional[str]

    class Config:
        orm_mode = True

class WorkspaceUsersResponse(BaseModel):
    users: List[WorkspaceUserResponse]
