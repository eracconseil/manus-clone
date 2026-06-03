"""Middleware d'authentification Supabase JWT."""
from fastapi import HTTPException, Header
from supabase import create_client
from ..config import settings

_anon_client = create_client(settings.supabase_url, settings.supabase_service_key)


async def get_current_user(authorization: str = Header(default="")) -> dict:
    """
    Extrait et vérifie le JWT Supabase depuis le header Authorization.
    Retourne le user dict ou lève une 401.
    Mode dev : si pas de token, retourne un user anonyme fictif.
    """
    if not authorization.startswith("Bearer "):
        # Mode dev sans auth
        return {"id": "00000000-0000-0000-0000-000000000000", "email": "dev@localhost"}

    token = authorization.removeprefix("Bearer ").strip()
    try:
        res = _anon_client.auth.get_user(token)
        if not res.user:
            raise HTTPException(status_code=401, detail="Token invalide")
        return {"id": str(res.user.id), "email": res.user.email or ""}
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")
