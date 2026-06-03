import json
import time
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from ..models.schemas import RunRequest
from ..agent.core import ReActAgent
from .auth import get_current_user
from ..services import usage as usage_svc

router = APIRouter()
_agent = ReActAgent()


async def event_stream(session_id: str, message: str, user_id: str):
    start = time.monotonic()
    total_cost = 0.0
    tool_count = 0
    final_model = "qwen"
    final_complexity = "simple"

    # Sauvegarde du message utilisateur
    await usage_svc.save_session(session_id, user_id)
    await usage_svc.save_message(session_id, role="user", content=message)

    full_response = ""

    async for event in _agent.run(session_id, message):
        sse = event.to_sse()
        yield sse

        if event.type == "routing":
            final_model = event.data.get("model", "qwen")
            final_complexity = event.data.get("complexity", "simple")
        elif event.type == "response":
            full_response += event.data.get("content", "")
        elif event.type == "tool_call":
            tool_count += 1

    # Sauvegarde de la réponse assistant
    duration_ms = int((time.monotonic() - start) * 1000)
    if full_response:
        await usage_svc.save_message(
            session_id, role="assistant", content=full_response, model=final_model
        )

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
    return StreamingResponse(
        event_stream(request.session_id, request.message, user["id"]),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/health")
async def health():
    return {"status": "ok"}
