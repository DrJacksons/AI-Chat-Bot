import pandas as pd

from typing import List, Optional, Union
from agent_core.agent.base import Agent
from agent_core.agent.dataframe_state import AgentState
from data_inteligence.dataframe import DataFrame, VirtualDataFrame
from data_inteligence.code_core.code_generation import CodeGenerator


class DataFrameAgent(Agent):
    """这是一个基于Dataframe的Agent，用于处理Dataframe（数据分析）相关的任务。"""
    def __init__(self, 
        dfs:  Union[
            Union[DataFrame, VirtualDataFrame], List[Union[DataFrame, VirtualDataFrame]]
        ],
        memory_size: Optional[int] = 10,
        **kwargs):
        super().__init__(name="DataframeAgent", 
        system_message="你是一个基于Dataframe的Agent，用于处理Dataframe（数据分析）相关的任务。", 
        description="这是一个基于Dataframe的Agent，用于处理Dataframe（数据分析）相关的任务。", **kwargs)
        self.description = description
        if isinstance(dfs, list):
            self.dfs = [DataFrame(df) if self.is_pd_dataframe(df) else df for df in dfs]
        elif self.is_pd_dataframe(dfs):
            self.dfs = [dfs]

        self._state = AgentState()
        self._state.initialize(dfs, memory_size=memory_size, description=description)
        self._code_generator = CodeGenerator()
        self._response_parser = ResponseParser()
        self._sandbox = sandbox

    def is_pd_dataframe(self, df: Union[DataFrame, VirtualDataFrame]) -> bool:
        """判断是否为pandas的DataFrame"""
        return isinstance(df, DataFrame) and isinstance(df, pd.DataFrame)

    def chat(self, query: str, output_type: Optional[str] = "string"):
        """
        处理用户查询，返回分析结果。

        :param query: 用户查询字符串
        :param output_type: 输出类型，可选值为"string"（字符串）或"json"（JSON格式）
        :return: 分析结果，根据output_type不同而不同
        """
        self.start_new_conversation()
        return self._process_query(query, output_type)

    def follow_up(self, query: str, output_type: Optional[str] = "string"):
        """
        继续处理用户查询，返回分析结果。

        :param query: 用户查询字符串
        :param output_type: 输出类型，可选值为"string"（字符串）
        :return: 分析结果，根据output_type不同而不同
        """
        return self._process_query(query, output_type)

    def start_new_conversation(self):
        """
        开始新的对话，清空历史记录。
        """
        self._state
