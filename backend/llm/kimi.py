from openai import AsyncOpenAI
from typing import AsyncIterator, Optional
from . import BaseLLMClient, LLMResponse, StreamChunk
from ..config import settings

MODEL = "moonshotai/kimi-k2"  # Kimi K2 via OpenRouter
BASE_URL = "https://openrouter.ai/api/v1"

# Coûts réels vérifiés juin 2026 — Kimi K2 via OpenRouter
COST_INPUT_PER_TOKEN = 0.57 / 1_000_000
COST_OUTPUT_PER_TOKEN = 2.30 / 1_000_000


class KimiClient(BaseLLMClient):

    def __init__(self):
        self._client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url=BASE_URL,
        )

    async def complete(
        self,
        messages: list[dict],
        tools: Optional[list] = None,
        stream: bool = False,
    ) -> LLMResponse:
        kwargs = dict(model=MODEL, messages=messages, max_tokens=8096)

        response = await self._client.chat.completions.create(**kwargs)

        content = response.choices[0].message.content or ""
        tokens_in = response.usage.prompt_tokens
        tokens_out = response.usage.completion_tokens
        cost = tokens_in * COST_INPUT_PER_TOKEN + tokens_out * COST_OUTPUT_PER_TOKEN

        return LLMResponse(
            content=content,
            model=MODEL,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_usd=cost,
        )

    async def stream(
        self,
        messages: list[dict],
        tools: Optional[list] = None,
    ) -> AsyncIterator[StreamChunk]:
        response = await self._client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=8096,
            stream=True,
        )

        async for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                yield StreamChunk(content=delta)

        yield StreamChunk(content="", done=True)
