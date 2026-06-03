"""Routes historique des conversations."""
from fastapi import APIRouter, Depends
from .auth import get_current_user
from ..services.usage import get_sessions, get_messages

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("/sessions")
async def list_sessions(user: dict = Depends(get_current_user)):
    sessions = await get_sessions(user["id"])
    return {"sessions": sessions}


@router.get("/sessions/{session_id}/messages")
async def list_messages(session_id: str, user: dict = Depends(get_current_user)):
    messages = await get_messages(session_id)
    return {"messages": messages}
