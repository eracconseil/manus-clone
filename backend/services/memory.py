"""Mémoire persistante de l'agent par utilisateur."""
from .supabase import get_client


async def get_memory(user_id: str) -> str:
    """Retourne le bloc mémoire de l'utilisateur sous forme de texte."""
    try:
        db = get_client()
        res = db.table("user_memory").select("content").eq("user_id", user_id).maybe_single().execute()
        if res.data:
            return res.data.get("content", "")
    except Exception:
        pass
    return ""


async def update_memory(user_id: str, content: str) -> None:
    try:
        db = get_client()
        db.table("user_memory").upsert({
            "user_id": user_id,
            "content": content,
        }).execute()
    except Exception:
        pass


async def extract_memory_from_conversation(messages: list[dict], llm_client) -> str | None:
    """
    Demande au LLM d'extraire les préférences et faits importants de la conversation.
    Retourne None si rien à retenir.
    """
    if len(messages) < 4:
        return None

    summary_prompt = [
        {"role": "user", "content": (
            "Lis cette conversation et extrait les informations importantes sur l'utilisateur "
            "(préférences, contexte métier, nom, outils préférés, style de communication, etc.) "
            "en 3-5 bullet points courts. Si rien d'important, réponds juste 'RIEN'.\n\n"
            + "\n".join(f"{m['role'].upper()}: {m['content'][:200]}" for m in messages[-6:])
        )}
    ]

    try:
        resp = await llm_client.complete(messages=summary_prompt, tools=None)
        result = resp.content.strip() if resp.content else ""
        if result and result != "RIEN" and len(result) > 10:
            return result
    except Exception:
        pass
    return None
