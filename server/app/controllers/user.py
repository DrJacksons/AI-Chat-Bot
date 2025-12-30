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

    async def me(self) -> UserInfo:
        users = await self.get_all(limit=1, join_={"departments", "roles"})
        if not users:
            raise NotFoundException(
                "No user found. Please restart the server and try again"
            )

        user = users[0]

        user_workspaces = await self.space_repository.get_user_workspaces(user)
        space = user_workspaces[0] if user_workspaces else None
        if space is None:
            spaces = await self.space_repository.get_all(limit=1)
            if not spaces:
                raise NotFoundException("No workspace found for the user")
            space = spaces[0]

        space_base = SpaceBase(id=space.id, name=space.name)

        department = (
            user.departments[0] if getattr(user, "departments", None) else None
        )
        if department is None:
            raise NotFoundException("No department found for the user")
        department_base = DepartmentBase(
            id=department.id, name=department.name, description=department.description
        )

        roles = [role.name for role in getattr(user, "roles", [])]
        permissions = []
        if getattr(user, "roles", None):
            seen = set()
            for role in user.roles:
                for p in getattr(role, "permissions", []):
                    if p.code not in seen:
                        seen.add(p.code)
                        permissions.append(p.code)

        return UserInfo(
            email=user.email,
            last_name=user.last_name,
            id=user.id,
            department=department_base,
            space=space_base,
            roles=roles,
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

    @Transactional(propagation=Propagation.REQUIRED)
    async def assign_role(self, user_id: str, role_id: str, workspace_id: str) -> None:
        success = await self.user_repository.add_role(user_id, role_id, workspace_id)
        if not success:
            raise BadRequestException("Role already assigned to user in this workspace")

    @Transactional(propagation=Propagation.REQUIRED)
    async def remove_role(self, user_id: str, role_id: str, workspace_id: str) -> None:
        await self.user_repository.remove_role(user_id, role_id, workspace_id)
