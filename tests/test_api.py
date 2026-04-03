import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

@pytest.fixture
def client(tmp_path):
    import core.main as main_module
    main_module.DB_PATH = str(tmp_path / "test.db")
    from core.db import init_db
    init_db(main_module.DB_PATH)
    from core.main import app
    return TestClient(app)

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_message_endpoint_general_chat(client):
    mock_ai = AsyncMock(return_value={
        "intent": "general_chat",
        "data": {},
        "response": "Merhaba!",
    })
    with patch("core.main.chat", mock_ai):
        response = client.post("/message", json={"text": "merhaba"})
        assert response.status_code == 200
        assert "Merhaba" in response.json()["response"]

def test_message_endpoint_add_task(client):
    mock_ai = AsyncMock(return_value={
        "intent": "add_task",
        "data": {"title": "Test görevi", "priority": "normal"},
        "response": "Görev eklendi",
    })
    with patch("core.main.chat", mock_ai):
        response = client.post("/message", json={"text": "test görevi ekle"})
        assert response.status_code == 200
