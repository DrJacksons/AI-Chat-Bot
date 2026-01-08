import os
import shutil
from fastapi import HTTPException, UploadFile
from server.app.models import Dataset, ConnectorType
from server.app.repositories import DatasetRepository, WorkspaceRepository
from server.core.controller import BaseController
from server.core.exceptions.base import NotFoundException
from server.app.schemas.responses.datasets import WorkspaceDatasetsResponseModel, DatasetsDetailsResponseModel
from server.app.schemas.requests.datasets import DatasetUpdateRequestModel
from server.app.schemas.responses.users import UserInfo
from server.core.utils.dataframe import read_csv, read_excel, convert_dataframe_to_dict
from server.core.database.transactional import Propagation, Transactional
from server.setting import config
from data_inteligence.constants import DEFAULT_STORGE_PATH
from data_inteligence.helpers.path import calculate_md5
from data_inteligence.data_loader.semantic_layer_schema import Source
from fastapi.responses import FileResponse


class DatasetController(BaseController[Dataset]):
    def __init__(
        self, 
        dataset_repository: DatasetRepository,
        space_repository: WorkspaceRepository
    ):
        super().__init__(model=Dataset, repository=dataset_repository)
        self.dataset_repository = dataset_repository
        self.space_repository = space_repository


    async def get_dataset_by_id(self, dataset_id: str):
        dataset = await self.dataset_repository.get_by_id(dataset_id)
        if not dataset:
            raise NotFoundException(
                "No dataset found with the given ID. Please check the ID and try again"
            )
        return dataset


    async def get_all_datasets(self) -> WorkspaceDatasetsResponseModel:
        datasets = await self.get_all()

        if not datasets:
            raise NotFoundException(
                "No dataset found. Please restart the server and try again"
            )

        return WorkspaceDatasetsResponseModel(datasets=datasets)
    

    async def get_datasets_details(self, dataset_id) -> DatasetsDetailsResponseModel:
        dataset = await self.get_dataset_by_id(dataset_id)
        return DatasetsDetailsResponseModel(dataset=dataset)
    

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_datasets(self, dataset_id, user):
        dataset = await self.get_dataset_by_id(dataset_id)
        await self.space_repository.delete_datasetspace(dataset_id, user.space.id)

        # if dataset.connector.type == "CSV":
        #     file_path = dataset.connector.config["file_path"]
        # else:
        #     # file_path = store_path / f"{dataset_id}.csv"
        #     pass
        # if not os.path.exists(file_path):
        #     raise NotFoundException(
        #         "File not found!"
        #     )
        # else:
        #     os.remove(file_path)

        return {"message": "Dataset deleted successfully"}
    

    async def update_dataset(self, dataset_id: str, dataset_update: DatasetUpdateRequestModel):
        dataset = await self.get_dataset_by_id(dataset_id)

        dataset.name = dataset_update.name
        dataset.description = dataset_update.description
        dataset = await self.dataset_repository.update_dataset(dataset=dataset)

        return {"message": "Dataset updated successfully"}
    

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_local_dataset(self, file: UploadFile, name: str, description: str, user: UserInfo):
        # 检查数据集名称是否已存在
        md5_hash = calculate_md5(file)
        existing_dataset = await self.check_duplicate_file(user.id, md5_hash)
        if existing_dataset:
            return DatasetsDetailsResponseModel(dataset=existing_dataset)
        store_path = DEFAULT_STORGE_PATH / "datasets" / user.space.name / name
        store_path.mkdir(parents=True, exist_ok=True)
        filename = file.filename
        file_path = store_path / f"{filename}"
        # 检查数据集文件夹(store_path)容量是否超出限制
        dataset_size = sum(f.stat().st_size for f in store_path.glob('**/*') if f.is_file())
        if dataset_size > config.MAX_DATASET_SIZE:
            raise HTTPException(status_code=400, detail="Dataset size exceeds the maximum limit. Please reduce the file size.")
        # Rewind the file and save it to disk
        file.file.seek(0)
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
        try:
            # 读取文件内容
            suffix_name = filename.split(".")[-1].lower()
            if suffix_name == "csv":
                df = read_csv(file_path)
            elif suffix_name in ['xlsx', 'xls']:
                df = read_excel(file_path)
            else:
                raise HTTPException(status_code=400, detail="Unsupported file format. Please upload a CSV or Excel file.")
            df.schema.source = Source(type=suffix_name, path=filename)
            column_list = df.schema.columns
            field_descriptions = [column.model_dump() for column in column_list]
            # 将DataFrame中的schema写入schema.yaml
            with open(store_path / "schema.yaml", "w", encoding="utf-8") as f:
                f.write(df.schema.to_yaml())
            head = convert_dataframe_to_dict(df)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")
        
        dataset = await self.dataset_repository.create_dataset(
            user_id=user.id,
            name=name,
            description=description,
            connector_type=ConnectorType.CSV,
            config={"file_path": str(file_path), 'file_digest': md5_hash},
            head=head,
            field_descriptions=field_descriptions,
        )
        await self.space_repository.add_dataset_to_space(workspace_id=user.space.id,dataset_id=dataset.id)

        return DatasetsDetailsResponseModel(dataset=dataset)
    

    async def create_remote_dataset(self, name: str, description: str, url: str, user: UserInfo):
        dataset = await self.dataset_repository.create_dataset(
            user_id=user.id,
            name=name,
            description=description,
            connector_type=ConnectorType.DB,
            config={"url": url},
            head=None,
        )

        await self.space_repository.add_dataset_to_space(workspace_id=user.space.id,dataset_id=dataset.id)

        return DatasetsDetailsResponseModel(dataset=dataset)


    async def download_dataset(self, dataset_id):
        await self.get_dataset_by_id(dataset_id)
        file_path = os.path.join(os.getcwd(), 'data', f"{dataset_id}.csv")

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(file_path, filename=f"{dataset_id}.csv", media_type='text/csv')

    async def check_duplicate_file(self, user_id: int, file_md5: str):
        # 检查用户是否已上传过相同内容的文件
        # logger.debug(f"Checking duplicate file for user {user_id}, MD5: {file_md5}")
        try:
            datasets = await self.dataset_repository.get_user_datasets(user_id)
            if not datasets:
                # logger.debug(f"No datasets found for user {user_id}")
                return None

            for dataset in datasets:
                if not dataset.connector:
                    # logger.debug(f"Dataset {dataset.id} has no connector")
                    continue

                config = dataset.connector.config
                if not isinstance(config, dict):
                    # logger.warning(f"Invalid config type for dataset {dataset.id}: {type(config)}")
                    continue

                stored_md5 = config.get('file_digest')
                if not stored_md5:
                    # logger.debug(f"Dataset {dataset.id} has no file_digest in config")
                    continue

                if stored_md5 == file_md5:
                    # logger.info(f"Found duplicate file: dataset {dataset.id}, MD5: {file_md5}")
                    return dataset

            # logger.debug(f"No duplicate found for MD5: {file_md5}")   
            return None
        except Exception as e:
            # logger.error(f"Error checking duplicate file: {str(e)}", exc_info=True)
            return None