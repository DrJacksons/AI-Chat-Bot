import traceback
import copy
from abc import ABC, abstractmethod
from typing import Dict, List, Union, Iterator


class Agent(ABC):
    def __init__(self, 
        name: str,
        system_message: str,
        description: float,
        **kwargs):
        """
        Initialize the agent.

        Args:
            name (str): The name of the agent.
            system_message (str): The system message of the agent.
            description (float): The description of the agent.
        """
        self.name = name
        self.system_message = system_message
        self.description = description

    def __repr__(self):
        return f"{self.name}({self.description})"

    def run(self, messages: List[Union[Dict, Message]],
            **kwargs) -> Union[Iterator[List[Message]], Iterator[List[Dict]]]:
        """Return one response generator based on the received messages.

        This method performs a uniform type conversion for the inputted messages,
        and calls the _run method to generate a reply.

        Args:
            messages: A list of messages.

        Yields:
            The response generator.
        """
        messages = copy.deepcopy(messages)
        _return_message_type = 'dict'
        new_messages = []
        # Only return dict when all input messages are dict
        if not messages:
            _return_message_type = 'message'
        for msg in messages:
            if isinstance(msg, dict):
                new_messages.append(Message(**msg))
            else:
                new_messages.append(msg)
                _return_message_type = 'message'

        if 'lang' not in kwargs:
            if has_chinese_messages(new_messages):
                kwargs['lang'] = 'zh'
            else:
                kwargs['lang'] = 'en'

        if self.system_message:
            if not new_messages or new_messages[0][ROLE] != SYSTEM:
                # Add the system instruction to the agent
                new_messages.insert(0, Message(role=SYSTEM, content=self.system_message))
            else:
                # Already got system message in new_messages
                if isinstance(new_messages[0][CONTENT], str):
                    new_messages[0][CONTENT] = self.system_message + '\n\n' + new_messages[0][CONTENT]
                else:
                    assert isinstance(new_messages[0][CONTENT], list)
                    assert new_messages[0][CONTENT][0].text
                    new_messages[0][CONTENT] = [ContentItem(text=self.system_message + '\n\n')
                                               ] + new_messages[0][CONTENT]  # noqa

        for rsp in self._run(messages=new_messages, **kwargs):
            for i in range(len(rsp)):
                if not rsp[i].name and self.name:
                    rsp[i].name = self.name
            if _return_message_type == 'message':
                yield [Message(**x) if isinstance(x, dict) else x for x in rsp]
            else:
                yield [x.model_dump() if not isinstance(x, dict) else x for x in rsp]

    @abstractmethod
    def _run(self, messages: List[Message], lang: str = 'en', **kwargs) -> Iterator[List[Message]]:
        """Return one response generator based on the received messages.

        The workflow for an agent to generate a reply.
        Each agent subclass needs to implement this method.

        Args:
            messages: A list of messages.
            lang: Language, which will be used to select the language of the prompt
              during the agent's execution process.

        Yields:
            The response generator.
        """
        raise NotImplementedError


