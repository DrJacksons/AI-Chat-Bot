from fastapi import APIRouter, Depends, Path, status, UploadFile, File, Form
from typing import Optional
from server.app.controllers.datasets import DatasetController
from server.app.schemas.responses.datasets import WorkspaceDatasetsResponseModel, DatasetsDetailsResponseModel
from server.core.factory import Factory, app_logger
from uuid import UUID
from server.app.schemas.responses import APIResponse
from server.core.fastapi.dependencies.authentication import AuthenticationRequired
from server.app.schemas.requests.datasets import DatasetUpdateRequestModel, DatabaseConnectionRequestModel
from server.app.schemas.responses.users import UserInfo
from server.core.fastapi.dependencies.current_user import get_current_user
from fastapi.responses import FileResponse

dataset_router = APIRouter()

@dataset_router.get("/", dependencies=[Depends(AuthenticationRequired)], response_model=WorkspaceDatasetsResponseModel)
async def get_all_datasets(datasets_controller: DatasetController = Depends(Factory().get_datasets_controller)):
    return await datasets_controller.get_all_datasets()


@dataset_router.get("/{dataset_id}", dependencies=[Depends(AuthenticationRequired)], response_model=DatasetsDetailsResponseModel)
async def get_dataset(
        dataset_id: UUID = Path(..., description="ID of the dataset"),
        datasets_controller: DatasetController = Depends(Factory().get_datasets_controller)
    ):
    return await datasets_controller.get_datasets_details(dataset_id)


@dataset_router.post("/")
async def create_local_dataset(
        name: str = Form(...),
        description: Optional[str] = Form(None),
        file: UploadFile = File(...),
        user: UserInfo = Depends(get_current_user),
        datasets_controller: DatasetController = Depends(Factory().get_datasets_controller)
    ):
    app_logger.info(f"Into create local dataset interface. Request params: {name}, {description}, {file.filename}")
    return await datasets_controller.create_local_dataset(file, name, description, user)


@dataset_router.post("/remote")
async def create_remote_dataset(
        name: str = Form(...),
        description: Optional[str] = Form(None),
        url: str = Form(...),
        user: UserInfo = Depends(get_current_user),
        datasets_controller: DatasetController = Depends(Factory().get_datasets_controller)
    ):
    return await datasets_controller.create_remote_dataset(name, description, url, user)


@dataset_router.post("/db/create")
async def create_database_dataset(
        connection: DatabaseConnectionRequestModel = Form(...),
        user: UserInfo = Depends(get_current_user),
        datasets_controller: DatasetController = Depends(Factory().get_datasets_controller)
    ):
    app_logger.info(f"Into create database dataset interface. Request params: {connection}")
    return await datasets_controller.create_database_dataset(connection, user)

    
@dataset_router.delete("/{dataset_id}")
async def delete_datasets(
        dataset_id: UUID = Path(..., description="ID of the dataset"),
        user: UserInfo = Depends(get_current_user),
        datasets_controller: DatasetController = Depends(Factory().get_datasets_controller)
    ):
    app_logger.info(f"Into delete dataset interface. Request params: {dataset_id}")
    return await datasets_controller.delete_datasets(dataset_id, user)


@dataset_router.put("/{dataset_id}", status_code=status.HTTP_200_OK)
async def update_datasets(
        dataset_update: DatasetUpdateRequestModel,
        dataset_id: UUID = Path(..., description="ID of the dataset"),
        datasets_controller: DatasetController = Depends(Factory().get_datasets_controller)
    ):
    return await datasets_controller.update_dataset(dataset_id, dataset_update)


@dataset_router.get("/download/{dataset_id}", response_class=FileResponse, status_code=status.HTTP_200_OK)
async def download_dataset(
        dataset_id: UUID = Path(..., description="ID of the dataset"),
        datasets_controller: DatasetController = Depends(Factory().get_datasets_controller)
    ):
    return await datasets_controller.download_dataset(dataset_id)


@dataset_router.post("/db/connect", dependencies=[Depends(AuthenticationRequired)], response_model=APIResponse[dict])
async def connect_database(
        connection: DatabaseConnectionRequestModel = Form(...),
        datasets_controller: DatasetController = Depends(Factory().get_datasets_controller)
    ) -> APIResponse[dict]:
    app_logger.info(f"Into connect database interface. Request params: {connection}")
    tables = await datasets_controller.connect_database(connection)
    return APIResponse(data={"tables": tables})
