import os
import shutil
import traceback
import json
from pathlib import Path
from loguru import logger
from uuid import UUID
from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, inspect, text
from server.app.models import Dataset, ConnectorType
from server.app.repositories import DatasetRepository, WorkspaceRepository
from server.core.controller import BaseController
from server.core.utils.database import build_connection_url, DatabaseProcessor
from server.core.exceptions.base import NotFoundException
from server.app.schemas.responses.datasets import (
    WorkspaceDatasetsResponseModel,
    DatasetsDetailsResponseModel,
)
from server.app.schemas.requests.datasets import (
    DatasetUpdateRequestModel,
    DatabaseConnectionRequestModel,
)
from server.app.schemas.responses.users import UserInfo
from server.core.utils.dataframe import read_csv, read_excel, convert_dataframe_to_dict
from server.core.database.transactional import Propagation, Transactional
from server.setting import config
from data_inteligence.constants import DEFAULT_STORGE_PATH, REMOTE_SOURCE_TYPES
from data_inteligence.helpers.path import calculate_md5
from data_inteligence.data_loader.semantic_layer_schema import Source, SemanticLayerSchema
from data_inteligence.data_loader.loader import DatasetLoader
from data_inteligence.data_loader.sql_loader import SQLDatasetLoader
from agent_core.agent.dataframe_agent import DataFrameAgent
from agent_core.llm.oai import OpenAIChatModel
from data_inteligence.helpers.path import find_project_root


app_logger = logger.bind(name="fastapi_app")


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
        # dataset = await self.get_dataset_by_id(dataset_id)
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
        dataset.field_descriptions = {"columns": dataset_update.field_descriptions}
        dataset.filterable_columns = {"columns": dataset_update.filterable_columns}
        dataset = await self.dataset_repository.update_dataset(dataset=dataset)

        return {"message": "Dataset updated successfully"}
    
    @Transactional(propagation=Propagation.REQUIRED)
    async def create_local_dataset(self, file: UploadFile, name: str, description: str, user: UserInfo):
        # 检查数据集名称是否已存在
        md5_hash = calculate_md5(file)
        existing_dataset = await self._check_duplicate_file(user.id, md5_hash)
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
            filterable_columns=[],
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

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_database_dataset(self, connection: DatabaseConnectionRequestModel, user: UserInfo):
        # 循环遍历tables，创建数据集
        table_names = connection.table_names or []
        if not table_names:
            try:
                table_names = await self.connect_database(connection, user)
            except HTTPException as e:
                raise HTTPException(status_code=400, detail=f"Failed to connect to database: {e.detail}")
        datasets = []
        existed_datasets = await self.dataset_repository.get_user_datasets(user.id, connector_type=ConnectorType.DB)
        existed_map: dict[tuple[str, str], Dataset] = {}
        for ds in existed_datasets:
            if not isinstance(ds.connector.config, dict):
                continue
            try:
                config_str = json.dumps(ds.connector.config, sort_keys=True)
            except TypeError:
                continue
            key = (ds.name, config_str)
            if key not in existed_map:
                existed_map[key] = ds
        for table_name in table_names:
            try:
                app_logger.info(f"开始创建表数据集: {table_name}")
                # 1、构建table的SemanticLayerSchema 
                source = {
                    "type": connection.type,
                    "connection": {
                        "host": connection.host,
                        "port": connection.port,
                        "user": connection.username,
                        "password": connection.password,
                        "database": connection.database,
                        "schema": connection.db_schema,
                    },
                    "table": table_name.lower()
                }
                initial_schema = SemanticLayerSchema(
                    name=table_name,
                    source=Source(**source)
                )
                # 2、加载表数据并获取comment
                processor = DatabaseProcessor(db_type=connection.type.lower(), schema=initial_schema)
                schema = processor.parse_comment(table_name, connection.db_schema)
                schema_dict = schema.to_dict()
                schema_config_str = json.dumps(schema_dict, sort_keys=True)
                existed = existed_map.get((table_name, schema_config_str))
                if existed:
                    app_logger.info(f"发现重复数据集: {existed.id}")
                    datasets.append(existed)
                    continue
                dataset = await self.dataset_repository.create_dataset(
                    user_id=user.id,
                    name=table_name,
                    description=schema.description,
                    connector_type=ConnectorType.DB,
                    config=schema_dict,
                    head=processor.get_table_head(),
                    field_descriptions=[c.model_dump(exclude_none=True, by_alias=True) for c in schema.columns or []],
                    filterable_columns=[],
                )
                existed_map[(table_name, schema_config_str)] = dataset
                app_logger.info(f"数据集表插入成功: {dataset.id}")
                
                # 3、将数据集添加到工作空间
                workspaces = await self.space_repository.get_user_workspaces(user)
                if workspaces:
                    workspace = workspaces[0]
                    await self.space_repository.add_dataset_to_space(
                        workspace_id=workspace.id, 
                        dataset_id=dataset.id
                    )
                    app_logger.info(f"数据集已添加到工作空间: {workspace.id}")
                else:
                    raise HTTPException(status_code=400, detail=f"用户 {user.id} 没有工作空间，请先创建")
                
                app_logger.info(f"表数据集创建完成: {table_name}")
                datasets.append(dataset)
            except Exception as e:
                app_logger.error(f"创建表数据集 {table_name} 失败: {str(e)}")
                app_logger.error(traceback.format_exc())
                raise HTTPException(status_code=500, detail=f"Failed to create dataset({table_name}): {str(e)}")
        return WorkspaceDatasetsResponseModel(datasets=datasets)

    async def connect_database(
        self, connection: DatabaseConnectionRequestModel
    ) -> list[str]:
        db_type = connection.type.lower()
        if db_type not in REMOTE_SOURCE_TYPES:
            raise HTTPException(status_code=400, detail=f"Unsupported database type: {connection.type}")

        url = build_connection_url(connection, db_type)
        try:
            engine = create_engine(url)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to create database engine: {str(e)}")

        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                inspector = inspect(conn)
                tables = inspector.get_table_names(schema=connection.db_schema)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to connect to database or query tables: {str(e)}",
            )
        finally:
            try:
                engine.dispose()
            except Exception:
                pass

        return tables

    async def download_dataset(self, dataset_id):
        await self.get_dataset_by_id(dataset_id)
        file_path = os.path.join(os.getcwd(), 'data', f"{dataset_id}.csv")

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(file_path, filename=f"{dataset_id}.csv", media_type='text/csv')

    async def _check_duplicate_file(self, user_id: int, file_md5: str):
        datasets = await self.dataset_repository.get_user_datasets(
            user_id, connector_type=ConnectorType.CSV
        )
        if not datasets:
            return None

        for dataset in datasets:
            connector = dataset.connector
            if not connector or not isinstance(connector.config, dict):
                continue

            stored_md5 = connector.config.get("file_digest")
            if stored_md5 and stored_md5 == file_md5:
                return dataset

        return None

    @Transactional(propagation=Propagation.REQUIRED)
    async def generate_dataset_summary(self, dataset_id: UUID):
        dataset = self.get_dataset_by_id(dataset_id)
        config = dataset.connector.config
        if dataset.connector.type == "CSV":
            # 读取schema.yaml文件加载Dataframe数据
            file_path = Path(find_project_root()) / config["file_path"]
            loader = DatasetLoader.create_loader_from_path(file_path.parent)
            df = loader.load()
        elif dataset.connector.type == "DB":
            if isinstance(config, dict) and "source" in config:
                schema = SemanticLayerSchema(**config)
                loader = SQLDatasetLoader(schema, "")
                df = loader.load()
    
        llm = OpenAIChatModel(
            api_key=os.getenv("OPENAI_API_KEY"), 
            base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"), 
            model=os.getenv("LLM_DEFAULT_MODEL", "gpt-4o-mini"),
            system_message = f"Please make sure to respond in the language: {app_config.DEFAULT_LOCALE}"
        )
        config = {"llm": llm}
        agent = DataFrameAgent(df, config=config)
        summary = agent.generate_dataset_summary()
        if len(dataset.description) < 30:
            dataset.description = f"{dataset.description}\n{summary}"
        else:
            dataset.description = summary
        await self.dataset_repository.update_dataset(dataset)
        return dataset.description
