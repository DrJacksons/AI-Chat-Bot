import os
import shutil
from typing import List

import pandas as pd
from agent_core.agent.dataframe_agent import DataFrameAgent
from data_inteligence.helpers.path import find_project_root
from agent_core.llm.oai import OpenAIChatModel

from server.app.models import Dataset, User
from server.app.repositories import UserRepository
from server.app.repositories.conversation import ConversationRepository
from server.app.repositories.workspace import WorkspaceRepository
from server.app.repositories.logs import LogsRepository
from server.app.schemas.requests.chat import ChatRequest
from server.app.schemas.responses.chat import ChatResponse
from server.app.schemas.responses.users import UserInfo
from server.app.utils.memory import prepare_conv_memory
from server.core.constants import CHAT_FALLBACK_MESSAGE
from server.core.controller import BaseController
from server.core.database.transactional import Propagation, Transactional
from server.core.utils.dataframe import load_df
from server.core.utils.json_encoder import jsonable_encoder
from server.core.utils.response_parser import JsonResponseParser
from server.core.config import config as env_config


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

        else:
            conversation_messages = (
                await self.conversation_repository.get_conversation_messages(
                    conversation_id
                )
            )
            memory = prepare_conv_memory(conversation_messages)

        connectors = []
        for dataset in datasets:
            config = dataset.connector.config
            df = pd.read_csv(config["file_path"])
            connector = PandasConnector(
                {"original_df": df},
                name=dataset.name,
                description=dataset.description,
                custom_head=(load_df(dataset.head) if dataset.head else None),
                field_descriptions=dataset.field_descriptions,
            )
            connectors.append(connector)

        path_plot_directory = find_project_root() + "/exports/" + str(conversation_id)

        config = {
            "enable_cache": False,
            "response_parser": JsonResponseParser,
            "save_charts": True,
            "save_charts_path": path_plot_directory,
        }

        if env_config.OPENAI_API_KEY:
            llm = OpenAI(env_config.OPENAI_API_KEY)
            config["llm"] = llm

        agent = Agent(connectors, config=config)

        # add to log get log id
        
        if memory:
            agent.context.memory = memory

        response = agent.chat(chat_request.query)

        if os.path.exists(path_plot_directory):
            shutil.rmtree(path_plot_directory)

        if isinstance(response, str) and (
            response.startswith("Unfortunately, I was not able to")
        ):
            return [
                {
                    "type": "string",
                    "message": CHAT_FALLBACK_MESSAGE,
                    "value": CHAT_FALLBACK_MESSAGE,
                }
            ]

        summary = agent.pipeline.query_exec_tracker.get_summary()
        log = await self.logs_repository.add_log(user.id, "", summary, chat_request.query, summary['success'], summary['execution_time'])

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