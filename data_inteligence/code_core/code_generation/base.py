import traceback
import re
import ast
from agent_core.agent.dataframe_state import AgentState
from agent_core.prompts.base import BasePrompt

from .code_cleaning import CodeCleaner
from .code_validation import CodeRequirementValidator
from data_inteligence.exceptions import NoCodeFoundError


class CodeGenerator:
    def __init__(self, context: AgentState):
        self._context = context
        self._code_cleaner = CodeCleaner(self._context)
        self._code_validator = CodeRequirementValidator(self._context)

    def _polish_code(self, code: str) -> str:
        """
        Polish the code by removing the leading "python" or "py",  \
        removing surrounding '`' characters  and removing trailing spaces and new lines.

        Args:
            code (str): A string of Python code.

        Returns:
            str: Polished code.

        """
        if re.match(r"^(python|py)", code):
            code = re.sub(r"^(python|py)", "", code)
        if re.match(r"^`.*`$", code):
            code = re.sub(r"^`(.*)`$", r"\1", code)
        code = code.strip()
        return code

    def _is_python_code(self, string):
        """
        Return True if it is valid python code.
        Args:
            string (str):

        Returns (bool): True if Python Code otherwise False

        """
        try:
            ast.parse(string)
            return True
        except SyntaxError:
            return False

    def _extract_code(self, response: str, separator: str = "```") -> str:
        """
        Extract the code from the response.

        Args:
            response (str): Response
            separator (str, optional): Separator. Defaults to "```".

        Raises:
            NoCodeFoundError: No code found in the response

        Returns:
            str: Extracted code from the response
        """
        code = response

        # If separator is in the response then we want the code in between only
        if separator in response and len(code.split(separator)) > 1:
            code = code.split(separator)[1]
        code = self._polish_code(code)

        # Even if the separator is not in the response, the output might still be valid python code
        if not self._is_python_code(code):
            raise NoCodeFoundError("No code found in the response")

        return code

    async def generate_code(self, prompt: BasePrompt) -> str:
        """
        Generates code using a given LLM and performs validation and cleaning steps.

        Args:
            prompt (BasePrompt): The prompt to guide code generation.

        Returns:
            str: The final cleaned and validated code.

        Raises:
            Exception: If any step fails during the process.
        """
        try:
            self._context.logger.info(f"Using Prompt: {prompt}")

            # Generate the code
            # , memory
            code = await self._context.config.llm.call(prompt) 
            code = self._extract_code(code)
            self._context.last_code_generated = code
            self._context.logger.info(f"Code Generated:\n{code}")
            
            # Validate and clean the code
            cleaned_code = self.validate_and_clean_code(code)
            # Update with the final cleaned code (for subsequent processing and multi-turn conversations)
            self._context.last_code_generated = cleaned_code

            return cleaned_code

        except Exception as e:
            error_message = f"An error occurred during code generation: {e}"
            stack_trace = traceback.format_exc()

            self._context.logger.error(error_message)
            self._context.logger.info(f"Stack Trace:\n{stack_trace}")

            raise e

    def validate_and_clean_code(self, code: str) -> str:
        # Validate code requirements
        self._context.logger.info("Validating code requirements...")
        if not self._code_validator.validate(code):
            raise ValueError("Code validation failed due to unmet requirements.")
        self._context.logger.info("Code validation successful.")

        # Clean the code
        self._context.logger.info("Cleaning the generated code...")
        return self._code_cleaner.clean_code(code)
