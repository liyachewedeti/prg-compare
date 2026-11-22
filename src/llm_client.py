"""Optional LLM adapter placeholder. The reproducible baseline uses no API calls."""
import os

class LLMClient:
    def __init__(self, budget_usd=7.0):
        self.budget_usd = float(budget_usd)
        self.api_key = os.getenv("OPENAI_API_KEY")

    @property
    def enabled(self):
        return bool(self.api_key)

    def extract(self, text):
        raise NotImplementedError(
            "LLM extraction is intentionally not enabled in the baseline. "
            "Use the deterministic extractor or implement a provider adapter with cost tracking."
        )
