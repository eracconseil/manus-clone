"""API mémoire utilisateur."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from .auth import get_current_user
from ..services.memory import get_memory, update_memory

router = APIRouter(prefix="/api/memory", tags=["memory"])


class MemoryUpdate(BaseModel):
    content: str


@router.get("")
async def read_memory(user: dict = Depends(get_current_user)):
    content = await get_memory(user["id"])
    return {"content": content}


@router.put("")
async def write_memory(req: MemoryUpdate, user: dict = Depends(get_current_user)):
    await update_memory(user["id"], req.content)
    return {"ok": True}
