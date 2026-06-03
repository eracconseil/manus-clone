"""Tests des outils agent."""
import pytest
import asyncio


@pytest.mark.asyncio
async def test_code_executor_simple():
    from backend.agent.tools.code_executor import code_executor
    result = await code_executor("print(2 + 2)")
    assert "4" in result


@pytest.mark.asyncio
async def test_code_executor_error():
    from backend.agent.tools.code_executor import code_executor
    result = await code_executor("raise ValueError('test error')")
    assert "ERREUR" in result or "ValueError" in result


@pytest.mark.asyncio
async def test_file_write_read(tmp_path, monkeypatch):
    from backend.agent.tools import file_manager
    monkeypatch.setattr(file_manager, "_WORKSPACE", tmp_path)

    result = await file_manager.file_write("test.txt", "hello world")
    assert "test.txt" in result

    content = await file_manager.file_read("test.txt")
    assert content == "hello world"


@pytest.mark.asyncio
async def test_file_path_traversal(tmp_path, monkeypatch):
    from backend.agent.tools import file_manager
    monkeypatch.setattr(file_manager, "_WORKSPACE", tmp_path)

    result = await file_manager.file_read("../../etc/passwd")
    assert "refusé" in result.lower() or "Accès" in result


@pytest.mark.asyncio
async def test_file_list(tmp_path, monkeypatch):
    from backend.agent.tools import file_manager
    monkeypatch.setattr(file_manager, "_WORKSPACE", tmp_path)

    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")

    result = await file_manager.file_list()
    assert "a.txt" in result
    assert "b.txt" in result


@pytest.mark.asyncio
async def test_web_search_no_key():
    """Sans clé Brave, retourne le message de fallback."""
    from backend.agent.tools.web_search import web_search
    with __import__("unittest.mock", fromlist=["patch"]).patch(
        "backend.agent.tools.web_search.get_brave_key", return_value=""
    ):
        result = await web_search("python tutorial")
        assert "Brave" in result or "manquante" in result


@pytest.mark.asyncio
async def test_browser_invalid_url():
    from backend.agent.tools.browser import browser_navigate
    result = await browser_navigate("not-a-url")
    assert "invalide" in result.lower()
