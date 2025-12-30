from fastapi import APIRouter, Depends

from server.app.controllers.chat import ChatController
from server.app.schemas.requests.chat import ChatRequest
from server.app.schemas.responses import APIResponse
from server.app.schemas.responses.chat import ChatResponse
from server.app.schemas.responses.users import UserInfo
from server.core.factory import Factory
from server.core.fastapi.dependencies.current_user import get_current_user

chat_router = APIRouter()


@chat_router.post("/")
async def chat(
    chat_request: ChatRequest,
    chat_controller: ChatController = Depends(Factory().get_chat_controller),
    user: UserInfo = Depends(get_current_user),
) -> APIResponse[ChatResponse]:
    response = await chat_controller.chat(user, chat_request)
    return APIResponse(data=response, message="Chat response returned successfully!")


@chat_router.post("/stream")
async def chat_stream(
    chat_request: ChatRequest,
    chat_controller: ChatController = Depends(Factory().get_chat_controller),
    user: UserInfo = Depends(get_current_user),
) -> APIResponse[ChatResponse]:
    response = await chat_controller.chat_stream(user, chat_request)
    return APIResponse(data=response, message="Chat response returned successfully!")
