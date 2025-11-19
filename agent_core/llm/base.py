from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Union, Callable, AsyncIterator


class BaseChatModel(ABC):
    """LLM 聊天模型的基类"""

    def __init__(self, model: str, api_key: str, **kwargs):
        """
        初始化 ChatModel 实例。

        Args:
            model (str): 模型名称。
            api_key (str): 访问模型 API 所需的密钥。
            **kwargs: 其他可能需要的配置参数，例如 base_url, organization 等。
                      这些参数会被存储在 self.config 中供子类使用。
        """
        self.model = model
        self.api_key = api_key
        # 将其他配置参数存储起来，供子类实现时使用
        self.config = kwargs 
        print(f"Initialized ChatModel with model: {self.model}")

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
        # 处理输入，统一转换为 messages 列表格式
        if isinstance(prompt_or_messages, str):
            messages = [{"role": "user", "content": prompt_or_messages}]
        elif isinstance(prompt_or_messages, list):
            messages = prompt_or_messages
        else:
            raise ValueError("prompt_or_messages must be either a string or a list of message dictionaries.")

        print(f"Calling chat with messages: {messages}, stream: {stream}, has_functions: {functions is not None}")

        # 处理函数调用参数
        if functions is not None:
            # 启用函数调用功能
            return await self._chat_with_functions(
                messages=messages,
                functions=functions,
                function_call=function_call,
                generate_cfg=kwargs,
            )
        else:
            # 普通聊天功能
            if stream:
                return self._chat_stream(
                    messages=messages,
                    generate_cfg=kwargs,
                )
            else:
                return await self._chat_no_stream(
                    messages=messages,
                    generate_cfg=kwargs,
                )

    @abstractmethod
    async def _chat_stream(
        self,
        messages: List[Dict[str, str]],
        generate_cfg: dict,
    ) -> AsyncIterator[str]:
        """
        异步流式聊天方法。

        Args:
            messages (List[Dict[str, str]]): 包含消息的列表，每个消息都是一个字典，包含 "role" 和 "content" 键。
            generate_cfg (dict): 生成配置参数，例如温度、top_p 等。

        Returns:
            AsyncIterator[str]: 异步迭代器，每次返回模型生成的新token。
        """
        raise NotImplementedError

    @abstractmethod
    async def _chat_no_stream(
        self,
        messages: List[Dict[str, str]],
        generate_cfg: dict,
    ) -> str:
        """
        非流式聊天方法。

        Args:
            messages (List[Dict[str, str]]): 包含消息的列表，每个消息都是一个字典，包含 "role" 和 "content" 键。
            generate_cfg (dict): 生成配置参数，例如温度、top_p 等。

        Returns:
            str: 模型生成的完整回答。
        """
        raise NotImplementedError


    @abstractmethod
    async def _chat_with_functions(
        self,
        messages: List[Dict[str, str]],
        functions: List[Dict[str, Any]],
        function_call: Union[str, Dict[str, str], None],
        generate_cfg: dict,
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
            generate_cfg (dict): 生成配置参数，例如温度、top_p 等。

        Returns:
            Dict[str, Any]: 包含模型回复和潜在函数调用信息的字典。
                           通常包含 'content' (文本回复) 和 'function_call' (如果被调用)。
        """
        raise NotImplementedError
