from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload

from server.app.models import Department, User, UserDepartment
from server.core.repository import BaseRepository
from server.core.database import Propagation, Transactional


class DepartmentRepository(BaseRepository[Department]):
    
    @Transactional(propagation=Propagation.REQUIRED)
    async def add_department(self, name: str, description: str = None, settings: dict = None) -> Department:
        """
        Create a new department.
        """
        department = Department(name=name, description=description, settings=settings)
        self.session.add(department)
        return department

    async def get_by_name(self, name: str) -> Optional[Department]:
        """
        Get department by name.
        """
        query = select(Department).where(Department.name == name)
        result = await self.session.execute(query)
        return result.scalars().first()

    @Transactional(propagation=Propagation.REQUIRED)
    async def update_department(self, department_id: UUID, **kwargs) -> Optional[Department]:
        """
        Update department details.
        """
        department = await self.get_by_id(department_id)
        if not department:
            return None
            
        for key, value in kwargs.items():
            # Only update attributes that exist on the model
            if hasattr(department, key):
                setattr(department, key, value)
        
        self.session.add(department)
        return department

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_department(self, department_id: UUID) -> bool:
        """
        Delete department by ID.
        """
        department = await self.get_by_id(department_id)
        if not department:
            return False
            
        await self.session.delete(department)
        return True

    @Transactional(propagation=Propagation.REQUIRED)
    async def add_user(self, department_id: UUID, user_id: UUID) -> bool:
        """
        Add a user to the department.
        """
        # Check if department exists
        department = await self.get_by_id(department_id)
        if not department:
            return False

        # Check if relation already exists
        stmt = select(UserDepartment).where(
            UserDepartment.department_id == department_id,
            UserDepartment.user_id == user_id
        )
        result = await self.session.execute(stmt)
        if result.scalars().first():
            return False # Already exists

        user_dept = UserDepartment(department_id=department_id, user_id=user_id)
        self.session.add(user_dept)
        return True

    @Transactional(propagation=Propagation.REQUIRED)
    async def remove_user(self, department_id: UUID, user_id: UUID) -> None:
        """
        Remove a user from the department.
        """
        stmt = delete(UserDepartment).where(
            UserDepartment.department_id == department_id,
            UserDepartment.user_id == user_id
        )
        await self.session.execute(stmt)

    async def get_users(self, department_id: UUID) -> List[User]:
        """
        Get all users in a department.
        """
        stmt = select(User).join(UserDepartment).where(UserDepartment.department_id == department_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    def _join_users(self, query: select) -> select:
        """
        Join users relationship for query options.
        """
        return query.options(joinedload(Department.users))
