import anthropic
from typing import AsyncIterator, Optional
from . import BaseLLMClient, LLMResponse, StreamChunk
from ..config import settings

MODEL = "claude-sonnet-4-6"

# Coûts réels vérifiés juin 2026
COST_INPUT_PER_TOKEN = 3.00 / 1_000_000
COST_OUTPUT_PER_TOKEN = 15.00 / 1_000_000


class ClaudeClient(BaseLLMClient):

    def __init__(self):
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    @staticmethod
    def _split_system(messages: list[dict]) -> tuple[Optional[str], list[dict]]:
        """Extrait le message system pour le passer en paramètre top-level (requis par Anthropic)."""
        if messages and messages[0].get("role") == "system":
            return messages[0]["content"], messages[1:]
        return None, messages

    async def complete(
        self,
        messages: list[dict],
        tools: Optional[list] = None,
        stream: bool = False,
    ) -> LLMResponse:
        system, msgs = self._split_system(messages)
        kwargs = dict(model=MODEL, max_tokens=8096, messages=msgs)
        if system:
            kwargs["system"] = system
        if tools:
            kwargs["tools"] = tools

        response = await self._client.messages.create(**kwargs)

        content = ""
        tool_calls = []
        for block in response.content:
            if block.type == "text":
                content = block.text
            elif block.type == "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                })

        tokens_in = response.usage.input_tokens
        tokens_out = response.usage.output_tokens
        cost = tokens_in * COST_INPUT_PER_TOKEN + tokens_out * COST_OUTPUT_PER_TOKEN

        return LLMResponse(
            content=content,
            model=MODEL,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_usd=cost,
            tool_calls=tool_calls or None,
        )

    async def stream(
        self,
        messages: list[dict],
        tools: Optional[list] = None,
    ) -> AsyncIterator[StreamChunk]:
        system, msgs = self._split_system(messages)
        kwargs = dict(model=MODEL, max_tokens=8096, messages=msgs)
        if system:
            kwargs["system"] = system
        if tools:
            kwargs["tools"] = tools

        async with self._client.messages.stream(**kwargs) as s:
            async for text in s.text_stream:
                yield StreamChunk(content=text)
            yield StreamChunk(content="", done=True)

    def format_tool_result(self, tool_use_id: str, result: str) -> dict:
        return {
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": result,
        }
