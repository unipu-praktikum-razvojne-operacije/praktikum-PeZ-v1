"""Minimal client for the local Ollama REST API (https://github.com/ollama/ollama/blob/main/docs/api.md)."""
import os

import requests
from dotenv import load_dotenv

load_dotenv()

DEFAULT_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5:0.5b"
TIMEOUT_SECONDS = 120


class OllamaError(RuntimeError):
    """Raised when Ollama is unreachable or returns an error."""


def get_base_url() -> str:
    return os.getenv("OLLAMA_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def get_model() -> str:
    return os.getenv("OLLAMA_MODEL", DEFAULT_MODEL)


def _request(method: str, path: str, **kwargs) -> requests.Response:
    url = f"{get_base_url()}{path}"
    try:
        response = requests.request(method, url, timeout=TIMEOUT_SECONDS, **kwargs)
    except requests.ConnectionError as error:
        raise OllamaError(f"Ollama is not reachable at {get_base_url()} (start it with: ollama serve)") from error
    if response.status_code != 200:
        raise OllamaError(f"Ollama returned HTTP {response.status_code}: {response.text}")
    return response


def is_running() -> bool:
    try:
        _request("GET", "/")
    except OllamaError:
        return False
    return True


def list_models() -> list[str]:
    data = _request("GET", "/api/tags").json()
    return [model["name"] for model in data.get("models", [])]


def generate(prompt: str, model: str | None = None) -> str:
    payload = {"model": model or get_model(), "prompt": prompt, "stream": False}
    return _request("POST", "/api/generate", json=payload).json()["response"]


def build_messages(question: str, system: str | None = None, history: list[dict] | None = None) -> list[dict]:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.extend(history or [])
    messages.append({"role": "user", "content": question})
    return messages


def chat(messages: list[dict], model: str | None = None) -> str:
    payload = {"model": model or get_model(), "messages": messages, "stream": False}
    return _request("POST", "/api/chat", json=payload).json()["message"]["content"]