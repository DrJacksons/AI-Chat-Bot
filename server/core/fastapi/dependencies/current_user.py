from fastapi import Depends, Request

from server.app.controllers.user import UserController
from server.app.schemas.responses.users import UserInfo
from server.core.factory import Factory


async def get_current_user(
    request: Request,
    user_controller: UserController = Depends(Factory().get_user_controller),
) -> UserInfo:
    # 重写，根据request中的token获取当前用户
    return await user_controller.me()