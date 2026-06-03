from typing import AsyncIterator, Optional
from dataclasses import dataclass


@dataclass
class LLMResponse:
    content: str
    model: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    tool_calls: Optional[list] = None  # Format Anthropic : [{id, name, input}]


@dataclass
class StreamChunk:
    content: str
    done: bool = False


class BaseLLMClient:
    """Interface commune pour tous les clients LLM."""

    async def complete(
        self,
        messages: list[dict],
        tools: Optional[list] = None,
        stream: bool = False,
    ) -> LLMResponse:
        raise NotImplementedError

    async def stream(
        self,
        messages: list[dict],
        tools: Optional[list] = None,
    ) -> AsyncIterator[StreamChunk]:
        raise NotImplementedError
