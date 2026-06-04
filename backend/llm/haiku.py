import anthropic
from typing import AsyncIterator, Optional
from . import BaseLLMClient, LLMResponse, StreamChunk
from ..config import settings

MODEL = "claude-haiku-4-5-20251001"

COST_INPUT_PER_TOKEN = 0.80 / 1_000_000
COST_OUTPUT_PER_TOKEN = 4.00 / 1_000_000


class HaikuClient(BaseLLMClient):

    def __init__(self):
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    @staticmethod
    def _split_system(messages: list[dict]) -> tuple[Optional[str], list[dict]]:
        if messages and messages[0].get("role") == "system":
            return messages[0]["content"], messages[1:]
        return None, messages

    async def complete(self, messages: list[dict], tools=None, stream=False) -> LLMResponse:
        system, msgs = self._split_system(messages)
        kwargs = dict(model=MODEL, max_tokens=2048, messages=msgs)
        if system:
            kwargs["system"] = system

        response = await self._client.messages.create(**kwargs)
        content = response.content[0].text if response.content else ""
        tokens_in = response.usage.input_tokens
        tokens_out = response.usage.output_tokens

        return LLMResponse(
            content=content,
            model=MODEL,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_usd=tokens_in * COST_INPUT_PER_TOKEN + tokens_out * COST_OUTPUT_PER_TOKEN,
        )

    async def stream(self, messages: list[dict], tools=None) -> AsyncIterator[StreamChunk]:
        system, msgs = self._split_system(messages)
        kwargs = dict(model=MODEL, max_tokens=2048, messages=msgs)
        if system:
            kwargs["system"] = system

        async with self._client.messages.stream(**kwargs) as s:
            async for text in s.text_stream:
                yield StreamChunk(content=text)
            yield StreamChunk(content="", done=True)
