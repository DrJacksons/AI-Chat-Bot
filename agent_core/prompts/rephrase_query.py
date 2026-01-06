from .base import BasePrompt


class RephraseQueryPrompt(BasePrompt):
    """Prompt to rephrase a query."""

    template_path = "rephrase_query.tmpl"

    def to_json(self):
        query = self.props["query"]

        return {
            "prompt": self.to_string(),
            "config": {
                "query": query,
            },
        }
