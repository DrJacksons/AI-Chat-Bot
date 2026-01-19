from pydantic import EmailStr

from server.app.models import User
from server.app.repositories import (
    UserRepository,
    DepartmentRepository,
    PermissionRepository,
)
from server.app.schemas.extras.token import Token
from server.core.controller import BaseController
from server.core.database import Propagation, Transactional
from server.core.exceptions import BadRequestException, UnauthorizedException
from server.core.security import JWTHandler, PasswordHandler


class AuthController(BaseController[User]):
    def __init__(
        self,
        user_repository: UserRepository,
        department_repository: DepartmentRepository,
        permission_repository: PermissionRepository,
    ):
        super().__init__(model=User, repository=user_repository)
        self.user_repository = user_repository
        self.department_repository = department_repository
        self.permission_repository = permission_repository

    @Transactional(propagation=Propagation.REQUIRED)
    async def register(self, email: EmailStr, password: str, username: str) -> User:
        user = await self.user_repository.get_by_email(email)

        if user:
            raise BadRequestException("A user with this email already exists")

        user = await self.user_repository.get_by_username(username)

        if user:
            raise BadRequestException("A user with this username already exists")

        password = PasswordHandler.hash(password)

        departments = await self.department_repository.get_all(limit=1)
        permissions = await self.permission_repository.get_all(limit=1)

        default_department = departments[0] if departments else None
        default_perm = permissions[0] if permissions else None

        return await self.user_repository.create(
            {
                "email": email,
                "password": password,
                "username": username,
                "department_id": default_department.id if default_department else None,
                "permission_id": default_perm.id if default_perm else None,
                "verified": True,
            }
        )

    async def login(self, email: EmailStr, password: str) -> Token:
        user = await self.user_repository.get_by_email(email)

        if not user:
            raise BadRequestException("Invalid credentials")

        if not PasswordHandler.verify(password, user.password):
            raise BadRequestException("Invalid credentials")

        return Token(
            access_token=JWTHandler.encode(payload={"user_id": str(user.id)}),
            refresh_token=JWTHandler.encode(payload={"sub": "refresh_token"}),
        )

    async def refresh_token(self, access_token: str, refresh_token: str) -> Token:
        token = JWTHandler.decode(access_token)
        refresh_token = JWTHandler.decode(refresh_token)
        if refresh_token.get("sub") != "refresh_token":
            raise UnauthorizedException("Invalid refresh token")

        return Token(
            access_token=JWTHandler.encode(payload={"user_id": token.get("user_id")}),
            refresh_token=JWTHandler.encode(payload={"sub": "refresh_token"}),
        )
