from fastapi import APIRouter, Depends

from server.app.controllers import AuthController
from server.app.controllers.user import UserController
from server.app.schemas.extras.token import Token
from server.app.schemas.requests.users import LoginUserRequest, RegisterUserRequest
from server.app.schemas.responses.users import UserInfo, UserResponse
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


@user_router.post("/register", response_model=UserResponse)
async def register_user(
    register_user_request: RegisterUserRequest,
    auth_controller: AuthController = Depends(Factory().get_auth_controller),
):
    created_user = await auth_controller.register(
        email=register_user_request.email,
        password=register_user_request.password,
        username=register_user_request.username,
    )
    # 显式构造 UserResponse，确保字段匹配 (User.id -> UserResponse.uuid)
    return UserResponse(
        email=created_user.email,
        username=created_user.username,
        uuid=created_user.id,
    )


@user_router.get("/me")
async def get_user(
    user: UserInfo = Depends(get_current_user),
) -> UserInfo:
    return user


@user_router.patch("/update_features")
async def update_user_routes(
    routes: Dict[str, Any],
    user_controller: UserController = Depends(Factory().get_user_controller),
    user: UserInfo = Depends(get_current_user),
):
    return await user_controller.update_features(user.id, routes)
