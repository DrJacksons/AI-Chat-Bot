from abc import ABC, abstractmethod
from typing import Dict, List, Union


class BaseTool(ABC):
    name: str = ''
    description: str = ''
    parameters: Union[List[Dict], Dict] = []

    def __init__(self, name: str, description: str):
        self.cfg = cfg or {}
        if not self.name:
            raise ValueError(
                f'You must set {self.__class__.__name__}.name, either by @register_tool(name=...) or explicitly setting {self.__class__.__name__}.name'
            )
        if isinstance(self.parameters, dict):
            if not is_tool_schema({'name': self.name, 'description': self.description, 'parameters': self.parameters}):
                raise ValueError(
                    'The parameters, 当作为一个dict提供时, 必须为一个有效的 openai-compatible JSON 格式.')

    @abstractmethod
    def call(self, params: Union[str, dict], **kwargs) -> Union[str, list, dict, List[ContentItem]]:
        """The interface for calling tools.

        每个工具都需要继承这个函数，这就是工具的工作流。

        Args:
            params: The parameters of func_call.
            kwargs: Additional parameters for calling tools.

        Returns:
            The result returned by the tool, implemented in the subclass.
        """
        raise NotImplementedError

    @property
    def function(self) -> dict:  # Bad naming. It should be `function_info`.
        return {
            # 'name_for_human': self.name_for_human,
            'name': self.name,
            'description': self.description,
            'parameters': self.parameters,
            # 'args_format': self.args_format
        }

    @property
    def name_for_human(self) -> str:
        return self.cfg.get('name_for_human', self.name)

    @property
    def args_format(self) -> str:
        fmt = self.cfg.get('args_format')
        if fmt is None:
            if has_chinese_chars([self.name_for_human, self.name, self.description, self.parameters]):
                fmt = '此工具的输入应为JSON对象。'
            else:
                fmt = 'Format the arguments as a JSON object.'
        return fmt

    @property
    def file_access(self) -> bool:
        return False