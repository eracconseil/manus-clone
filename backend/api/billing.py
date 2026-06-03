"""Routes Stripe billing."""
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from .auth import get_current_user
from ..services import stripe as stripe_svc
from ..services.usage import get_profile

router = APIRouter(prefix="/api/billing", tags=["billing"])


class CheckoutRequest(BaseModel):
    plan: str  # pro | business


@router.post("/checkout")
async def checkout(req: CheckoutRequest, user: dict = Depends(get_current_user)):
    try:
        url = await stripe_svc.create_checkout_session(
            user_id=user["id"], email=user["email"], plan=req.plan
        )
        return {"url": url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/portal")
async def portal(user: dict = Depends(get_current_user)):
    try:
        url = await stripe_svc.create_portal_session(user_id=user["id"])
        return {"url": url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/profile")
async def profile(user: dict = Depends(get_current_user)):
    p = await get_profile(user["id"])
    if not p:
        # Profil inexistant (dev mode)
        return {
            "plan": "free",
            "tasks_used": 0,
            "tasks_limit": 10,
            "email": user["email"],
        }
    return {
        "plan": p.get("plan", "free"),
        "tasks_used": p.get("tasks_used", 0),
        "tasks_limit": p.get("tasks_limit", 10),
        "email": user["email"],
    }


@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    try:
        event = stripe_svc.handle_webhook(payload, sig)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    await stripe_svc.process_webhook_event(event)
    return {"ok": True}
