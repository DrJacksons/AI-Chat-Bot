from .base import BasePrompt


class ClarificationQuestionsPrompt(BasePrompt):
    """Prompt to generate clarification questions."""

    template_path = "clarification_questions_prompt.tmpl"

    def to_json(self):
        context = self.props["context"]
        code = self.props["code"]
        error = self.props["error"]
        output_type = self.props["output_type"]
        memory = context.memory
        conversations = memory.to_json()

        system_prompt = memory.agent_description

        # prepare datasets
        datasets = [dataset.to_json() for dataset in context.dfs]

        return {
            "datasets": datasets,
            "conversation": conversations,
            "system_prompt": system_prompt,
            "error": {
                "code": code,
                "error_trace": str(error),
                "exception_type": "InvalidLLMOutputType",
            },
            "config": {
                "output_type": output_type,
            },
        }
