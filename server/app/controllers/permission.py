from typing import List, Optional
from uuid import UUID

from server.app.models import Permission
from server.app.repositories import PermissionRepository
from server.app.schemas.requests.permission import CreatePermissionRequest, UpdatePermissionRequest
from server.app.schemas.responses.permission import PermissionBase
from server.core.controller import BaseController
from server.core.database.transactional import Propagation, Transactional
from server.core.exceptions import BadRequestException, NotFoundException


class PermissionController(BaseController[Permission]):
    def __init__(self, permission_repository: PermissionRepository):
        super().__init__(model=Permission, repository=permission_repository)
        self.permission_repository = permission_repository

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_permission(self, request: CreatePermissionRequest) -> Permission:
        existing = await self.permission_repository.get_by_code(request.code)
        if existing:
            raise BadRequestException(f"Permission with code {request.code} already exists")
        
        return await self.permission_repository.create_permission(
            code=request.code,
            resource=request.resource,
            action=request.action,
            description=request.description
        )

    async def list_permissions(self) -> List[Permission]:
        return await self.permission_repository.list_all()

    @Transactional(propagation=Propagation.REQUIRED)
    async def update_permission(self, permission_id: UUID, request: UpdatePermissionRequest) -> Permission:
        permission = await self.permission_repository.get_by_id(permission_id)
        if not permission:
            raise NotFoundException(f"Permission with id {permission_id} not found")

        if request.code:
             # Check for duplicate code if code is being updated
            existing = await self.permission_repository.get_by_code(request.code)
            if existing and existing.id != permission_id:
                raise BadRequestException(f"Permission with code {request.code} already exists")
            permission.code = request.code
            
        if request.resource is not None:
            permission.resource = request.resource
        if request.action is not None:
            permission.action = request.action
        if request.description is not None:
            permission.description = request.description
            
        return permission

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_permission(self, permission_id: UUID) -> None:
        permission = await self.permission_repository.get_by_id(permission_id)
        if not permission:
            raise NotFoundException(f"Permission with id {permission_id} not found")
        
        await self.permission_repository.delete(permission)
