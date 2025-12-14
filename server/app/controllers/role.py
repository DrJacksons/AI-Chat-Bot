from typing import List, Optional
from uuid import UUID

from server.app.models import Role
from server.app.repositories import RoleRepository
from server.core.controller import BaseController
from server.core.database.transactional import Propagation, Transactional
from server.core.exceptions.base import NotFoundException, BadRequestException

class RoleController(BaseController[Role]):
    def __init__(self, role_repository: RoleRepository):
        super().__init__(model=Role, repository=role_repository)
        self.role_repository = role_repository

    async def list_by_workspace(self, workspace_id: UUID) -> List[Role]:
        return await self.role_repository.list_by_workspace_id(workspace_id)

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_role(
        self,
        name: str,
        workspace_id: UUID | None,
        description: str | None = None,
        is_system_role: bool = False,
    ) -> Role:
        if workspace_id:
            existing = await self.role_repository.get_by_name_in_workspace(workspace_id, name)
            if existing:
                raise BadRequestException(f"Role {name} already exists in workspace")
        
        return await self.role_repository.create_role(name, workspace_id, description, is_system_role)

    @Transactional(propagation=Propagation.REQUIRED)
    async def update_role(self, role_id: UUID, **kwargs) -> Role:
        role = await self.role_repository.get_by_id(role_id)
        if not role:
            raise NotFoundException(f"Role with id {role_id} not found")
        
        for key, value in kwargs.items():
            if hasattr(role, key) and value is not None:
                setattr(role, key, value)
        
        # BaseController doesn't have explicit update, so we rely on session tracking changes or add explicit add
        # Since we fetched it from session, modifying it should be enough if we commit/flush, but adding is safer
        # But wait, BaseRepository doesn't expose update. 
        # Usually fetching and modifying attributes on an attached object updates it on flush/commit.
        # We can call repository.session.add(role) to be sure.
        self.repository.session.add(role)
        return role

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_role(self, role_id: UUID) -> None:
        role = await self.role_repository.get_by_id(role_id)
        if not role:
            raise NotFoundException(f"Role with id {role_id} not found")
        await self.role_repository.delete(role)

    @Transactional(propagation=Propagation.REQUIRED)
    async def add_permission(self, role_id: UUID, permission_id: UUID) -> None:
        await self.role_repository.add_permission(role_id, permission_id)

    @Transactional(propagation=Propagation.REQUIRED)
    async def remove_permission(self, role_id: UUID, permission_id: UUID) -> None:
        await self.role_repository.remove_permission(role_id, permission_id)
