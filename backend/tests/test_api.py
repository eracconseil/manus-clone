"""Tests de l'API FastAPI."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock


@pytest.fixture
def client():
    from backend.main import app
    return TestClient(app)


def test_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_agent_run_sse(client):
    """Vérifie que l'endpoint SSE retourne les bons event types."""
    async def mock_run(session_id, message, **kwargs):
        from backend.agent.core import AgentEvent
        yield AgentEvent("routing", {"model": "qwen", "complexity": "simple", "session_id": session_id})
        yield AgentEvent("response", {"content": "Bonjour !", "model": "qwen"})
        yield AgentEvent("done", {"session_id": session_id})

    with patch("backend.api.routes._agent") as mock_agent, \
         patch("backend.api.routes.usage_svc") as mock_usage:
        mock_agent.run = mock_run
        mock_usage.save_session = AsyncMock()
        mock_usage.save_message = AsyncMock()
        mock_usage.save_task_run = AsyncMock()

        res = client.post(
            "/api/agent/run",
            json={"session_id": "test-session", "message": "Dis bonjour"},
            headers={"Accept": "text/event-stream"},
        )
        assert res.status_code == 200
        content = res.text
        assert "routing" in content
        assert "response" in content
        assert "done" in content


def test_billing_profile_dev_mode(client):
    """En mode dev (sans token), retourne un profil par défaut."""
    with patch("backend.api.billing.get_profile", new_callable=AsyncMock, return_value=None):
        res = client.get("/api/billing/profile")
    assert res.status_code == 200
    data = res.json()
    assert data["plan"] == "free"
    assert data["tasks_used"] == 0
    assert data["tasks_limit"] == 10
