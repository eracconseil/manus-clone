from ..models.schemas import TaskComplexity

# Questions qui nécessitent Sonnet (recherche, analyse, code, raisonnement)
async def route_task(task: str, context_length: int = 0) -> TaskComplexity:
    if context_length > 8000:
        return TaskComplexity.LONG_CONTEXT

    task_lower = task.lower().strip()
    word_count = len(task.split())

    if word_count > 300:
        return TaskComplexity.LONG_CONTEXT

    # Haiku uniquement pour les salutations pures et très courtes
    GREETINGS = {"bonjour", "hello", "salut", "hi", "merci", "bonsoir", "bye", "ok", "oui", "non"}
    if word_count <= 4 and any(g in task_lower for g in GREETINGS):
        return TaskComplexity.SIMPLE

    # Tout le reste → Sonnet avec outils
    return TaskComplexity.COMPLEX
