from typing import List
from sqlalchemy import select

from server.app.models import Permission
from server.core.repository import BaseRepository


class PermissionRepository(BaseRepository[Permission]):
    async def get_by_code(self, code: str) -> Permission | None:
        result = await self.session.execute(
            select(Permission).where(Permission.code == code)
        )
        return result.scalars().first()

    async def list_all(self) -> List[Permission]:
        result = await self.session.execute(select(Permission))
        return result.scalars().all()

    async def create_permission(
        self,
        code: str,
        resource: str | None = None,
        action: str | None = None,
        description: str | None = None,
    ) -> Permission:
        permission = Permission(
            code=code,
            resource=resource,
            action=action,
            description=description,
        )
        self.session.add(permission)
        await self.session.flush()
        return permission

