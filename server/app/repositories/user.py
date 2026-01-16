from sqlalchemy import Select, select
from sqlalchemy.orm import joinedload

from server.app.models import Department, Workspace, Permission, User
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

    async def get_by_username(
        self, username: str, join_: set[str] | None = None
    ) -> User | None:
        """
        Get user by username.
        """
        query = self._query(join_)
        query = query.filter(User.username == username)
        
        if join_ is not None:
            return await self._all_unique(query)

        return await self._one_or_none(query)
        
    async def get_by_username(
        self, username: str, join_: set[str] | None = None
    ) -> User | None:
        """
        Get user by username.
        """
        query = self._query(join_)
        query = query.filter(User.username == username)

        if join_ is not None:
            return await self._all_unique(query)

        return await self._one_or_none(query)    
        
    async def get_by_username(
            self, username: str, join_: set[str] | None = None
        ) -> User | None:
            """
            Get user by username.

            :param username: Username.
            :param join_: Join relations.
            :return: User.
            """
            query = self._query(join_)
            query = query.filter(User.username == username)

            if join_ is not None:
                return await self._all_unique(query)

            return await self._one_or_none(query)

    def _join_departments(self, query: Select) -> Select:
        return query.options(joinedload(User.department))

    def _join_permissions(self, query: Select) -> Select:
        return query.options(joinedload(User.permission))

    def get_user_me_details(self) -> User:
        return

    async def create_and_init_dummy_user(self) -> User:
        # step 1: create department
        department = Department(
            name="System",
            description="系统管理部门",
            settings={},
        )
        self.session.add(department)
        # step 2: create admin permission
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

        password = PasswordHandler.hash(config.PASSWORD)
        user = User(
            email=config.EMAIL,
            password=password,
            username="admin",
            department_id=department.id,
            permission_id=admin_perm.id,
            verified=True,
            features={},
        )
        self.session.add(user)
        await self.session.flush()

        workspace = Workspace(
            name=config.DEFAULT_SPACE,
            description="测试数据",
            user_id=user.id,
        )
        self.session.add(workspace)

        return user
