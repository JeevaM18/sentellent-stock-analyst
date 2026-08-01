from dataclasses import dataclass


@dataclass(slots=True)
class LLMResponse:
    """Dataclass representing raw LLM generation response and execution metrics."""
    answer: str
    model: str
    provider: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    finish_reason: str | None = None
    latency_ms: float = 0.0
