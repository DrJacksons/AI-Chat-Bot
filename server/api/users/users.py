from fastapi import APIRouter, Depends

from server.app.controllers import AuthController
from server.app.controllers.user import UserController
from server.app.schemas.extras.token import Token
from server.app.schemas.requests.users import LoginUserRequest, AssignRoleRequest
from server.app.schemas.responses.users import UserInfo
from server.core.factory import Factory
from server.core.fastapi.dependencies.current_user import get_current_user
from typing import Any, Dict
from uuid import UUID

user_router = APIRouter()


@user_router.post("/login")
async def login_user(
    login_user_request: LoginUserRequest,
    auth_controller: AuthController = Depends(Factory().get_auth_controller),
) -> Token:
    return await auth_controller.login(
        email=login_user_request.email, password=login_user_request.password
    )


@user_router.get("/me")
async def get_user(
    user_controller: UserController = Depends(Factory().get_user_controller),
) -> UserInfo:
    return await user_controller.me()


@user_router.patch("/update_features")
async def update_user_routes(
    routes: Dict[str, Any],
    user_controller: UserController = Depends(Factory().get_user_controller),
    user: UserInfo = Depends(get_current_user),
):
    return await user_controller.update_features(user.id, routes)

@user_router.post("/{user_id}/roles", status_code=201)
async def assign_role_to_user(
    user_id: UUID,
    request: AssignRoleRequest,
    user_controller: UserController = Depends(Factory().get_user_controller),
    current_user: UserInfo = Depends(get_current_user),
):
    # TODO: Add permission check (e.g. only admin can assign roles)
    await user_controller.assign_role(user_id, request.role_id, request.workspace_id)

@user_router.delete("/{user_id}/roles/{role_id}/workspace/{workspace_id}", status_code=204)
async def remove_role_from_user(
    user_id: UUID,
    role_id: UUID,
    workspace_id: UUID,
    user_controller: UserController = Depends(Factory().get_user_controller),
    current_user: UserInfo = Depends(get_current_user),
):
    # TODO: Add permission check
    await user_controller.remove_role(user_id, role_id, workspace_id)