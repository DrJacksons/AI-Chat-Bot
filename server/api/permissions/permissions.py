from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from server.app.controllers.permission import PermissionController
from server.app.schemas.requests.permission import CreatePermissionRequest, UpdatePermissionRequest
from server.app.schemas.responses.permission import PermissionBase
from server.app.schemas.responses.users import UserInfo
from server.core.factory import Factory
from server.core.fastapi.dependencies.current_user import get_current_user

permission_router = APIRouter()


@permission_router.post("/", response_model=PermissionBase, status_code=201)
async def create_permission(
    permisson_request: CreatePermissionRequest,
    permission_controller: PermissionController = Depends(Factory().get_permission_controller),
    user: UserInfo = Depends(get_current_user),
):
    """
    Create a new permission.
    """
    if not user.permissions.code == "admin.all":
        raise HTTPException(status_code=403, detail="Only admin user can create permissions")
    return await permission_controller.create_permission(permisson_request)


@permission_router.get("/", response_model=List[PermissionBase])
async def list_permissions(
    permission_controller: PermissionController = Depends(Factory().get_permission_controller),
):
    """
    List all permissions.
    """
    return await permission_controller.list_permissions()


@permission_router.patch("/{permission_id}", response_model=PermissionBase)
async def update_permission(
    permission_id: UUID,
    request: UpdatePermissionRequest,
    permission_controller: PermissionController = Depends(Factory().get_permission_controller),
    user: UserInfo = Depends(get_current_user),
):
    """
    Update a permission.
    """
    if not user.permissions.code == "admin.all":
        raise HTTPException(status_code=403, detail="Only admin user can update permissions")
    return await permission_controller.update_permission(permission_id, request)


@permission_router.delete("/{permission_id}", status_code=204)
async def delete_permission(
    permission_id: UUID,
    permission_controller: PermissionController = Depends(Factory().get_permission_controller),
    user: UserInfo = Depends(get_current_user),
):
    """
    Delete a permission.
    """
    if not user.permissions.code == "admin.all":
        raise HTTPException(status_code=403, detail="Only admin user can delete permissions")
    await permission_controller.delete_permission(permission_id)
