"""
Génération d'images via Pollinations.ai (gratuit, sans clé API).
"""
import httpx
import urllib.parse


async def generate_image(prompt: str, width: int = 1024, height: int = 1024) -> str:
    """
    Génère une image à partir d'un prompt texte.
    Retourne l'URL de l'image générée.
    """
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true&enhance=true"

    # Vérifier que l'URL est accessible
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                return f"![Image générée]({url})\n\n*Prompt : {prompt}*"
    except Exception:
        pass

    # Fallback : retourner l'URL directement
    return f"![Image générée]({url})\n\n*Prompt : {prompt}*"
