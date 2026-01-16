from server.app.models import User
from server.app.repositories import UserRepository, WorkspaceRepository
from server.app.schemas.responses.users import UserInfo
from server.app.schemas.responses.space import SpaceBase
from server.app.schemas.responses.department import DepartmentBase
from server.core.controller import BaseController
from server.core.database.transactional import Propagation, Transactional
from server.core.exceptions.base import NotFoundException


class UserController(BaseController[User]):
    def __init__(
        self, user_repository: UserRepository, space_repository: WorkspaceRepository
    ):
        super().__init__(model=User, repository=user_repository)
        self.user_repository = user_repository
        self.space_repository = space_repository

    @Transactional(propagation=Propagation.REQUIRED_NEW)
    async def create_default_user(self) -> User:
        users = await self.get_all(limit=1)
        if not users:
            await self.user_repository.create_and_init_dummy_user()

    async def get_by_email(self, email: str) -> User:
        return await self.user_repository.get_by_email(email)

    async def admin(self) -> UserInfo:
        users = await self.get_all(limit=1, join_={"departments", "permissions"})
        if not users:
            raise NotFoundException(
                "No user found. Please restart the server and try again"
            )

        user = users[0]

        department = getattr(user, "department", None)
        if department is None:
            raise NotFoundException("No department found for the user")
        department_base = DepartmentBase(
            id=department.id, name=department.name, description=department.description
        )

        user_workspaces = await self.space_repository.get_user_workspaces(user)
        space = user_workspaces[0] if user_workspaces else None
        if space is None:
            spaces = await self.space_repository.get_all(limit=1)
            if not spaces:
                raise NotFoundException("No workspace found for the user")
            space = spaces[0]

        space_base = SpaceBase(id=space.id, name=space.name)

        permissions = []
        if getattr(user, "permission", None):
            permissions.append(user.permission.code)

        return UserInfo(
            email=user.email,
            username=user.username,
            id=user.id,
            department=department_base,
            space=space_base,
            permissions=permissions,
            features=user.features,
        )

    @Transactional(propagation=Propagation.REQUIRED_NEW)
    async def update_features(self, user_id, features):
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundException(
                "No user found. Please restart the server and try again"
            )

        user.features = features
        return user.features
