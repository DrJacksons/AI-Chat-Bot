import os
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict
from agent_core.llm.base import BaseChatModel


model_name = "gpt-3.5-turbo"
embedding_model_name = "text-embedding-ada-002"

# memory config
memory_db_path = "memory.db"
memory_collection_name = "memory"


class Config(BaseModel):
    save_logs: bool = True
    enable_cache: bool = False
    max_retries: int = 3
    llm: Optional[BaseChatModel] = None
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "Config":
        return cls(**config)

