"""
Exécution de code Python dans un sandbox sécurisé.
Utilise E2B si la clé est configurée, sinon sandbox local restrictif.
"""
import asyncio
import sys
import io
import traceback
from contextlib import redirect_stdout, redirect_stderr


async def code_executor(code: str, language: str = "python") -> str:
    if language.lower() != "python":
        return f"Langage '{language}' non supporté. Seul Python est disponible."

    try:
        from ..config_tools import get_e2b_key
        e2b_key = get_e2b_key()
    except Exception:
        e2b_key = None

    if e2b_key:
        return await _run_e2b(code, e2b_key)
    return await _run_local_sandbox(code)


async def _run_e2b(code: str, api_key: str) -> str:
    try:
        from e2b_code_interpreter import AsyncSandbox
        async with AsyncSandbox(api_key=api_key) as sandbox:
            execution = await sandbox.run_code(code)
            output = "\n".join(str(r) for r in execution.results if r)
            if execution.error:
                output += f"\nERREUR: {execution.error.name}: {execution.error.value}"
            return output or "(pas de sortie)"
    except ImportError:
        return await _run_local_sandbox(code)
    except Exception as e:
        return f"Erreur E2B: {e}"


async def _run_local_sandbox(code: str) -> str:
    """Sandbox local basique — pas de réseau, pas de filesystem."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _exec_restricted, code)


def _exec_restricted(code: str) -> str:
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()

    # Namespace restreint
    safe_globals = {
        "__builtins__": {
            "print": print,
            "len": len, "range": range, "enumerate": enumerate,
            "zip": zip, "map": map, "filter": filter,
            "list": list, "dict": dict, "set": set, "tuple": tuple,
            "str": str, "int": int, "float": float, "bool": bool,
            "abs": abs, "round": round, "sum": sum, "min": min, "max": max,
            "sorted": sorted, "reversed": reversed,
            "isinstance": isinstance, "type": type,
            "True": True, "False": False, "None": None,
        }
    }

    output_lines = []

    def captured_print(*args, **kwargs):
        output_lines.append(" ".join(str(a) for a in args))

    safe_globals["__builtins__"]["print"] = captured_print

    try:
        exec(code, safe_globals)  # noqa: S102
        return "\n".join(output_lines) if output_lines else "(code exécuté sans sortie)"
    except Exception:
        tb = traceback.format_exc()
        return f"ERREUR:\n{tb}"
