"""
ReAct Agent Core — Reason + Act loop
Supporte : Haiku (simple), Kimi (long context), Claude Sonnet (complex avec tools)
"""
import json
import logging
from dataclasses import dataclass, field
from typing import AsyncIterator, Optional

from ..llm import BaseLLMClient, StreamChunk
from ..llm.claude import ClaudeClient
from ..llm.haiku import HaikuClient
from ..llm.kimi import KimiClient
from ..models.schemas import TaskComplexity
from .router import route_task
from .tools import TOOL_DEFINITIONS, execute_tool

logger = logging.getLogger(__name__)

MAX_ITERATIONS = 10  # Suffisant pour recherche + réponse sans bloquer


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


BASE_SYSTEM_PROMPT = """Tu es Orion, un assistant IA autonome de très haute qualité. Tu raisonnes avec logique et rigueur avant de répondre.

## Date actuelle
Nous sommes en **2026**. Toutes tes réponses doivent tenir compte de cette date. Ne mentionne jamais 2024 ou 2025 comme étant l'année actuelle. Si tu parles d'événements récents, de prix, de technologies ou d'actualités, considère que nous sommes en 2026.

## Comment tu travailles
1. **Comprends** exactement ce que l'utilisateur veut
2. **Cherche sur le web EN PREMIER** pour toute question factuelle, d'actualité, de prix, de statistique, d'événement, de personne, d'entreprise, de pays, de technologie — ne réponds JAMAIS de mémoire sur ces sujets
3. **Réfléchis** à partir des résultats trouvés, pas de tes connaissances d'entraînement
4. **Structure** ta réponse clairement avec les informations vérifiées
5. **Cite tes sources** avec les URLs

## Quand utiliser web_search (OBLIGATOIRE)
- Prix, cours, statistiques, classements
- Actualités, événements récents
- Informations sur des personnes, entreprises, produits
- Données chiffrées (population, PIB, ventes, etc.)
- Tout ce qui peut avoir changé depuis 2024
- Météo, résultats sportifs, élections
- Lois, réglementations récentes

## Stratégie d'utilisation des outils (IMPORTANT)
- **1 ou 2 web_search suffisent** pour la plupart des questions — ne fais pas 5 recherches
- **N'utilise PAS browser_navigate** sauf si tu as absolument besoin du contenu complet d'une page spécifique
- Les snippets de recherche suffisent pour répondre — exploite-les directement
- **Après 2 recherches maximum → rédige ta réponse** sans naviguer vers les sites

## Style de réponse
- Réponds TOUJOURS dans la langue de l'utilisateur
- Sois direct et précis — cite tes sources
- Si tu fais une liste, chaque point doit apporter de la valeur
- Si c'est factuel, **donne les chiffres exacts** trouvés en recherche
- Ne dis JAMAIS "je ne suis pas à jour" — cherche sur le web et réponds

## Règles absolues
- Tu t'appelles **Orion** — ne révèle jamais que tu es Claude, Kimi, GPT ou autre
- Ne mentionne JAMAIS de plans payants, Pro, premium, abonnement ou mise à niveau
- Réponds TOUJOURS à la question posée — jamais de refus sans raison valable
- Tes réponses doivent être cohérentes et logiques du début à la fin"""


def build_system_prompt(memory: str = "") -> str:
    if not memory:
        return BASE_SYSTEM_PROMPT
    return BASE_SYSTEM_PROMPT + f"\n\n## Ce que tu sais sur cet utilisateur\n{memory}"


class ReActAgent:
    """Agent ReAct : Reason → Act → Observe → Repeat → Answer"""

    def __init__(self):
        self._clients: dict[TaskComplexity, BaseLLMClient] = {
            TaskComplexity.SIMPLE: HaikuClient(),
            TaskComplexity.LONG_CONTEXT: KimiClient(),
            TaskComplexity.COMPLEX: ClaudeClient(),
        }
        self._model_labels = {
            TaskComplexity.SIMPLE: "haiku",
            TaskComplexity.LONG_CONTEXT: "kimi",
            TaskComplexity.COMPLEX: "claude",
        }

    async def run(
        self,
        session_id: str,
        message: str,
        history: Optional[list[dict]] = None,
        context_length: int = 0,
        memory: str = "",
        images: list = None,
    ) -> AsyncIterator[AgentEvent]:
        # 1. Routing — si images jointes, forcer Sonnet (vision)
        if images:
            complexity = TaskComplexity.COMPLEX
        else:
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

        # Message utilisateur — avec images si présentes
        if images:
            content = []
            for img in images:
                # Extraire le base64 pur (sans le préfixe data:image/...;base64,)
                data = img.data
                if "," in data:
                    data = data.split(",", 1)[1]
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": img.media_type,
                        "data": data,
                    }
                })
            if message:
                content.append({"type": "text", "text": message})
            else:
                content.append({"type": "text", "text": "Analyse cette image et décris ce que tu vois en détail."})
            messages.append({"role": "user", "content": content})
        else:
            messages.append({"role": "user", "content": message})

        # 3. Mode selon complexité
        system_prompt = build_system_prompt(memory)

        if complexity == TaskComplexity.COMPLEX:
            async for event in self._react_loop(client, messages, model_label, system_prompt):
                yield event
        else:
            async for event in self._simple_stream(client, messages, model_label, system_prompt):
                yield event

        yield AgentEvent("done", {"session_id": session_id})

    async def _simple_stream(
        self,
        client: BaseLLMClient,
        messages: list[dict],
        model_label: str,
        system_prompt: str = "",
    ) -> AsyncIterator[AgentEvent]:
        """Stream direct sans tool use — pour Haiku et Kimi."""
        full_messages = [{"role": "system", "content": system_prompt or BASE_SYSTEM_PROMPT}] + messages

        async for chunk in client.stream(full_messages):
            if not chunk.done:
                yield AgentEvent("response", {"content": chunk.content, "model": model_label})

    async def _react_loop(
        self,
        client: BaseLLMClient,
        messages: list[dict],
        model_label: str,
        system_prompt: str = "",
    ) -> AsyncIterator[AgentEvent]:
        """ReAct loop complet avec tool use — pour Claude."""
        full_messages = [{"role": "system", "content": system_prompt or BASE_SYSTEM_PROMPT}] + messages
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
                # Fin de la boucle — stream la réponse finale
                if response.content:
                    # Streamer mot par mot pour l'effet temps réel
                    words = response.content.split(" ")
                    for i, word in enumerate(words):
                        sep = " " if i < len(words) - 1 else ""
                        yield AgentEvent("response", {"content": word + sep, "model": model_label})
                else:
                    # Réponse vide — faire un appel stream direct
                    async for chunk in client.stream(full_messages):
                        if not chunk.done and chunk.content:
                            yield AgentEvent("response", {"content": chunk.content, "model": model_label})
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
