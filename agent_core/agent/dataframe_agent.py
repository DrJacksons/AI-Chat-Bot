from typing import List, Optional, Union
from agent_core.agent.base import Agent
from data_inteligence.dataframe import DataFrame, VirtualDataFrame


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

