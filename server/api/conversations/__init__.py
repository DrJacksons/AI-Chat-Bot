from fastapi import APIRouter

from .conversations import conversation_router

conversations_router = APIRouter()
conversations_router.include_router(conversation_router, tags=["Conversation"])

__all__ = ["conversations_router"]