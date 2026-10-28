import pytest
import requests

import ollama_client


class FakeResponse:
    def __init__(self, data: dict, status_code: int = 200):
        self._data = data
        self.status_code = status_code
        self.text = str(data)

    def json(self) -> dict:
        return self._data


@pytest.fixture
def fake_request(monkeypatch):
    """Replaces requests.request and records every call it receives."""
    calls = []

    def install(response: FakeResponse | None = None, error: Exception | None = None):
        def fake(method, url, **kwargs):
            calls.append({"method": method, "url": url, **kwargs})
            if error:
                raise error
            return response

        monkeypatch.setattr(ollama_client.requests, "request", fake)
        return calls

    return install

#1
def test_build_messages_puts_system_prompt_first():
    messages = ollama_client.build_messages("What is git?", system="Answer briefly.")

    assert messages == [
        {"role": "system", "content": "Answer briefly."},
        {"role": "user", "content": "What is git?"},
    ]
#2
def test_list_models_returns_model_names(fake_request):
    lazod = {"models": [{"name": "llama3.2:1b"}, {"name": "qwen2.5:0.5b"}]}
    fake_request(FakeResponse(lazod))

    models = ollama_client.list_models()

    assert models == ["llama3.2:1b", "qwen2.5:0.5b"]
#3
def test_generate_sends_model_and_prompt_without_streaming(fake_request, monkeypatch):
    monkeypatch.setenv("OLLAMA_MODEL", "test-model")
    calls = fake_request(FakeResponse({"response": "Hello!"}))

    result = ollama_client.generate("Hi")

    assert result == "Hello!"
    assert len(calls) == 1
    assert calls[0]["json"] == {
        "model": "test-model",
        "prompt": "Hi",
        "stream": False,
    }
#4
def test_chat_returns_assistant_message_content(fake_request):
    mock_data = {"message": {"role": "assistant", "content": "Git is a VCS."}}
    fake_request(FakeResponse(mock_data))

    messages = [{"role": "user", "content": "What is git?"}]
    response = ollama_client.chat(messages)

    assert response == "Git is a VCS."
#5
def test_generate_raises_ollama_error_when_server_is_down(fake_request):
    fake_request(error=requests.ConnectionError("Connection refused"))

    with pytest.raises(ollama_client.OllamaError, match="not reachable"):
        ollama_client.generate("Hello")
#dot
@pytest.mark.skipif(not ollama_client.is_running(), reason="Ollama is not running")
def test_real_model_answers():
    assert ollama_client.generate("Reply with the single word: ok").strip() != ""