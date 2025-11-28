from fastapi import APIRouter

from .chat import chat_router

chat_router = APIRouter()
chat_router.include_router(chat_router, tags=["Chat"])

__all__ = ["chat_router"]