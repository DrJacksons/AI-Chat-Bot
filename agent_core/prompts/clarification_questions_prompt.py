from .base import BasePrompt


class ClarificationQuestionsPrompt(BasePrompt):
    """Prompt to generate clarification questions."""

    template_path = "clarification_questions_prompt.tmpl"

    def to_json(self):
        context = self.props["context"]
        memory = context.memory
        # prepare datasets
        datasets = [dataset.to_json() for dataset in context.dfs]

        return {
            "prompt": self.to_string(),
            "datasets": datasets,
            "memory": memory.to_json(),
        }
