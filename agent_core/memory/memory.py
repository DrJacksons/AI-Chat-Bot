from ast import Dict
from email import message
from turtle import update
from typing import Any, List, Optional
from copy import deepcopy
from .base import MemoryBase
from .storage import SQLiteManager
from .utils import (
    get_fact_retrieval_messages,
    parse_messages,
    remove_code_blocks
)
from agent_core.llm.oai import OpenAIChatModel
from agent_core.vectorstores import VectorStore



class Memory(MemoryBase):
    def __init__(self, db_path: str):
        self.db = SQLiteManager(db_path)
        self.vector_store = VectorStore()
        self.llm = OpenAIChatModel()

    def _should_use_agent_memory_extraction(self, messages: List[dict], metadata: dict) -> bool:
        """判断是否需要使用智能体记忆提取。"""
        return any(msg.get("role") == "assistant" for msg in messages)

    def _add_to_vector_store(self, messages: List[dict], metadata: dict, filters, infer):
        """Add messages to the vector store.

        Args:
            messages: Iterable of messages to add.
            metadata: Optional Iterable of metadata associated with the messages.
            filters: Optional filters to apply to the messages.
            infer: Optional function to infer vectors from the messages.
        """
        if not infer:
            returned_memories = []
            for message_dict in messages:
                if (
                    not isinstance(message_dict, dict)
                    or message_dict.get("role") is None
                    or message_dict.get("content") is None
                ):
                    print("跳过无效的消息:", message_dict)
                    continue

                if message_dict["role"] == "system":
                    continue

                per_msg_meta = deepcopy(metadata)
                per_msg_meta["role"] = message_dict["role"]

                actor_name = message_dict.get("name")
                if actor_name:
                    per_msg_meta["actor_id"] = actor_name

                msg_content = message_dict["content"]
                msg_embeddings = self.embedding_model.embed(msg_content, "add")
                mem_id = self._create_memory(msg_content, msg_embeddings, per_msg_meta)
                returned_memories.append(
                    {
                        "id": mem_id,
                        "content": msg_content,
                        "event": "ADD",
                        "actor_id": actor_name if actor_name else None,
                        "role": message_dict["role"]
                    }
                )
            return returned_memories

        parsed_messages = parse_messages(messages)

        if self.config.custom_fact_extraction_prompt:
            system_prompt = self.config.custom_fact_extraction_prompt
            user_prompt = f"Input:\n{parsed_messages}"
        else:
            # Determine if this should use agent memory extraction based on agent_id presence
            # and role types in messages
            is_agent_memory = self._should_use_agent_memory_extraction(messages, metadata)
            system_prompt, user_prompt = get_fact_retrieval_messages(parsed_messages, is_agent_memory)
        
        response = self.llm.chat(
            prompt_or_messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"}
        )

        try:
            response = remove_code_blocks(response)
            if not response.strip():
                new_retrieved_facts = []
            else:
                try:
                    new_retrieved_facts = json.loads(response)
                except json.JSONDecodeError:
                    print(f"Error in _add_to_vector_store: Failed to parse JSON response: {response}")
                    extracted_json = extract_json(response)
                    print("Extracted JSON:", extracted_json)
                    new_retrieved_facts = json.loads(extracted_json)["facts"]
        except Exception as e:
            print(f"Error in _add_to_vector_store: {e}")
            new_retrieved_facts = []
        
        if not new_retrieved_facts:
            print("No new facts retrieved from input. Skipping memory update LLM call.")
        
        retrieved_old_memory = []
        new_message_embeddings = []
        # 
        search_filters = {}
        if filters.get("user_id"):
            search_filters["user_id"] = filters["user_id"]
        if filters.get("agent_id"):
            search_filters["agent_id"] = filters["agent_id"]
        

    def _process_metadata_filters(self, metadata_filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理metadata_filters并将其转换为向量存储兼容的格式。
        Args:
            metadata_filters: Enhanced metadata filters with operators
        Returns:
            Dict of processed filters compatible with vector store
        """
        processed_filters = {}

        def process_condition(key: str, condition: Any) -> Dict[str, Any]:
            if not isinstance(condition, dict):
                if condition == "*":
                    # 通配符：匹配此字段的所有内容（具体实现取决于向量存储）
                    return {key: "*"}
                return {key: condition}
        
            result = {}
            for op, value in condition.items():
                operator_map = {
                    "eq": "eq", "ne": "ne", "gt": "gt", "gte": "gte",
                    "lt": "lt", "lte": "lte", "in": "in", "nin": "nin",
                    "contains": "contains", "icontains": "icontains"
                }

                if op in operator_map:
                    result[key] = {operator_map[op]: value}
                else:
                    raise ValueError(f"不支持的操作符(metadata filter): {op}")
                    
            return result
        
        for key, value in metadata_filters.items():
            if key == "AND":
                # 逻辑与：合并多个条件
                if not isinstance(value, list):
                    raise ValueError("AND条件必须是一个列表")
                for condition in value:
                    for sub_key, sub_value in condition.items():
                        processed_filters.update(process_condition(sub_key, sub_value))
            elif key == "OR":
                # 逻辑或：传递到向量存储以进行特定实现的处理
                if not isinstance(value, list):
                    raise ValueError("OR条件必须是一个列表")
                processed_filters["$or"] = []
                for condition in value:
                    or_condition = {}
                    for sub_key, sub_value in condition.items():
                        or_condition.update(process_condition(sub_key, sub_value))
                    processed_filters["$or"].append(or_condition)
            elif key == "NOT":
                # 逻辑非：传递到向量存储以进行特定实现的处理
                if not isinstance(value, list) or not value:
                    raise ValueError("NOT条件必须是一个非空列表")
                processed_filters["$not"] = []
                for condition in value:
                    not_condition = {}
                    for sub_key, sub_value in condition.items():
                        not_condition.update(process_condition(sub_key, sub_value))
                    processed_filters["$not"].append(not_condition)
            else:
                processed_filters.update(process_condition(key, value))
        
        return processed_filters

    def _has_advanced_operator(self, filters: Dict[str, Any]) -> bool:
        """检查filters是否包含高级操作符（如$or, $not）。"""
        if not isinstance(filters, dict):
            return False
        for key, value in filters.items():
            if key in ["AND", "OR", "NOT"]:
                return True
            if isinstance(value, dict):
                for op in value.keys():
                    if op in ["eq", "ne", "gt", "gte", "lt", "lte", "in", "nin", "contains", "icontains"]:
                        return True
            if value == "*":
                return True
        return False


