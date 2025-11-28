from sqlalchemy import Select
from sqlalchemy.orm import joinedload
from server.app.models import (
    Department,
    Role,
    Permission,
    RolePermission,
    User,
)
from server.core.repository import BaseRepository


class RoleRepository(BaseRepository[Role]):
    pass
