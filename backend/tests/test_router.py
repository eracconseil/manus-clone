"""Tests du router multi-modèles."""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from backend.models.schemas import TaskComplexity


@pytest.mark.asyncio
async def test_route_simple():
    with patch("backend.agent.router._qwen") as mock_qwen:
        mock_qwen.complete = AsyncMock(return_value=type("R", (), {"content": "SIMPLE"})())
        from backend.agent.router import route_task
        result = await route_task("Résume ce texte court")
        assert result == TaskComplexity.SIMPLE


@pytest.mark.asyncio
async def test_route_long_context_by_length():
    from backend.agent.router import route_task
    # context_length > 8000 → LONG_CONTEXT sans appel LLM
    result = await route_task("n'importe quoi", context_length=9000)
    assert result == TaskComplexity.LONG_CONTEXT


@pytest.mark.asyncio
async def test_route_complex():
    with patch("backend.agent.router._qwen") as mock_qwen:
        mock_qwen.complete = AsyncMock(return_value=type("R", (), {"content": "COMPLEX"})())
        from backend.agent.router import route_task
        result = await route_task("Crée un plan détaillé multi-étapes avec recherche web")
        assert result == TaskComplexity.COMPLEX


@pytest.mark.asyncio
async def test_route_fallback_to_complex():
    """Un label inconnu retourne COMPLEX par sécurité."""
    with patch("backend.agent.router._qwen") as mock_qwen:
        mock_qwen.complete = AsyncMock(return_value=type("R", (), {"content": "UNKNOWN_LABEL"})())
        from backend.agent.router import route_task
        result = await route_task("quelque chose")
        assert result == TaskComplexity.COMPLEX
