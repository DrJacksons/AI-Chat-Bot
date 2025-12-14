from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends

from server.app.controllers.role import RoleController
from server.app.schemas.requests.role import CreateRoleRequest, UpdateRoleRequest, AddPermissionRequest
from server.app.schemas.responses.role import RoleResponse
from server.core.factory import Factory
from server.core.fastapi.dependencies.current_user import get_current_user
from server.app.models import User

role_router = APIRouter()

@role_router.get("/workspace/{workspace_id}", response_model=List[RoleResponse])
async def list_workspace_roles(
    workspace_id: UUID,
    role_controller: RoleController = Depends(Factory().get_role_controller),
    user: User = Depends(get_current_user),
):
    return await role_controller.list_by_workspace(workspace_id)

@role_router.post("/", response_model=RoleResponse, status_code=201)
async def create_role(
    request: CreateRoleRequest,
    role_controller: RoleController = Depends(Factory().get_role_controller),
    user: User = Depends(get_current_user),
):
    # TODO: Add permission check
    return await role_controller.create_role(
        name=request.name,
        workspace_id=request.workspace_id,
        description=request.description
    )

@role_router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: UUID,
    role_controller: RoleController = Depends(Factory().get_role_controller),
    user: User = Depends(get_current_user),
):
    role = await role_controller.repository.get_by_id(role_id)
    # Ensure permissions are loaded if needed, though lazy='selectin' in model should handle it
    return role

@role_router.patch("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: UUID,
    request: UpdateRoleRequest,
    role_controller: RoleController = Depends(Factory().get_role_controller),
    user: User = Depends(get_current_user),
):
    # TODO: Add permission check
    return await role_controller.update_role(
        role_id=role_id,
        **request.dict(exclude_unset=True)
    )

@role_router.delete("/{role_id}", status_code=204)
async def delete_role(
    role_id: UUID,
    role_controller: RoleController = Depends(Factory().get_role_controller),
    user: User = Depends(get_current_user),
):
    # TODO: Add permission check
    await role_controller.delete_role(role_id)

@role_router.post("/{role_id}/permissions", status_code=201)
async def add_permission_to_role(
    role_id: UUID,
    request: AddPermissionRequest,
    role_controller: RoleController = Depends(Factory().get_role_controller),
    user: User = Depends(get_current_user),
):
    # TODO: Add permission check
    await role_controller.add_permission(role_id, request.permission_id)

@role_router.delete("/{role_id}/permissions/{permission_id}", status_code=204)
async def remove_permission_from_role(
    role_id: UUID,
    permission_id: UUID,
    role_controller: RoleController = Depends(Factory().get_role_controller),
    user: User = Depends(get_current_user),
):
    # TODO: Add permission check
    await role_controller.remove_permission(role_id, permission_id)
