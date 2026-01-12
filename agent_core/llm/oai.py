from typing import List, Dict, Any, Optional, Union, Tuple, AsyncIterator
import openai
from .base import BaseChatModel


class OpenAIChatModel(BaseChatModel):
    temperature: float = 0
    max_tokens: int = 10000
    top_p: float = 1
    frequency_penalty: float = 0
    presence_penalty: float = 0.6
    n: int = 1
    stop: Optional[str] = None
    request_timeout: Union[float, Tuple[float, float], Any, None] = None
    max_retries: int = 2
    seed: Optional[int] = None

    """使用 OpenAI Python SDK v2.0+ 实现的 ChatModel 子类。"""
    def __init__(self, model: str, api_key: str, base_url: Optional[str] = None, **kwargs):
        """
        初始化 OpenAIChatModel 实例。

        Args:
            model (str): OpenAI 模型名称，例如 'gpt-3.5-turbo', 'gpt-4'。
            api_key (str): OpenAI API 密钥。
            base_url (Optional[str], optional): 自定义 API 基础 URL (例如使用代理或本地部署时)。默认为 None。
            **kwargs: 其他传递给父类或 OpenAI 客户端的参数。
        """
        super().__init__(model, api_key, base_url=base_url, **kwargs)
        
        # 创建 OpenAI 异步客户端
        # 注意：OpenAI SDK v2.x 推荐使用异步客户端以获得更好的性能
        client_kwargs = {"api_key": self.api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
            
        self.client = openai.AsyncOpenAI(**client_kwargs)
        print(f"Initialized OpenAIChatModel client for model: {self.model}")

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling OpenAI API."""
        params: Dict[str, Any] = {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "seed": self.seed,
            "stop": self.stop,
            "n": self.n,
        }

        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens

        return params

    async def _chat_stream(self, messages: List[Dict[str, str]]) -> AsyncIterator[str]:
        """
        使用 OpenAI SDK 实现流式聊天。
        """
        try:
            # 调用 OpenAI 的聊天补全 API，启用流式传输
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True, # 关键参数，启用流式
                **self._default_params   # 传递其他可能的参数，如 temperature, max_tokens 等
            )
            
            # 异步迭代流式响应
            async for chunk in stream:
                # 检查是否有内容并 yield 出来
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            # 错误处理非常重要
            print(f"Error during OpenAI stream chat: {e}")
            yield f"[Error]: {str(e)}"

    async def _chat_no_stream(self, messages: List[Dict[str, str]]) -> str:
        """
        使用 OpenAI SDK 实现非流式聊天。
        """
        try:
            # 调用 OpenAI 的聊天补全 API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False, # 明确禁用流式
                **self._default_params     # 传递其他可能的参数
            )
            # 提取并返回完整回复
            content = response.choices[0].message.content
            return content if content is not None else ""
            
        except Exception as e:
            print(f"Error during OpenAI non-stream chat: {e}")
            return f"[Error]: {str(e)}"

    async def _chat_with_functions(
        self,
        messages: List[Dict[str, str]],
        functions: List[Dict[str, Any]],
        function_call: Union[str, Dict[str, str], None] = None
    ) -> Dict[str, Any]:
        """
        使用 OpenAI SDK 实现带 Function Calling 的聊天。
        注意：OpenAI 新版本推荐使用 Tools API 替代旧的 Functions API。
        此处为了兼容性仍保留 functions/function_call 的命名，但内部可能映射到 tools。
        """
        try:
             # 构建请求参数
            create_kwargs = {
                "model": self.model,
                "messages": messages,
                "tools": functions, # OpenAI 新版使用 tools 和 tool_choice
                "tool_choice": function_call if function_call is not None else "auto",
                "stream": False,
                **self._default_params
            }
            
            # 如果没有显式提供 tool_choice，则移除它以便让 API 默认为 "auto"
            if function_call is None:
                 create_kwargs.pop('tool_choice')

            # 调用 OpenAI 的聊天补全 API
            response = await self.client.chat.completions.create(**create_kwargs)
            
            choice = response.choices[0]
            message = choice.message

            result = {"content": "", "function_call": None, "tool_calls": None}

            # 检查是否有文本回复
            if message.content:
                result["content"] = message.content

            # 检查是否有工具调用 (新版 Function Calling / Tools)
            if message.tool_calls:
                result["tool_calls"] = [tc.model_dump() for tc in message.tool_calls]

            return result

        except Exception as e:
            print(f"Error during OpenAI function call chat: {e}")
            return {"content": f"[Error]: {str(e)}", "function_call": None, "tool_calls": None}

    @property
    def type(self) -> str:
        return "openai"
