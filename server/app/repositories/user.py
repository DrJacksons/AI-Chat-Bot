from sqlalchemy import Select, select
from sqlalchemy.orm import joinedload

from server.app.models import (
    Department,
    Workspace,
    Role,
    Permission,
    RolePermission,
    UserRole,
    User,
)
from server.setting import config
from server.core.repository import BaseRepository
from server.core.security.password import PasswordHandler


class UserRepository(BaseRepository[User]):
    """
    User repository provides all the database operations for the User model.
    """

    async def get_by_email(
        self, email: str, join_: set[str] | None = None
    ) -> User | None:
        """
        Get user by email.

        :param email: Email.
        :param join_: Join relations.
        :return: User.
        """
        query = self._query(join_)
        query = query.filter(User.email == email)

        if join_ is not None:
            return await self._all_unique(query)

        return await self._one_or_none(query)

    def _join_departments(self, query: Select) -> Select:
        return query.options(joinedload(User.departments))

    def _join_roles(self, query: Select) -> Select:
        return query.options(
            joinedload(User.roles).joinedload(Role.permissions)
        )

    async def add_role(self, user_id: str, role_id: str, workspace_id: str) -> bool:
        """
        Assign a role to a user in a specific workspace.
        """
        stmt = select(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id,
            UserRole.workspace_id == workspace_id,
        )
        result = await self.session.execute(stmt)
        if result.scalars().first():
            return False  # Already exists

        user_role = UserRole(
            user_id=user_id, role_id=role_id, workspace_id=workspace_id
        )
        self.session.add(user_role)
        return True

    async def remove_role(self, user_id: str, role_id: str, workspace_id: str) -> None:
        """
        Remove a role from a user in a specific workspace.
        """
        # Find the specific UserRole entry
        stmt = select(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id,
            UserRole.workspace_id == workspace_id,
        )
        result = await self.session.execute(stmt)
        user_role = result.scalars().first()
        
        if user_role:
            await self.session.delete(user_role)

    def get_user_me_details(self) -> User:
        return

    async def create_and_init_dummy_user(self) -> User:
        password = PasswordHandler.hash(config.PASSWORD)
        user = User(
            email=config.EMAIL,
            password=password,
            last_name="admin",
            first_name="admin",
            verified=True,
            features={},
        )
        self.session.add(user)

        department = Department(
            name="System",
            description="系统管理部门",
            settings={},
        )
        self.session.add(department)

        await self.session.flush()

        workspace = Workspace(
            name=config.DEFAULT_SPACE,
            description="管理员工作空间，具有所有权限",
            user_id=user.id,
            department_id=department.id,
        )
        self.session.add(workspace)

        # Ensure admin permission exists
        res_perm = await self.session.execute(
            select(Permission).where(Permission.code == "admin.all")
        )
        admin_perm = res_perm.scalars().first()
        if admin_perm is None:
            admin_perm = Permission(
                code="admin.all",
                resource="*",
                action="*",
                description="系统管理员权限：允许所有操作",
            )
            self.session.add(admin_perm)

        await self.session.flush()

        # Create ADMIN role in the workspace if missing
        res_role = await self.session.execute(
            select(Role).where(
                Role.workspace_id == workspace.id, Role.name == "ADMIN"
            )
        )
        admin_role = res_role.scalars().first()
        if admin_role is None:
            admin_role = Role(
                name="ADMIN",
                description="系统管理员角色",
                workspace_id=workspace.id,
                is_system_role=True,
            )
            self.session.add(admin_role)

        await self.session.flush()

        # Bind permission to role (idempotent)
        res_rp = await self.session.execute(
            select(RolePermission).where(
                RolePermission.role_id == admin_role.id,
                RolePermission.permission_id == admin_perm.id,
            )
        )
        if res_rp.scalars().first() is None:
            self.session.add(
                RolePermission(role_id=admin_role.id, permission_id=admin_perm.id)
            )

        # Assign role to user within the workspace via association table
        res_ur = await self.session.execute(
            select(UserRole).where(
                UserRole.user_id == user.id,
                UserRole.role_id == admin_role.id,
                UserRole.workspace_id == workspace.id,
            )
        )
        if res_ur.scalars().first() is None:
            self.session.add(
                UserRole(
                    user_id=user.id,
                    role_id=admin_role.id,
                    workspace_id=workspace.id,
                )
            )

        return user
