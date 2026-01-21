from fastapi import APIRouter, Depends, Path
from uuid import UUID

from server.app.controllers.workspace import WorkspaceController
from server.core.factory import Factory, app_logger
from server.app.schemas.responses.users import UserInfo
from server.core.fastapi.dependencies.current_user import get_current_user
from server.app.schemas.responses.datasets import WorkspaceDatasetsBasicResponseModel
from server.app.schemas.requests.workspace import WorkspaceCreateRequestModel
from server.core.fastapi.dependencies.authentication import AuthenticationRequired


workspace_router = APIRouter()


@workspace_router.get("/list")
async def get_user_workspaces(
    workspace_controller: WorkspaceController = Depends(Factory().get_space_controller),
    user: UserInfo = Depends(get_current_user),
):
    return await workspace_controller.get_user_workspaces(user)


@workspace_router.get("/{workspace_id}/datasets", dependencies=[Depends(AuthenticationRequired)], response_model=WorkspaceDatasetsBasicResponseModel)
async def get_workspace_datasets(
    workspace_id: UUID = Path(..., description="ID of the workspace"),
    workspace_controller: WorkspaceController = Depends(Factory().get_space_controller),
):
    app_logger.info(f"Into get workspace datasets interface. Request params: workspace_id={workspace_id}")
    return await workspace_controller.get_workspace_datasets(workspace_id)


@workspace_router.get("/{workspace_id}/details", dependencies=[Depends(AuthenticationRequired)])
async def get_workspace_details(
    workspace_id: UUID = Path(..., description="ID of the workspace"),
    workspace_controller: WorkspaceController = Depends(Factory().get_space_controller),
):
    app_logger.info(f"Into get workspace details interface. Request params: workspace_id={workspace_id}")
    return await workspace_controller.get_workspace_datails(workspace_id)


@workspace_router.delete("/{workspace_id}", dependencies=[Depends(AuthenticationRequired)])
async def delete_workspace(
    workspace_id: UUID = Path(..., description="ID of the workspace"),
    workspace_controller: WorkspaceController = Depends(Factory().get_space_controller),
):
    app_logger.info(f"Into delete workspace interface. Request params: workspace_id={workspace_id}")
    return await workspace_controller.delete_workspace(workspace_id)


@workspace_router.post("/add")
async def add_workspace(
    workspace: WorkspaceCreateRequestModel,
    workspace_controller: WorkspaceController = Depends(Factory().get_space_controller),
    user: UserInfo = Depends(get_current_user),
):
    app_logger.info(f"Into add workspace interface. Request params: workspace={workspace}")
    return await workspace_controller.add_workspace(workspace, user)


@workspace_router.put("/{workspace_id}/edit", dependencies=[Depends(AuthenticationRequired)])
async def edit_workspace(
    workspace: WorkspaceCreateRequestModel,
    workspace_id: UUID = Path(..., description="ID of the workspace"),
    workspace_controller: WorkspaceController = Depends(Factory().get_space_controller),
):
    app_logger.info(f"Into edit workspace interface. Request params: workspace_id={workspace_id} workspace={workspace}")
    return await workspace_controller.edit_workspace(workspace_id, workspace)
