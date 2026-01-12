from fastapi import APIRouter
from .permissions import permission_router

permissions_router = APIRouter()
permissions_router.include_router(permission_router, tags=["Permission"])

__all__ = ["permissions_router"]
