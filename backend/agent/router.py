from ..models.schemas import TaskComplexity

# Seulement les salutations pures → Haiku
SIMPLE_KEYWORDS = {
    "bonjour", "hello", "salut", "hi", "merci", "thanks", "bonsoir",
    "au revoir", "bye", "ok", "oui", "non", "ça va", "ca va",
}


async def route_task(task: str, context_length: int = 0) -> TaskComplexity:
    if context_length > 8000:
        return TaskComplexity.LONG_CONTEXT

    task_lower = task.lower().strip()
    word_count = len(task.split())

    # Long context si message très long
    if word_count > 300:
        return TaskComplexity.LONG_CONTEXT

    # Haiku SEULEMENT pour les salutations courtes (<= 5 mots)
    if word_count <= 5 and any(kw in task_lower for kw in SIMPLE_KEYWORDS):
        return TaskComplexity.SIMPLE

    # Tout le reste → Sonnet (qualité maximale)
    return TaskComplexity.COMPLEX
