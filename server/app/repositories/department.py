from typing import List
from server.app.models import Department
from server.core.repository import BaseRepository
from server.core.database import Propagation, Transactional
from sqlalchemy import func
from sqlalchemy.future import select


class DepartmentRepository(BaseRepository):
    
    @Transactional(propagation=Propagation.REQUIRED)
    def add_department(self, name: str, description: str = None, settings: dict = None) -> Department:
        department = Department(name=name, description=description, settings=settings)
        self.session.add(department)
        return department
