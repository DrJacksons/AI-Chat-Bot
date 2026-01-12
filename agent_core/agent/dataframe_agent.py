import pandas as pd
import traceback

from typing import List, Optional, Union, Any
from agent_core.agent.dataframe_state import AgentState
from agent_core.llm.schema import Message
from agent_core.config import Config
from agent_core.sandbox import Sandbox
from agent_core.prompts import (
    get_chat_prompt_for_sql,
    get_rephrase_query_prompt,
    get_correct_output_type_error_prompt,
    get_correct_error_prompt_for_sql,
)
from data_inteligence.dataframe import DataFrame, VirtualDataFrame
from data_inteligence.code_core.code_generation import CodeGenerator
from data_inteligence.code_core.code_execution import CodeExecutor
from data_inteligence.data_loader.duck_db_connection_manager import DuckDBConnectionManager
from data_inteligence.query_builders.sql_parser import SQLParser
from data_inteligence.code_core.response import ResponseParser, ErrorResponse
from data_inteligence.exceptions import (
    CodeExecutionError,
    InvalidLLMOutputType,
)


class DataFrameAgent:
    """这是一个基于Dataframe的Agent，用于处理Dataframe（数据分析）相关的任务。"""
    def __init__(self, 
        dfs:  Union[
            Union[DataFrame, VirtualDataFrame], List[Union[DataFrame, VirtualDataFrame]]
        ],
        config: Optional[Union[Config, dict]] = None,
        memory_size: Optional[int] = 10,
        response_parser: Optional[ResponseParser | Any] = None,
        sandbox: Optional[Sandbox] = None,
        **kwargs
    ):
        if isinstance(dfs, list):
            self.dfs = [DataFrame(df) if self.is_pd_dataframe(df) else df for df in dfs]
        elif self.is_pd_dataframe(dfs):
            self.dfs = [dfs]

        self._state = AgentState()
        self._state.initialize(dfs, config=config, memory_size=memory_size, description="基于Pandas的数据分析Agent")
        self._code_generator = CodeGenerator(self._state)
        self._response_parser = response_parser or ResponseParser()
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
        if self._state.config.enable_cache:
            self._state.logger.info("Cache enabled.")
        return self._process_query(query, output_type)

    async def follow_up(self, query: str, output_type: Optional[str] = "string"):
        """
        继续处理用户查询，返回分析结果。

        :param query: 用户查询字符串
        :param output_type: 输出类型，可选值为"string"（字符串）
        :return: 分析结果，根据output_type不同而不同
        """
        return await self._process_query(query, output_type)

    def rephrase_query(self, query: str, business_description: Optional[str] = None) -> str:
        """Rephrase the query to make it more understandable for the LLM."""
        prompt = get_rephrase_query_prompt(self._state, query, business_description)
        rephrased_query = self._state.config.llm.chat(prompt)
        return rephrased_query

    async def generate_code(self, query: Union[Message, str]) -> str:
        """Generate code using the LLM."""
        self._state.memory.add(str(query), is_user=True)

        self._state.logger.info("Generating new code...")
        prompt = get_chat_prompt_for_sql(self._state)

        code = await self._code_generator.generate_code(prompt)
        self._state.last_prompt_used = prompt
        return code

    def execute_code(self, code: str) -> dict:
        """Execute the generated code."""
        self._state.logger.info(f"Executing code: {code}")

        code_executor = CodeExecutor(self._state.config)
        code_executor.add_to_env("execute_sql_query", self._execute_sql_query)
        for skill in self._state.skills:
            code_executor.add_to_env(skill.name, skill.func)

        if self._sandbox:
            return self._sandbox.execute(code, code_executor.environment)

        return code_executor.execute_and_return_result(code)

    def _execute_sql_query(self, query: str) -> pd.DataFrame:
        """
        Executes an SQL query on registered DataFrames.

        Args:
            query (str): The SQL query to execute.

        Returns:
            pd.DataFrame: The result of the SQL query as a pandas DataFrame.
        """
        if not self._state.dfs:
            raise ValueError("No DataFrames available to register for query execution.")

        db_manager = DuckDBConnectionManager()

        table_mapping = {}
        df_executor = None

        for df in self._state.dfs:
            if hasattr(df, "query_builder"):
                # df is a valid dataset with query builder, loader and execute_sql_query method
                table_mapping[df.schema.name] = df.query_builder._get_table_expression()
                df_executor = df.execute_sql_query
            else:
                # dataset created from loading a csv, no query builder available
                db_manager.register(df.schema.name, df)

        final_query = SQLParser.replace_table_and_column_names(query, table_mapping)

        if not df_executor:
            return db_manager.sql(final_query).df()
        else:
            return df_executor(final_query)

    async def generate_code_with_retries(self, query: str) -> Any:
        """Execute the code with retry logic."""
        max_retries = self._state.config.max_retries
        attempts = 0
        try:
            return await self.generate_code(query)
        except Exception as e:
            exception = e
            while attempts <= max_retries:
                try:
                    return await self._regenerate_code_after_error(
                        self._state.last_code_generated, exception
                    )
                except Exception as e:
                    exception = e
                    attempts += 1
                    if attempts > max_retries:
                        self._state.logger.error(
                            f"Maximum retry attempts exceeded. Last error: {e}"
                        )
                        raise
                    self._state.logger.warning(
                        f"Retrying Code Generation ({attempts}/{max_retries})..."
                    )
            return None

    async def execute_with_retries(self, code: str) -> Any:
        """Execute the code with retry logic."""
        max_retries = self._state.config.max_retries
        attempts = 0

        while attempts <= max_retries:
            try:
                result = self.execute_code(code)
                return self._response_parser.parse(result)
            except Exception as e:
                attempts += 1
                if attempts > max_retries:
                    self._state.logger.error(f"Max retries reached. Error: {e}")
                    raise
                self._state.logger.warning(
                    f"Retrying execution ({attempts}/{max_retries})..."
                )
                code = await self._regenerate_code_after_error(code, e)

        return None

    def clear_memory(self):
        """
        清空对话历史记录
        """
        self._state.memory.clear()

    def start_new_conversation(self):
        """
        开始新的对话，清空历史记录。
        """
        self.clear_memory()

    async def _process_query(self, query: str, output_type: Optional[str] = "string"):
        """
        处理用户查询，返回分析结果。

        :param query: 用户查询字符串
        :param output_type: 输出类型，可选值为"string"（字符串）或"json"（JSON格式）
        :return: 分析结果，根据output_type不同而不同
        """
        self._state.logger.info(f"Question: {query}")
        self._state.logger.info(f"Running with {self._state.config.llm.type} LLM...")
        self._state.output_type = output_type
        try:
            self._state.assign_prompt_id()
            # 生成代码
            code = await self.generate_code_with_retries(query)
            # 执行代码
            result = await self.execute_with_retries(code)
            self._state.logger.info("Response generated successfully.")
            # 生成并返回最终结果
            return result
        except CodeExecutionError:
            return self._handle_exception(code)

    async def _regenerate_code_after_error(self, code: str, error: Exception) -> str:
        """Generate a new code snippet based on the error."""
        error_trace = traceback.format_exc()
        self._state.logger.info(f"Execution failed with error: {error_trace}")

        if isinstance(error, InvalidLLMOutputType):
            prompt = get_correct_output_type_error_prompt(
                self._state, code, error_trace
            )
        else:
            prompt = get_correct_error_prompt_for_sql(self._state, code, error_trace)

        return await self._code_generator.generate_code(prompt)

    def _handle_exception(self, code: str) -> ErrorResponse:
        """Handle exceptions and return an error message."""
        error_message = traceback.format_exc()
        self._state.logger.info(f"Processing failed with error: {error_message}")

        return ErrorResponse(last_code_executed=code, error=error_message)

    @property
    def last_generated_code(self):
        return self._state.last_code_generated

    @property
    def last_code_executed(self):
        return self._state.last_code_generated

    @property
    def last_prompt_used(self):
        return self._state.last_prompt_used
