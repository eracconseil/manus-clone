"""
ReAct Agent Core — Reason + Act loop
Supporte : Qwen (simple), Kimi (long context), Claude (complex avec tools)
"""
import json
import logging
from dataclasses import dataclass, field
from typing import AsyncIterator, Optional

from ..llm import BaseLLMClient, StreamChunk
from ..llm.claude import ClaudeClient
from ..llm.kimi import KimiClient
from ..llm.qwen import QwenClient
from ..models.schemas import TaskComplexity
from .router import route_task
from .tools import TOOL_DEFINITIONS, execute_tool

logger = logging.getLogger(__name__)

MAX_ITERATIONS = 8  # Sécurité anti-boucle infinie


@dataclass
class AgentEvent:
    type: str  # routing | thinking | tool_call | tool_result | response | done | error
    data: dict = field(default_factory=dict)

    def to_sse(self) -> str:
        payload = {"type": self.type, **self.data}
        return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@dataclass
class AgentResult:
    content: str
    model: str
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    iterations: int = 0


SYSTEM_PROMPT = """Tu es Orion, un agent IA autonome expert. Tu peux utiliser des outils pour accomplir des tâches complexes.

Stratégie :
1. Analyse la demande
2. Utilise les outils nécessaires (recherche web, code, navigation)
3. Synthétise une réponse claire et structurée
4. Cite tes sources quand tu utilises la recherche web

Sois concis, précis, et toujours utile."""


class ReActAgent:
    """Agent ReAct : Reason → Act → Observe → Repeat → Answer"""

    def __init__(self):
        self._clients: dict[TaskComplexity, BaseLLMClient] = {
            TaskComplexity.SIMPLE: QwenClient(),
            TaskComplexity.LONG_CONTEXT: KimiClient(),
            TaskComplexity.COMPLEX: ClaudeClient(),
        }
        self._model_labels = {
            TaskComplexity.SIMPLE: "qwen",
            TaskComplexity.LONG_CONTEXT: "kimi",
            TaskComplexity.COMPLEX: "claude",
        }

    async def run(
        self,
        session_id: str,
        message: str,
        history: Optional[list[dict]] = None,
        context_length: int = 0,
    ) -> AsyncIterator[AgentEvent]:
        # 1. Routing
        complexity = await route_task(message, context_length)
        model_label = self._model_labels[complexity]
        client = self._clients[complexity]

        yield AgentEvent("routing", {
            "model": model_label,
            "complexity": complexity.value,
            "session_id": session_id,
        })

        # 2. Construction des messages
        messages = []
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message})

        # 3. Mode selon complexité
        if complexity == TaskComplexity.COMPLEX:
            # ReAct loop avec tool use (Claude uniquement)
            async for event in self._react_loop(client, messages, model_label):
                yield event
        else:
            # Stream direct pour Qwen/Kimi (pas de tool use)
            async for event in self._simple_stream(client, messages, model_label):
                yield event

        yield AgentEvent("done", {"session_id": session_id})

    async def _simple_stream(
        self,
        client: BaseLLMClient,
        messages: list[dict],
        model_label: str,
    ) -> AsyncIterator[AgentEvent]:
        """Stream direct sans tool use — pour Qwen et Kimi."""
        # Ajout du system prompt
        full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

        async for chunk in client.stream(full_messages):
            if not chunk.done:
                yield AgentEvent("response", {"content": chunk.content, "model": model_label})

    async def _react_loop(
        self,
        client: BaseLLMClient,
        messages: list[dict],
        model_label: str,
    ) -> AsyncIterator[AgentEvent]:
        """ReAct loop complet avec tool use — pour Claude."""
        full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        iterations = 0

        while iterations < MAX_ITERATIONS:
            iterations += 1

            try:
                response = await client.complete(
                    messages=full_messages,
                    tools=TOOL_DEFINITIONS,
                )
            except Exception as e:
                yield AgentEvent("error", {"message": str(e), "model": model_label})
                return

            # Réponse textuelle
            if response.content:
                yield AgentEvent("thinking", {
                    "content": response.content,
                    "model": model_label,
                    "iteration": iterations,
                })

            # Tool calls — format Anthropic : liste de ContentBlock avec type="tool_use"
            tool_calls = response.tool_calls or []
            if not tool_calls:
                # Fin de la boucle — stream la réponse finale mot par mot
                if response.content:
                    words = response.content.split(" ")
                    for i, word in enumerate(words):
                        sep = " " if i < len(words) - 1 else ""
                        yield AgentEvent("response", {
                            "content": word + sep,
                            "model": model_label,
                        })
                return

            # Construit le message assistant avec les tool_use blocks (format Anthropic)
            assistant_content = []
            if response.content:
                assistant_content.append({"type": "text", "text": response.content})
            for tc in tool_calls:
                assistant_content.append({
                    "type": "tool_use",
                    "id": tc["id"],
                    "name": tc["name"],
                    "input": tc["input"],
                })
            full_messages.append({"role": "assistant", "content": assistant_content})

            # Exécution des outils + collecte des résultats
            tool_results_content = []
            for tool_call in tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["input"]
                tool_id = tool_call["id"]

                yield AgentEvent("tool_call", {
                    "tool": tool_name,
                    "args": tool_args,
                    "iteration": iterations,
                })

                try:
                    result = await execute_tool(tool_name, tool_args)
                    result_str = result[:4000] if isinstance(result, str) else str(result)[:4000]
                    yield AgentEvent("tool_result", {
                        "tool": tool_name,
                        "result": result_str,
                        "iteration": iterations,
                    })
                except Exception as e:
                    result_str = f"Erreur outil {tool_name}: {e}"
                    yield AgentEvent("tool_result", {
                        "tool": tool_name,
                        "result": result_str,
                        "error": True,
                        "iteration": iterations,
                    })

                tool_results_content.append({
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": result_str,
                })

            # Message user avec les résultats (format Anthropic)
            full_messages.append({"role": "user", "content": tool_results_content})

        # Sécurité : max iterations atteint
        yield AgentEvent("error", {
            "message": f"Max iterations ({MAX_ITERATIONS}) atteint",
            "model": model_label,
        })
