from fastapi import APIRouter

from server.api.monitoring import monitoring_router

api_router = APIRouter()
api_router.include_router(monitoring_router, prefix="/monitoring")


__all__ = ["api_router"]