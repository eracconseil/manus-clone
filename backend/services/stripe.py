"""Stripe billing : checkout, webhook, gestion des abonnements."""
import stripe
from ..config import settings
from .supabase import get_client

stripe.api_key = settings.stripe_secret_key

PLAN_PRICE_IDS = {
    "pro":      settings.stripe_pro_price_id,
    "business": settings.stripe_business_price_id,
}

PLAN_LIMITS = {
    "free":     10,
    "pro":      150,
    "business": 600,
}


async def create_checkout_session(user_id: str, email: str, plan: str) -> str:
    """Crée une session Stripe Checkout et retourne l'URL."""
    price_id = PLAN_PRICE_IDS.get(plan)
    if not price_id:
        raise ValueError(f"Plan inconnu : {plan}")

    db = get_client()
    profile = db.table("profiles").select("stripe_customer_id").eq("id", user_id).single().execute()
    customer_id = profile.data.get("stripe_customer_id") if profile.data else None

    kwargs = {
        "mode": "subscription",
        "line_items": [{"price": price_id, "quantity": 1}],
        "success_url": f"{settings.frontend_url}/dashboard?upgraded=1",
        "cancel_url": f"{settings.frontend_url}/dashboard",
        "metadata": {"user_id": user_id, "plan": plan},
        "subscription_data": {"metadata": {"user_id": user_id, "plan": plan}},
    }
    if customer_id:
        kwargs["customer"] = customer_id
    else:
        kwargs["customer_email"] = email

    session = stripe.checkout.Session.create(**kwargs)
    return session.url


async def create_portal_session(user_id: str) -> str:
    """Retourne l'URL du portail client Stripe pour gérer l'abonnement."""
    db = get_client()
    profile = db.table("profiles").select("stripe_customer_id").eq("id", user_id).single().execute()
    customer_id = profile.data.get("stripe_customer_id") if profile.data else None
    if not customer_id:
        raise ValueError("Aucun compte Stripe trouvé")

    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=f"{settings.frontend_url}/dashboard",
    )
    return session.url


def handle_webhook(payload: bytes, sig_header: str) -> dict:
    """Vérifie la signature et retourne l'événement Stripe."""
    return stripe.Webhook.construct_event(
        payload, sig_header, settings.stripe_webhook_secret
    )


async def process_webhook_event(event: dict) -> None:
    """Met à jour le profil utilisateur selon l'événement Stripe."""
    db = get_client()
    etype = event["type"]

    if etype == "checkout.session.completed":
        data = event["data"]["object"]
        user_id = data["metadata"].get("user_id")
        plan = data["metadata"].get("plan", "free")
        customer_id = data.get("customer")
        sub_id = data.get("subscription")
        if user_id:
            db.table("profiles").update({
                "plan": plan,
                "tasks_limit": PLAN_LIMITS.get(plan, 10),
                "stripe_customer_id": customer_id,
                "stripe_subscription_id": sub_id,
            }).eq("id", user_id).execute()

    elif etype in ("customer.subscription.updated", "customer.subscription.deleted"):
        sub = event["data"]["object"]
        customer_id = sub.get("customer")
        status = sub.get("status")
        plan = sub.get("metadata", {}).get("plan", "free")

        # Si annulé ou impayé → retour au plan free
        if status in ("canceled", "unpaid", "past_due"):
            plan = "free"

        profile = db.table("profiles").select("id").eq("stripe_customer_id", customer_id).single().execute()
        if profile.data:
            db.table("profiles").update({
                "plan": plan,
                "tasks_limit": PLAN_LIMITS.get(plan, 10),
            }).eq("stripe_customer_id", customer_id).execute()

    elif etype == "invoice.payment_failed":
        # Notifier (log seulement pour l'instant)
        print(f"[Stripe] Paiement échoué : {event['data']['object'].get('customer')}")
