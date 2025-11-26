from sqlalchemy import Select, select
from sqlalchemy.orm import joinedload

from server.app.models import (
    Organization,
    OrganizationMembership,
    Role,
    Permission,
    RolePermission,
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

    def get_user_me_details(self) -> User:
        return

    async def create_and_init_dummy_user(self) -> User:
        # Create user
        password = PasswordHandler.hash(config.PASSWORD)
        user = User(
            email=config.EMAIL,
            password=password,
            first_name="pandasai",
            verified=True,
            features={}
        )
        self.session.add(user)

        # Create organization
        organization = Organization(name="PandasAI", url="", is_default=True)
        self.session.add(organization)

        # Flush to ensure IDs are populated
        await self.session.flush()

        # Ensure ADMIN role within organization
        res_role = await self.session.execute(
            select(Role).filter(
                Role.organization_id == organization.id, Role.name == "ADMIN"
            )
        )
        admin_role = res_role.scalar_one_or_none()
        if admin_role is None:
            admin_role = Role(
                name="ADMIN",
                description="Organization admin role",
                organization_id=organization.id,
            )
            self.session.add(admin_role)

        # Ensure admin permission and bind to role
        res_perm = await self.session.execute(
            select(Permission).filter(Permission.code == "admin.all")
        )
        admin_all_permission = res_perm.scalar_one_or_none()
        if admin_all_permission is None:
            admin_all_permission = Permission(
                code="admin.all",
                resource="*",
                action="*",
                description="Grant all permissions within the organization",
            )
            self.session.add(admin_all_permission)

        res_rp = await self.session.execute(
            select(RolePermission).filter(
                RolePermission.role_id == admin_role.id,
                RolePermission.permission_id == admin_all_permission.id,
            )
        )
        res_rp.scalar_one_or_none()
        # if res_rp.scalar_one_or_none() is None:
        #     admin_role.permissions.append(admin_all_permission)

        # Create user-organization membership
        user_organization = OrganizationMembership(
            user_id=user.id,
            organization_id=organization.id,
            verified=True,
        )
        self.session.add(user_organization)

        # Assign ADMIN role to the membership (populates membership_role association)
        user_organization.roles.append(admin_role)

        user.organization_id = organization.id

        return user

    def _join_memberships(self, query: Select) -> Select:
        """
        Join tasks.

        :param query: Query.
        :return: Query.
        """
        return query.options(
            joinedload(User.memberships)
            .joinedload(OrganizationMembership.organization),
            joinedload(User.memberships)
            .joinedload(OrganizationMembership.roles)
            .joinedload(Role.permissions),
        )
