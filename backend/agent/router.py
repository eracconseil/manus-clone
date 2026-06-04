from ..models.schemas import TaskComplexity

COMPLEX_KEYWORDS = {
    "recherche", "search", "web", "trouve", "find", "analyse", "plan", "code",
    "script", "programme", "crée", "génère", "génère", "generate", "create",
    "rapport", "report", "compare", "évalue", "evaluate", "stratégie", "strategy",
    "implémente", "implement", "développe", "develop", "debug", "corrige",
    "calcule", "simulate", "scrape", "télécharge", "download", "fichier", "file",
    "execute", "exécute", "run", "teste", "test",
}

SIMPLE_KEYWORDS = {
    "bonjour", "hello", "salut", "hi", "merci", "thanks", "ok", "oui", "non",
    "traduis", "translate", "résume", "summarize", "explique", "explain",
    "définis", "define", "qu'est-ce", "what is", "c'est quoi", "dis-moi",
    "reformule", "rephrase", "liste", "list",
}


async def route_task(task: str, context_length: int = 0) -> TaskComplexity:
    if context_length > 8000:
        return TaskComplexity.LONG_CONTEXT

    task_lower = task.lower()
    word_count = len(task.split())

    # Long context if message itself is very long
    if word_count > 300:
        return TaskComplexity.LONG_CONTEXT

    # Complex if contains complex keywords
    if any(kw in task_lower for kw in COMPLEX_KEYWORDS):
        return TaskComplexity.COMPLEX

    # Simple for short greetings / definitions / translations
    if word_count <= 15 or any(kw in task_lower for kw in SIMPLE_KEYWORDS):
        return TaskComplexity.SIMPLE

    # Default: complex
    return TaskComplexity.COMPLEX
