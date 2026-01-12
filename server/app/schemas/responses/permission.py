from typing import Optional
from pydantic import UUID4, BaseModel, Field


class PermissionBase(BaseModel):
    code: str
    id: UUID4 = Field(..., example="a3b8f042-1e16-4f0a-a8f0-421e16df0a2f")
    resource: Optional[str] = Field(None)
    action: Optional[str] = Field(None)
    description: Optional[str] = Field(None, example="系统管理部")

    class Config:
        from_attributes = True