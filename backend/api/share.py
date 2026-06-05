"""Partage public de conversations."""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from .auth import get_current_user
from ..services.supabase import get_client

router = APIRouter(prefix="/api/share", tags=["share"])


class ShareRequest(BaseModel):
    session_id: str


@router.post("")
async def create_share(req: ShareRequest, user: dict = Depends(get_current_user)):
    """Crée un lien de partage public pour une session."""
    db = get_client()

    # Vérifie que la session appartient à l'utilisateur
    res = db.table("sessions").select("id, title").eq("id", req.session_id).eq("user_id", user["id"]).maybe_single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Session introuvable")

    share_id = str(uuid.uuid4())
    db.table("shared_sessions").upsert({
        "id": share_id,
        "session_id": req.session_id,
        "user_id": user["id"],
    }).execute()

    return {"share_id": share_id}


@router.get("/{share_id}")
async def get_shared(share_id: str):
    """Retourne le contenu d'une session partagée (public)."""
    db = get_client()

    res = db.table("shared_sessions").select("session_id").eq("id", share_id).maybe_single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Lien invalide ou expiré")

    session_id = res.data["session_id"]

    session_res = db.table("sessions").select("id, title, created_at").eq("id", session_id).maybe_single().execute()
    messages_res = (
        db.table("messages")
        .select("role, content, model, created_at")
        .eq("session_id", session_id)
        .order("created_at")
        .execute()
    )

    return {
        "session": session_res.data,
        "messages": messages_res.data or [],
    }
