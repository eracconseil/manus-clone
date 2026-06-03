import httpx
from ..config_tools import get_brave_key

BRAVE_API_URL = "https://api.search.brave.com/res/v1/web/search"


async def web_search(query: str, count: int = 5) -> str:
    api_key = get_brave_key()
    if not api_key:
        return _fallback_search(query)

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            BRAVE_API_URL,
            headers={"Accept": "application/json", "X-Subscription-Token": api_key},
            params={"q": query, "count": count},
        )
        resp.raise_for_status()
        data = resp.json()

    results = data.get("web", {}).get("results", [])
    if not results:
        return f"Aucun résultat pour : {query}"

    lines = []
    for r in results:
        title = r.get("title", "")
        url = r.get("url", "")
        desc = r.get("description", "")
        lines.append(f"**{title}**\n{url}\n{desc}")

    return "\n\n".join(lines)


def _fallback_search(query: str) -> str:
    return (
        f"[Recherche web non disponible — clé Brave manquante]\n"
        f"Requête : {query}\n"
        f"Ajoutez BRAVE_SEARCH_API_KEY dans le fichier .env pour activer la recherche."
    )
