from fastapi import APIRouter
from .departments import department_router


departments_router = APIRouter()
departments_router.include_router(department_router, tags=["Department"])

__all__ = ["departments_router"]
