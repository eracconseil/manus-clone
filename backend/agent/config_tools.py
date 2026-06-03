"""Accesseurs pour les clés API des outils — évite l'import circulaire."""
from ..config import settings


def get_brave_key() -> str:
    return settings.brave_search_api_key


def get_e2b_key() -> str:
    return settings.e2b_api_key
