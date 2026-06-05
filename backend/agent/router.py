from ..models.schemas import TaskComplexity

# Questions qui nécessitent Sonnet (recherche, analyse, code, raisonnement)
COMPLEX_KEYWORDS = {
    "recherche", "search", "trouve", "find", "web", "internet", "actualité",
    "analyse", "analyser", "compare", "évalue", "stratégie",
    "code", "script", "programme", "bug", "debug", "développe", "implémente",
    "plan", "rapport", "rédige", "écris un", "crée", "génère",
    "calcule", "résous", "explique en détail", "approfondi",
    "investissement", "finance", "juridique", "médical", "scientifique",
    # Image generation
    "image", "photo", "illustration", "dessin", "dessine", "génère une image",
    "generate image", "picture", "visuel", "logo", "affiche", "poster",
}


async def route_task(task: str, context_length: int = 0) -> TaskComplexity:
    if context_length > 8000:
        return TaskComplexity.LONG_CONTEXT

    task_lower = task.lower().strip()
    word_count = len(task.split())

    # Long context si message très long
    if word_count > 300:
        return TaskComplexity.LONG_CONTEXT

    # Sonnet si mot-clé complexe détecté
    if any(kw in task_lower for kw in COMPLEX_KEYWORDS):
        return TaskComplexity.COMPLEX

    # Sonnet si question longue (>= 20 mots) — besoin de raisonnement
    if word_count >= 20:
        return TaskComplexity.COMPLEX

    # Haiku pour tout le reste (questions courtes, explications simples, conversation)
    return TaskComplexity.SIMPLE
