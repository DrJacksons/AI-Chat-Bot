from pydantic import BaseModel, Field
from uuid import UUID


class CurrentUser(BaseModel):
    id: UUID = Field(None, description="User ID")

    class Config:
        validate_assignment = True