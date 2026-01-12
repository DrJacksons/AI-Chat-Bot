from fastapi import APIRouter

from server.api.monitoring import monitoring_router
from server.api.chat import chats_router
from server.api.datasets import datasets_router
from server.api.conversations import conversations_router
from server.api.users import users_router
from server.api.workspace import workspace_router
from server.api.departments import departments_router
from server.api.permissions import permissions_router

api_router = APIRouter()
api_router.include_router(monitoring_router, prefix="/monitoring")
api_router.include_router(chats_router, prefix="/chat")
api_router.include_router(datasets_router, prefix="/datasets")
api_router.include_router(conversations_router, prefix="/conversations")
api_router.include_router(users_router, prefix="/users")
api_router.include_router(workspace_router, prefix="/workspace")
api_router.include_router(departments_router, prefix="/departments")
api_router.include_router(permissions_router, prefix="/permission")


__all__ = ["api_router"]
