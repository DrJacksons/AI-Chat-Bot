from typing import List
from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload
from server.app.models import (
    Role,
    Permission,
    RolePermission,
)
from server.core.repository import BaseRepository


class RoleRepository(BaseRepository[Role]):
    async def list_by_workspace_id(self, workspace_id: str) -> List[Role]:
        # 枚举指定工作空间下的所有角色
        result = await self.session.execute(
            select(Role).where(Role.workspace_id == workspace_id)
        )
        return result.scalars().all()

    async def get_by_name_in_workspace(self, workspace_id: str, name: str) -> Role | None:
        result = await self.session.execute(
            select(Role).where(
                Role.workspace_id == workspace_id,
                Role.name == name,
            )
        )
        return result.scalars().first()

    async def create_role(
        self,
        name: str,
        workspace_id: str | None,
        description: str | None = None,
        is_system_role: bool = False,
    ) -> Role:
        role = Role(
            name=name,
            workspace_id=workspace_id,
            description=description,
            is_system_role=is_system_role,
        )
        self.session.add(role)
        await self.session.flush()
        return role

    async def add_permission(self, role_id: str, permission_id: str) -> None:
        rp = RolePermission(role_id=role_id, permission_id=permission_id)
        self.session.add(rp)

    async def remove_permission(self, role_id: str, permission_id: str) -> None:
        await self.session.execute(
            delete(RolePermission).where(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id,
            )
        )

    def _join_permissions(self, query):
        return query.options(joinedload(Role.permissions))
