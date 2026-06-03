from ..llm.qwen import QwenClient
from ..models.schemas import TaskComplexity

_qwen = QwenClient()

SYSTEM_PROMPT = """Tu es un classificateur de tâches. Analyse la tâche et réponds UNIQUEMENT par un seul mot :
- SIMPLE : résumé court, extraction de données, classification, traduction, reformulation
- LONG_CONTEXT : analyse de PDF ou document long, contexte > 8000 tokens
- COMPLEX : planification multi-étapes, raisonnement, recherche web, génération de code, décisions

Réponds uniquement par : SIMPLE, LONG_CONTEXT ou COMPLEX"""


async def route_task(task: str, context_length: int = 0) -> TaskComplexity:
    # Long contexte détecté directement par la taille
    if context_length > 8000:
        return TaskComplexity.LONG_CONTEXT

    response = await _qwen.complete(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": task},
        ]
    )

    label = response.content.strip().upper()

    if label == "SIMPLE":
        return TaskComplexity.SIMPLE
    if label == "LONG_CONTEXT":
        return TaskComplexity.LONG_CONTEXT
    return TaskComplexity.COMPLEX
