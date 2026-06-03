"""Gestion des quotas et du suivi d'usage."""
from datetime import datetime
from .supabase import get_client

PLAN_LIMITS = {
    "free":     10,
    "pro":      150,
    "business": 600,
}


async def get_profile(user_id: str) -> dict | None:
    try:
        db = get_client()
        res = db.table("profiles").select("*").eq("id", user_id).maybe_single().execute()
        return res.data
    except Exception:
        return None


async def check_and_increment(user_id: str) -> tuple[bool, dict]:
    """
    Vérifie le quota et incrémente si OK.
    Retourne (allowed, profile).
    """
    db = get_client()
    res = db.rpc("increment_task_usage", {"p_user_id": user_id}).execute()
    allowed: bool = res.data
    profile = await get_profile(user_id)
    return allowed, profile or {}


async def save_session(session_id: str, user_id: str, title: str = "") -> None:
    try:
        db = get_client()
        db.table("sessions").upsert({
            "id": session_id,
            "user_id": user_id,
            "title": title or "Nouvelle conversation",
            "updated_at": datetime.utcnow().isoformat(),
        }).execute()
    except Exception:
        pass


async def save_message(
    session_id: str,
    role: str,
    content: str,
    model: str = "",
    tokens_in: int = 0,
    tokens_out: int = 0,
    cost_usd: float = 0.0,
) -> None:
    try:
        db = get_client()
        db.table("messages").insert({
            "session_id": session_id,
            "role": role,
            "content": content,
            "model": model,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "cost_usd": cost_usd,
        }).execute()
    except Exception:
        pass


async def save_task_run(
    session_id: str,
    user_id: str,
    model: str,
    complexity: str,
    tokens_in: int = 0,
    tokens_out: int = 0,
    cost_usd: float = 0.0,
    tool_calls: int = 0,
    duration_ms: int = 0,
) -> None:
    try:
        db = get_client()
        db.table("task_runs").insert({
            "session_id": session_id,
            "user_id": user_id,
            "model": model,
            "complexity": complexity,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "cost_usd": cost_usd,
            "tool_calls": tool_calls,
            "duration_ms": duration_ms,
        }).execute()
    except Exception:
        pass


async def get_sessions(user_id: str, limit: int = 20) -> list[dict]:
    db = get_client()
    res = (
        db.table("sessions")
        .select("id, title, created_at, updated_at")
        .eq("user_id", user_id)
        .order("updated_at", desc=True)
        .limit(limit)
        .execute()
    )
    return res.data or []


async def get_messages(session_id: str) -> list[dict]:
    db = get_client()
    res = (
        db.table("messages")
        .select("role, content, model, cost_usd, created_at")
        .eq("session_id", session_id)
        .order("created_at")
        .execute()
    )
    return res.data or []
