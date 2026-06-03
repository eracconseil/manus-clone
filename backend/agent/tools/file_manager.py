"""
Gestionnaire de fichiers pour l'agent — lecture et écriture dans un workspace isolé.
"""
import os
import pathlib

# Workspace isolé dans le répertoire de travail de l'app
_WORKSPACE = pathlib.Path("workspace").resolve()
_WORKSPACE.mkdir(exist_ok=True)
_MAX_READ_BYTES = 50_000  # 50 KB max par lecture


def _safe_path(relative_path: str) -> pathlib.Path:
    """Empêche les path traversal attacks."""
    target = (_WORKSPACE / relative_path).resolve()
    if not str(target).startswith(str(_WORKSPACE)):
        raise ValueError(f"Accès refusé : chemin hors workspace — {relative_path}")
    return target


async def file_read(path: str) -> str:
    try:
        target = _safe_path(path)
        if not target.exists():
            return f"Fichier introuvable : {path}"
        if target.stat().st_size > _MAX_READ_BYTES:
            return f"Fichier trop volumineux (>{_MAX_READ_BYTES // 1000} KB) : {path}"
        return target.read_text(encoding="utf-8")
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Erreur lecture : {e}"


async def file_write(path: str, content: str) -> str:
    try:
        target = _safe_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Fichier écrit : {path} ({len(content)} caractères)"
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Erreur écriture : {e}"


async def file_list(path: str = "") -> str:
    try:
        target = _safe_path(path) if path else _WORKSPACE
        if not target.is_dir():
            return f"Pas un répertoire : {path}"
        entries = []
        for entry in sorted(target.iterdir()):
            kind = "📁" if entry.is_dir() else "📄"
            size = entry.stat().st_size if entry.is_file() else 0
            entries.append(f"{kind} {entry.name} ({size} B)" if entry.is_file() else f"{kind} {entry.name}/")
        return "\n".join(entries) if entries else "(répertoire vide)"
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Erreur liste : {e}"
