import json
import pytest
from unittest.mock import AsyncMock, patch
from core.ai import build_system_prompt, parse_ai_response, chat

def test_build_system_prompt_contains_turkish_instructions():
    context = {"tasks": [], "habits": [], "events": []}
    prompt = build_system_prompt(context)
    assert "Türkçe" in prompt
    assert "intent" in prompt
    assert "JSON" in prompt

def test_build_system_prompt_includes_context_data():
    context = {
        "tasks": [{"id": 1, "title": "Test görevi", "status": "bekliyor"}],
        "habits": [],
        "events": [],
    }
    prompt = build_system_prompt(context)
    assert "Test görevi" in prompt

def test_parse_ai_response_valid_json():
    raw = '{"intent": "add_task", "data": {"title": "Test"}, "response": "Eklendi"}'
    result = parse_ai_response(raw)
    assert result["intent"] == "add_task"
    assert result["data"]["title"] == "Test"
    assert result["response"] == "Eklendi"

def test_parse_ai_response_extracts_json_from_text():
    raw = 'Some text before {"intent": "general_chat", "data": {}, "response": "Merhaba!"} some after'
    result = parse_ai_response(raw)
    assert result["intent"] == "general_chat"

def test_parse_ai_response_fallback_on_invalid():
    raw = "Bu düz bir metin yanıtı"
    result = parse_ai_response(raw)
    assert result["intent"] == "general_chat"
    assert result["response"] == raw

@pytest.mark.asyncio
async def test_chat_sends_request_to_ollama():
    mock_response = AsyncMock()
    mock_response.json = lambda: {
        "message": {
            "content": '{"intent": "general_chat", "data": {}, "response": "Merhaba!"}'
        }
    }
    mock_response.raise_for_status = lambda: None

    with patch("core.ai.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = await chat("merhaba", [], {})
        assert result["intent"] == "general_chat"
