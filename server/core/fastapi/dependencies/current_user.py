from fastapi import Depends, Request

from server.app.controllers.user import UserController
from server.app.schemas.responses.users import UserInfo
from server.app.schemas.responses.space import SpaceBase
from server.app.schemas.responses.department import DepartmentBase
from server.core.exceptions import NotFoundException
from server.core.factory import Factory
from server.core.fastapi.dependencies.authentication import AuthenticationRequiredException
from server.core.security import JWTHandler


async def get_current_user(
    request: Request,
    user_controller: UserController = Depends(Factory().get_user_controller),
) -> UserInfo:
    authorization: str | None = request.headers.get("Authorization")
    token: str | None = None

    if authorization:
        try:
            scheme, credentials = authorization.split(" ")
        except ValueError:
            raise AuthenticationRequiredException()

        if scheme.lower() != "bearer" or not credentials:
            raise AuthenticationRequiredException()

        token = credentials

    if token is None:
        session_token = request.cookies.get("session_id") or request.headers.get(
            "session_id"
        )
        if session_token:
            token = session_token

    if token is None:
        raise AuthenticationRequiredException()

    payload = JWTHandler.decode(token)
    user_id = payload.get("user_id")

    if not user_id:
        raise AuthenticationRequiredException()

    user = await user_controller.get_by_id(user_id, join_={"departments", "permissions"})
    user = user[0]

    if user.department.id is None:
        raise NotFoundException("No department found for the user")

    department_base = DepartmentBase(
        id=user.department.id, name=user.department.name, description=user.department.description
    )

    user_workspaces = await user_controller.space_repository.get_user_workspaces(user)
    space = user_workspaces[0] if user_workspaces else None
    if space is None:
        spaces = await user_controller.space_repository.get_all(limit=1)
        if not spaces:
            raise NotFoundException("No workspace found for the user")
        space = spaces[0]

    space_base = SpaceBase(id=space.id, name=space.name)

    permissions: list[str] = []
    if getattr(user, "permission", None):
        permissions.append(user.permission.code)

    return UserInfo(
        email=user.email,
        last_name=user.last_name,
        id=user.id,
        department=department_base,
        space=space_base,
        permissions=permissions,
        features=user.features,
    )
