"""
Registre des outils disponibles pour l'agent ReAct.
Expose TOOL_DEFINITIONS (format Anthropic) et execute_tool().
"""
from .web_search import web_search
from .browser import browser_navigate
from .code_executor import code_executor
from .file_manager import file_read, file_write, file_list
from .image_gen import generate_image

# Définitions au format Anthropic tool_use
TOOL_DEFINITIONS = [
    {
        "name": "web_search",
        "description": "Effectue une recherche web et retourne les résultats. Utilise cet outil pour trouver des informations récentes, des faits, des prix, des actualités.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "La requête de recherche"},
                "count": {"type": "integer", "description": "Nombre de résultats (défaut: 5)", "default": 5},
            },
            "required": ["query"],
        },
    },
    {
        "name": "browser_navigate",
        "description": "Navigue vers une URL et retourne le contenu textuel de la page. Utile pour lire des articles, de la documentation, des pages web.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "L'URL complète à visiter (doit commencer par http:// ou https://)"},
            },
            "required": ["url"],
        },
    },
    {
        "name": "code_executor",
        "description": "Exécute du code Python et retourne le résultat. Idéal pour les calculs, la manipulation de données, les algorithmes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Le code Python à exécuter"},
                "language": {"type": "string", "description": "Langage (défaut: python)", "default": "python"},
            },
            "required": ["code"],
        },
    },
    {
        "name": "file_read",
        "description": "Lit le contenu d'un fichier dans le workspace.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Chemin relatif du fichier dans le workspace"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "file_write",
        "description": "Écrit ou crée un fichier dans le workspace.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Chemin relatif du fichier"},
                "content": {"type": "string", "description": "Contenu à écrire"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "generate_image",
        "description": "Génère une image à partir d'une description textuelle (prompt). Utilise cet outil quand l'utilisateur demande de créer, générer ou dessiner une image.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Description détaillée de l'image à générer en anglais pour de meilleurs résultats"},
                "width": {"type": "integer", "description": "Largeur en pixels (défaut: 1024)", "default": 1024},
                "height": {"type": "integer", "description": "Hauteur en pixels (défaut: 1024)", "default": 1024},
            },
            "required": ["prompt"],
        },
    },
    {
        "name": "file_list",
        "description": "Liste les fichiers dans le workspace ou un sous-répertoire.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Sous-répertoire à lister (optionnel)", "default": ""},
            },
        },
    },
]


async def execute_tool(name: str, args: dict) -> str:
    """Dispatche l'exécution vers le bon outil."""
    match name:
        case "web_search":
            return await web_search(args.get("query", ""), args.get("count", 5))
        case "browser_navigate":
            return await browser_navigate(args.get("url", ""))
        case "code_executor":
            return await code_executor(args.get("code", ""), args.get("language", "python"))
        case "file_read":
            return await file_read(args.get("path", ""))
        case "file_write":
            return await file_write(args.get("path", ""), args.get("content", ""))
        case "file_list":
            return await file_list(args.get("path", ""))
        case "generate_image":
            return await generate_image(args.get("prompt", ""), args.get("width", 1024), args.get("height", 1024))
        case _:
            return f"Outil inconnu : {name}"
