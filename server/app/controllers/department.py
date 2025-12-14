from typing import Optional, List
from uuid import UUID

from server.app.models import Department
from server.app.repositories import DepartmentRepository
from server.core.controller import BaseController
from server.core.database.transactional import Propagation, Transactional
from server.core.exceptions.base import NotFoundException, BadRequestException

class DepartmentController(BaseController[Department]):
    def __init__(self, department_repository: DepartmentRepository):
        super().__init__(model=Department, repository=department_repository)
        self.department_repository = department_repository

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_department(self, name: str, description: str = None, settings: dict = None) -> Department:
        existing = await self.department_repository.get_by_name(name)
        if existing:
            raise BadRequestException(f"Department with name {name} already exists")
        
        return await self.department_repository.add_department(name, description, settings)

    @Transactional(propagation=Propagation.REQUIRED)
    async def update_department(self, department_id: UUID, **kwargs) -> Department:
        department = await self.department_repository.update_department(department_id, **kwargs)
        if not department:
            raise NotFoundException(f"Department with id {department_id} not found")
        return department

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_department(self, department_id: UUID) -> bool:
        result = await self.department_repository.delete_department(department_id)
        if not result:
            raise NotFoundException(f"Department with id {department_id} not found")
        return True

    @Transactional(propagation=Propagation.REQUIRED)
    async def add_user(self, department_id: UUID, user_id: UUID) -> bool:
        result = await self.department_repository.add_user(department_id, user_id)
        if not result:
             # This could mean dept not found or user already in dept. 
             # For simplicity assuming dept exists check is done in repo
             department = await self.department_repository.get_by_id(department_id)
             if not department:
                 raise NotFoundException(f"Department with id {department_id} not found")
             # If department exists, it means user is already added
             raise BadRequestException("User already in department")
        return True

    @Transactional(propagation=Propagation.REQUIRED)
    async def remove_user(self, department_id: UUID, user_id: UUID) -> None:
        await self.department_repository.remove_user(department_id, user_id)
