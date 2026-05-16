from dataclasses import dataclass
from typing import Protocol

from app.infrastructure.rag.simple_retriever import RetrievalResult


class LlmGatewayUnavailable(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class LlmGeneration:
    answer: str
    safe_to_answer: bool
    prompt: str
    provider: str


class LlmGateway(Protocol):
    def generate(self, question: str, contexts: list[RetrievalResult]) -> LlmGeneration:
        """Generate an answer constrained to the retrieved contexts."""
