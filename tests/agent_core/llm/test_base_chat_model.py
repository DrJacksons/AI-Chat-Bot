import importlib.util
import sys
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List

import pytest


ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
BASE_MODULE_PATH = ROOT_DIR / "agent_core" / "llm" / "base.py"
SPEC = importlib.util.spec_from_file_location("agent_core.llm.base", BASE_MODULE_PATH)
BASE_MODULE = importlib.util.module_from_spec(SPEC)
sys.modules["agent_core.llm.base"] = BASE_MODULE
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(BASE_MODULE)
BaseChatModel = BASE_MODULE.BaseChatModel


class DummyChatModel(BaseChatModel):
    def __init__(self, system_message: str | None = None):
        super().__init__(model="dummy-model", api_key="dummy-key", system_message=system_message)
        self.last_stream_messages: List[Dict[str, str]] | None = None
        self.last_no_stream_messages: List[Dict[str, str]] | None = None
        self.last_with_functions: Dict[str, Any] | None = None

    async def _chat_stream(self, messages: List[Dict[str, str]]) -> AsyncIterator[str]:
        self.last_stream_messages = messages
        for chunk in ["hello", " ", "stream"]:
            yield chunk

    async def _chat_no_stream(self, messages: List[Dict[str, str]]) -> str:
        self.last_no_stream_messages = messages
        return "no-stream-response"

    async def _chat_with_functions(
        self,
        messages: List[Dict[str, str]],
        functions: List[Dict[str, Any]],
        function_call: str | Dict[str, str] | None,
    ) -> Dict[str, Any]:
        self.last_with_functions = {
            "messages": messages,
            "functions": functions,
            "function_call": function_call,
        }
        return {"content": "with-functions"}


class TestBaseChatModel:
    @pytest.mark.asyncio
    async def test_chat_no_stream_returns_string_and_includes_system_message(self):
        model = DummyChatModel(system_message="system-message")

        result = await model.chat("user message", stream=False)

        assert result == "no-stream-response"
        assert model.last_no_stream_messages is not None
        assert model.last_no_stream_messages[0] == {
            "role": "system",
            "content": "system-message",
        }
        assert model.last_no_stream_messages[1] == {
            "role": "user",
            "content": "user message",
        }

    @pytest.mark.asyncio
    async def test_chat_stream_returns_async_iterator_and_includes_system_message(self):
        model = DummyChatModel(system_message="system-message")

        iterator = await model.chat("user message", stream=True)

        chunks: List[str] = []
        async for chunk in iterator:
            chunks.append(chunk)

        assert "".join(chunks) == "hello stream"
        assert model.last_stream_messages is not None
        assert model.last_stream_messages[0] == {
            "role": "system",
            "content": "system-message",
        }
        assert model.last_stream_messages[1] == {
            "role": "user",
            "content": "user message",
        }
