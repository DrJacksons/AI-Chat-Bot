from .base import BasePrompt


class GenerateDatasetSummaryPrompt(BasePrompt):
    """Prompt to generate dataset summary."""

    template_path = "dataset_summary.tmpl"

    def to_json(self):
        return {
            "prompt": self.to_string(),
        }
