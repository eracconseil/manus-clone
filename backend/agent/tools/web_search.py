"""
Recherche web — Brave Search (si clé dispo) ou DuckDuckGo (gratuit, sans clé).
"""
import httpx

BRAVE_API_URL = "https://api.search.brave.com/res/v1/web/search"
DDG_API_URL = "https://api.duckduckgo.com/"


async def web_search(query: str, count: int = 8) -> str:
    from ..config_tools import get_brave_key
    api_key = get_brave_key()

    if api_key:
        return await _brave_search(query, count, api_key)
    return await _ddg_search(query, count)


async def _brave_search(query: str, count: int, api_key: str) -> str:
    try:
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
            return await _ddg_search(query, count)

        lines = []
        for r in results:
            title = r.get("title", "")
            url = r.get("url", "")
            desc = r.get("description", "")
            age = r.get("age", "")
            extra = r.get("extra_snippets", [])
            entry = f"**{title}**\n{url}"
            if age:
                entry += f" [{age}]"
            entry += f"\n{desc}"
            if extra:
                entry += "\n" + " | ".join(extra[:2])
            lines.append(entry)
        return "\n\n".join(lines)
    except Exception:
        return await _ddg_search(query, count)


async def _ddg_search(query: str, count: int = 5) -> str:
    """DuckDuckGo Instant Answer API + HTML scraping pour résultats complets."""
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            # DuckDuckGo Instant Answer API
            resp = await client.get(
                DDG_API_URL,
                params={"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"},
            )
            resp.raise_for_status()
            data = resp.json()

        lines = []

        # Réponse directe
        if data.get("AbstractText"):
            lines.append(f"**{data.get('Heading', query)}**\n{data.get('AbstractURL', '')}\n{data['AbstractText']}")

        # Résultats liés
        for r in data.get("RelatedTopics", [])[:count]:
            if isinstance(r, dict) and r.get("Text"):
                url = r.get("FirstURL", "")
                text = r.get("Text", "")
                lines.append(f"• {text}\n  {url}")

        if lines:
            return "\n\n".join(lines)

        # Fallback : recherche HTML DuckDuckGo
        return await _ddg_html_search(query, count)

    except Exception as e:
        return await _ddg_html_search(query, count)


async def _ddg_html_search(query: str, count: int = 5) -> str:
    """Scraping léger de DuckDuckGo HTML."""
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.get(
                "https://html.duckduckgo.com/html/",
                params={"q": query},
                headers={"User-Agent": "Mozilla/5.0 (compatible; OrionBot/1.0)"},
            )
            resp.raise_for_status()
            html = resp.text

        # Extraction simple des résultats
        import re
        results = []
        # Pattern pour extraire titres et URLs depuis le HTML DDG
        snippets = re.findall(
            r'class="result__snippet"[^>]*>([^<]+)',
            html, re.DOTALL
        )
        titles = re.findall(
            r'class="result__a"[^>]*>([^<]+)',
            html
        )
        urls = re.findall(
            r'uddg=([^&"]+)',
            html
        )

        for i in range(min(count, len(titles))):
            title = titles[i].strip() if i < len(titles) else ""
            url = httpx.URL(urls[i]).params.get("uddg", urls[i]) if i < len(urls) else ""
            snippet = snippets[i].strip() if i < len(snippets) else ""
            if title:
                results.append(f"**{title}**\n{url}\n{snippet}")

        if results:
            return "\n\n".join(results)

        return f"Recherche effectuée pour : {query}\n(Résultats non disponibles — essayez de reformuler)"
    except Exception as e:
        return f"Erreur de recherche : {e}"
