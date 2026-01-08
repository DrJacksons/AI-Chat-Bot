from fastapi import APIRouter

from .chat import chat_router

chats_router = APIRouter()
chats_router.include_router(chat_router, tags=["Chat"])

__all__ = ["chats_router"]