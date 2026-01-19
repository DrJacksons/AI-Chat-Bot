from fastapi import APIRouter, Depends, Query

from server.app.controllers.chat import ChatController
from server.core.fastapi.dependencies.authentication import AuthenticationRequired
from server.app.schemas.requests.chat import ChatRequest
from server.app.schemas.responses import APIResponse
from server.app.schemas.responses.chat import ChatResponse
from server.app.schemas.responses.users import UserInfo
from server.core.factory import Factory, app_logger
from server.core.fastapi.dependencies.current_user import get_current_user

chat_router = APIRouter()


@chat_router.post("/")
async def chat(
    chat_request: ChatRequest,
    chat_controller: ChatController = Depends(Factory().get_chat_controller),
    user: UserInfo = Depends(get_current_user),
) -> APIResponse[ChatResponse]:
    app_logger.info(f"Into chat interface. Request params: {chat_request}")
    response = await chat_controller.chat(user, chat_request)
    return APIResponse(data=response, message="Chat response returned successfully!")


@chat_router.post("/stream")
async def chat_stream(
    chat_request: ChatRequest,
    chat_controller: ChatController = Depends(Factory().get_chat_controller),
    user: UserInfo = Depends(get_current_user),
) -> APIResponse[ChatResponse]:
    app_logger.info(f"Into chat stream interface. Request params: {chat_request}")
    response = await chat_controller.chat_stream(user, chat_request)
    return APIResponse(data=response, message="Chat response returned successfully!")


@chat_router.get("/clarification_questions", dependencies=[Depends(AuthenticationRequired)], tags=["chat"])
async def clarification_questions(
    workspace_id: str = Query(..., description="Workspace ID"),
    chat_controller: ChatController = Depends(Factory().get_chat_controller),
):
    app_logger.info(f"Into clarification questions interface. Request params: {workspace_id}")
    response = await chat_controller.get_clarification_questions(workspace_id)
    return APIResponse(data=response, message="Get clarification questions returned successfully.")