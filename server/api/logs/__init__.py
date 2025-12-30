from fastapi import APIRouter

from .logs import logs_router

logs_router = APIRouter()
logs_router.include_router(logs_router, tags=["Logs"])

__all__ = ["logs_router"]
