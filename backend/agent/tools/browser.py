"""
Navigateur headless pour scraping de pages web.
Utilise httpx pour les pages simples, playwright pour le JS rendu.
"""
import re
import httpx

_MAX_CONTENT = 8_000  # caractères max retournés


async def browser_navigate(url: str) -> str:
    """Récupère le contenu texte d'une URL."""
    if not url.startswith(("http://", "https://")):
        return f"URL invalide : {url}"

    try:
        return await _fetch_with_httpx(url)
    except Exception as e:
        return f"Erreur navigation : {e}"


async def _fetch_with_httpx(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        if "text" not in content_type and "json" not in content_type:
            return f"Type de contenu non textuel : {content_type}"
        text = resp.text
        cleaned = _clean_html(text)
        if len(cleaned) > _MAX_CONTENT:
            cleaned = cleaned[:_MAX_CONTENT] + f"\n\n[... tronqué à {_MAX_CONTENT} caractères]"
        return cleaned


def _clean_html(html: str) -> str:
    """Extraction de texte basique depuis HTML."""
    # Supprime scripts, styles, commentaires
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    # Convertit certaines balises en texte lisible
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    html = re.sub(r"<p[^>]*>", "\n", html, flags=re.IGNORECASE)
    html = re.sub(r"<h[1-6][^>]*>", "\n## ", html, flags=re.IGNORECASE)
    html = re.sub(r"<li[^>]*>", "\n- ", html, flags=re.IGNORECASE)
    # Supprime toutes les balises restantes
    html = re.sub(r"<[^>]+>", "", html)
    # Nettoie les espaces
    html = re.sub(r"\n{3,}", "\n\n", html)
    html = re.sub(r"[ \t]+", " ", html)
    return html.strip()
