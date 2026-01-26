from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Union, Callable, AsyncIterator

from agent_core.prompts.base import BasePrompt


class BaseChatModel(ABC):
    def __init__(self, model: str, api_key: str, system_message: Optional[str] = None, **kwargs):
        self.model = model
        self.api_key = api_key
        self.config = kwargs
        self.system_message = system_message

    async def chat(
        self,
        prompt_or_messages: Union[str, List[Dict[str, str]]],
        stream: bool = False,
        functions: Optional[List[Dict[str, Any]]] = None,
        function_call: Union[str, Dict[str, str], None] = None,
        **kwargs
    ):
        """
        主要的对外接口，用于与模型进行交互。

        Args:
            prompt_or_messages (Union[str, List[Dict[str, str]]]):
                用户输入。可以是简单的字符串（会被转换为 user 消息），
                或者是一个完整的对话消息列表。
            stream (bool, optional): 是否启用流式输出。默认为 False。
            functions (Optional[List[Dict[str, Any]]], optional):
                可供模型调用的函数列表。如果提供，则启用 Function Calling 功能。
            function_call (Union[str, Dict[str, str], None], optional):
                控制函数调用的行为。默认为 None。
            **kwargs: 其他传递给模型 API 的参数。

        Returns:
            根据 stream 和 functions 参数的不同组合，返回不同类型的结果：
            - 如果 stream=True 且 functions=None: 返回 AsyncIterator[str]
            - 如果 stream=False 且 functions=None: 返回 str
            - 如果 functions is not None: 返回 Dict[str, Any] (忽略 stream 参数)
        """
        if isinstance(prompt_or_messages, str):
            messages = [{"role": "user", "content": prompt_or_messages}]
        elif isinstance(prompt_or_messages, list):
            messages = prompt_or_messages
        else:
            raise ValueError("prompt_or_messages must be either a string or a list of message dictionaries.")

        if self.system_message:
            if not messages or messages[0].get("role") != "system":
                messages.insert(0, {"role": "system", "content": self.system_message})
                
        if functions is not None:
            return await self._chat_with_functions(
                messages=messages,
                functions=functions,
                function_call=function_call
            )
        else:
            if stream:
                return self._chat_stream(
                    messages=messages
                )
            else:
                return await self._chat_no_stream(
                    messages=messages
                )

    @abstractmethod
    async def _chat_stream(
        self,
        messages: List[Dict[str, str]]
    ) -> AsyncIterator[str]:
        """
        异步流式聊天方法。

        Args:
            messages (List[Dict[str, str]]): 包含消息的列表，每个消息都是一个字典，包含 "role" 和 "content" 键。

        Returns:
            AsyncIterator[str]: 异步迭代器，每次返回模型生成的新token。
        """
        raise NotImplementedError

    @abstractmethod
    async def _chat_no_stream(
        self,
        messages: List[Dict[str, str]]
    ) -> str:
        """
        非流式聊天方法。

        Args:
            messages (List[Dict[str, str]]): 包含消息的列表，每个消息都是一个字典，包含 "role" 和 "content" 键。

        Returns:
            str: 模型生成的完整回答。
        """
        raise NotImplementedError


    @abstractmethod
    async def _chat_with_functions(
        self,
        messages: List[Dict[str, str]],
        functions: List[Dict[str, Any]],
        function_call: Union[str, Dict[str, str], None]
    ) -> Dict[str, Any]:
        """
        带函数调用的聊天方法。

        Args:
            messages (List[Dict[str, str]]): 包含消息的列表，每个消息都是一个字典，包含 "role" 和 "content" 键。
            functions (List[Dict[str, Any]]): 包含函数定义的列表，每个函数都是一个字典，包含 "name" 和 "arguments" 键。
            function_call (Union[str, Dict[str, str], None]): 控制函数调用行为。
                                                              "auto" 表示模型可以决定；
                                                              {"name": "my_function"} 表示强制调用特定函数；
                                                              None 表示不调用函数。

        Returns:
            Dict[str, Any]: 包含模型回复和潜在函数调用信息的字典。
                           通常包含 'content' (文本回复) 和 'function_call' (如果被调用)。
        """
        raise NotImplementedError

    @property
    def type(self) -> str:
        """
        Return type of LLM.

        Raises:
            ValueError: Type has not been implemented

        Returns:
            str: Type of LLM a string

        """
        raise ValueError("Type has not been implemented")

    async def call(
        self,
        prompt: BasePrompt | str,
        memory: List[Dict[str, str]] = None,
        stream: bool = False,
    ):
        """
        整合提示词和memory历史对话，给到大模型LLM，生成回复
        
        Args:
            prompt (str): 用户输入的提示词
            memory (List[Dict[str, str]]): 包含历史对话的列表，每个对话都是一个字典，包含 "role" 和 "content" 键。
        
        Returns:
            str: 模型生成的回复
        """
        messages = memory.to_openai_messages() if memory else []
        if isinstance(prompt, str):
            messages.append({"role": "user", "content": prompt})
        else:
            messages.append({"role": "user", "content": prompt.to_string()})
        return await self.chat(
            prompt_or_messages=messages,
            stream=stream,
        )
        
