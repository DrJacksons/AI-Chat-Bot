import os
import time
from pathlib import Path
from typing import List
from loguru import logger

from agent_core.agent.dataframe_agent import DataFrameAgent
from data_inteligence.helpers.path import find_project_root
from data_inteligence.data_loader.semantic_layer_schema import SemanticLayerSchema
from data_inteligence.data_loader.sql_loader import SQLDatasetLoader
from data_inteligence.data_loader.loader import DatasetLoader
from agent_core.llm.oai import OpenAIChatModel

from server.setting import config as app_config
from server.app.models import Dataset, User
from server.app.repositories import UserRepository
from server.app.repositories.conversation import ConversationRepository
from server.app.repositories.workspace import WorkspaceRepository
from server.app.repositories.logs import LogsRepository
from server.app.schemas.requests.chat import ChatRequest
from server.app.schemas.responses.chat import ChatResponse
from server.app.schemas.responses.users import UserInfo
from server.app.utils.memory import prepare_conv_memory
from server.core.controller import BaseController
from server.core.database.transactional import Propagation, Transactional
from server.core.utils.json_encoder import jsonable_encoder
from server.core.utils.response_parser import JsonResponseParser


class ChatController(BaseController[User]):
    def __init__(
        self,
        user_repository: UserRepository,
        space_repository: WorkspaceRepository,
        conversation_repository: ConversationRepository,
        logs_repository: LogsRepository,
    ):
        super().__init__(model=User, repository=user_repository)
        self.user_repository = user_repository
        self.space_repository = space_repository
        self.conversation_repository = conversation_repository
        self.logs_repository = logs_repository
        self.llm = OpenAIChatModel(
            api_key=os.getenv("OPENAI_API_KEY"), 
            base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"), 
            model=os.getenv("LLM_DEFAULT_MODEL", "gpt-4o-mini"),
            system_message = f"Please make sure to respond in the language: {app_config.DEFAULT_LOCALE}"
        )

    async def get_clarification_questions(self, workspace_id: str) -> List[str]:
        datasets: List[Dataset] = await self.space_repository.get_space_datasets(
            workspace_id
        )
        logger.info(f"查询到{len(datasets)}条dataset")
        connectors = []
        for dataset in datasets:
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
            connectors.append(df)

        config = {"llm": self.llm}
        agent = DataFrameAgent(connectors, config=config)
        result = await agent.clarification_questions()
        return result

    @Transactional(propagation=Propagation.REQUIRED)
    async def start_new_conversation(self, user: UserInfo, chat_request: ChatRequest):
        return await self.conversation_repository.create(
            {
                "workspace_id": chat_request.workspace_id,
                "user_id": user.id,
            }
        )

    @Transactional(propagation=Propagation.REQUIRED)
    async def chat(self, user: UserInfo, chat_request: ChatRequest) -> ChatResponse:
        datasets: List[Dataset] = await self.space_repository.get_space_datasets(
            chat_request.workspace_id
        )
        conversation_id = chat_request.conversation_id
        conversation_messages = []
        memory = None

        if not chat_request.conversation_id:
            user_conversation = await self.start_new_conversation(user, chat_request)
            conversation_id = user_conversation.id
            logger.bind(name="fastapi_app").info(f"new conversation id created. conversation_id: {conversation_id}")
        else:
            conversation_messages = (
                await self.conversation_repository.get_conversation_messages(
                    conversation_id
                )
            )
            memory = prepare_conv_memory(conversation_messages)

        connectors = []
        for dataset in datasets:
            # load dataset：分两种情况。1、有description或field_descriptions，加载SemanticLayer数据集。2、没有，直接从文件或数据库中加载。
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
            connectors.append(df)

        config = {"llm": self.llm}
        agent = DataFrameAgent(connectors, config=config, response_parser=JsonResponseParser())
        
        if memory:
            agent._state.memory = memory

        start_time = time.time()
        if app_config.USE_CACHE:
            cache_message = await self.conversation_repository.get_cache_message(conversation_id, chat_request.query)
            cache_code = cache_message.code_generated if cache_message else None
            if cache_code:
                try:
                    response = agent.execute_code(cache_code)
                    logger.bind(name="fastapi_app").info(f"cache hit. response: {response}")
                except Exception:
                    response = await agent.follow_up(chat_request.query)
            else:
                response = await agent.follow_up(chat_request.query)
        else:
            response = await agent.follow_up(chat_request.query)

        if isinstance(response, str) and (
            response.startswith("抱歉，我无法回答")
        ):
            return [
                {
                    "type": "string",
                    "message": "抱歉，我无法回答你的问题。请提供更详细的信息。",
                    "value": "抱歉，我无法回答你的问题。请重试。",
                }
            ]
        execution_time = round(time.time() - start_time, 3)
        log = await self.logs_repository.add_log(user.id, [{}], chat_request.query, execution_time=execution_time)

        response = jsonable_encoder([response])
        conversation_message = await self.conversation_repository.add_conversation_message(
            conversation_id=conversation_id,
            query=chat_request.query,
            response=response,
            code_generated=agent.last_code_executed,
            log_id=log.id
        )

        return ChatResponse(
            response=response,
            conversation_id=str(conversation_id),
            message_id = str(conversation_message.id),
            query = str(conversation_message.query)
        )
