from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from .correct_execute_sql_query_usage_error_prompt import (
    CorrectExecuteSQLQueryUsageErrorPrompt,
)
from .correct_output_type_error_prompt import (
    CorrectOutputTypeErrorPrompt,
)

from .base import BasePrompt
from .generate_python_code_with_sql import GeneratePythonCodeWithSQLPrompt
from .rephrase_query import RephraseQueryPrompt
from .clarification_questions_prompt import ClarificationQuestionsPrompt
from .generate_dataset_summary import GenerateDatasetSummaryPrompt

if TYPE_CHECKING:
    from agent_core.agent.dataframe_state import AgentState


def get_chat_prompt_for_sql(context: AgentState) -> BasePrompt:
    return GeneratePythonCodeWithSQLPrompt(
        context=context,
        last_code_generated=context.last_code_generated,
        output_type=context.output_type,
    )


def get_correct_error_prompt_for_sql(
    context: AgentState, code: str, traceback_error: str
) -> BasePrompt:
    return CorrectExecuteSQLQueryUsageErrorPrompt(
        context=context, code=code, error=traceback_error
    )


def get_correct_output_type_error_prompt(
    context: AgentState, code: str, traceback_error: str
) -> BasePrompt:
    return CorrectOutputTypeErrorPrompt(
        context=context,
        code=code,
        error=traceback_error,
        output_type=context.output_type,
    )


def get_rephrase_query_prompt(
    context: AgentState, query: str, business_description: str = None
) -> BasePrompt:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return RephraseQueryPrompt(
        context=context,
        query=query,
        business_description=business_description,
        current_time=current_time,
    )


def get_clarification_questions_prompt(
    context: AgentState
) -> BasePrompt:
    return ClarificationQuestionsPrompt(
        context=context
    )


__all__ = [
    "BasePrompt",
    "CorrectErrorPrompt",
    "GeneratePythonCodePrompt",
    "GeneratePythonCodeWithSQLPrompt",
    "RephraseQueryPrompt",
    "ClarificationQuestionsPrompt",
    "GenerateDatasetSummaryPrompt",
]
