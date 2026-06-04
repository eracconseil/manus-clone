import json
import time
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from ..models.schemas import RunRequest
from ..agent.core import ReActAgent
from .auth import get_current_user
from ..services import usage as usage_svc
from ..services.memory import get_memory

router = APIRouter()
_agent = ReActAgent()


ANON_USER_ID = "00000000-0000-0000-0000-000000000000"

async def event_stream(session_id: str, message: str, user_id: str):
    start = time.monotonic()
    tool_count = 0
    final_model = "haiku"
    final_complexity = "simple"
    is_anon = user_id == ANON_USER_ID

    import asyncio

    if not is_anon:
        # Sauvegarde du message utilisateur
        await usage_svc.save_session(session_id, user_id)
        await usage_svc.save_message(session_id, role="user", content=message)
        history_msgs, memory = await asyncio.gather(
            usage_svc.get_messages(session_id),
            get_memory(user_id),
        )
    else:
        history_msgs, memory = [], ""

    # Convertit l'historique en format messages (exclut le dernier message qui est celui qu'on envoie)
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in history_msgs[:-1]  # Le message user vient d'être sauvé, on l'exclut
    ] if history_msgs else []

    context_length = sum(len(m["content"]) for m in history)
    full_response = ""

    async for event in _agent.run(session_id, message, history=history, context_length=context_length, memory=memory):
        sse = event.to_sse()
        yield sse

        if event.type == "routing":
            final_model = event.data.get("model", "haiku")
            final_complexity = event.data.get("complexity", "simple")
        elif event.type == "response":
            full_response += event.data.get("content", "")
        elif event.type == "tool_call":
            tool_count += 1

    # Sauvegarde de la réponse assistant
    duration_ms = int((time.monotonic() - start) * 1000)
    if full_response and not is_anon:
        await usage_svc.save_message(
            session_id, role="assistant", content=full_response, model=final_model
        )
        title = message[:60] + ("…" if len(message) > 60 else "")
        await usage_svc.save_session(session_id, user_id, title=title)

    if not is_anon:
        await usage_svc.save_task_run(
            session_id=session_id,
            user_id=user_id,
            model=final_model,
            complexity=final_complexity,
            tool_calls=tool_count,
            duration_ms=duration_ms,
        )


@router.post("/agent/run")
async def run_agent(request: RunRequest, user: dict = Depends(get_current_user)):
    if user["id"] != ANON_USER_ID:
        allowed, profile = await usage_svc.check_and_increment(user["id"])
        if not allowed:
            async def quota_exceeded():
                yield f"data: {json.dumps({'type': 'error', 'message': 'Limite de tâches atteinte. Passez à Pro pour continuer.'})}\n\n"
            return StreamingResponse(quota_exceeded(), media_type="text/event-stream")

    return StreamingResponse(
        event_stream(request.session_id, request.message, user["id"]),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/health")
async def health():
    return {"status": "ok"}
