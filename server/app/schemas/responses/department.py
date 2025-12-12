from typing import Optional
from pydantic import UUID4, BaseModel, Field


class DepartmentBase(BaseModel):
    name: str
    id: UUID4 = Field(..., example="a3b8f042-1e16-4f0a-a8f0-421e16df0a2f")
    description: Optional[str] = Field(None, example="默认工作空间（admin）")

    class Config:
        orm_mode = True
