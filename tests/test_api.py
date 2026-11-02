
import os

# Configure API key before importing the application.
os.environ["API_KEY"] = "test-api-key"

import pytest
from unittest.mock import patch

from fastapi.testclient import TestClient
from main import app


API_KEY = "test-api-key"

client = TestClient(app)


@pytest.fixture(autouse=True)
def configure_api_key(monkeypatch):
    monkeypatch.setattr("main.API_KEY", API_KEY)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_chat_without_api_key():
    response = client.post(
        "/chat",
        json={"question": "What is Python?"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "API key is required"


def test_chat_with_invalid_api_key():
    response = client.post(
        "/chat",
        headers={"X-API-Key": "wrong-key"},
        json={"question": "What is Python?"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid API key"


def test_chat_with_empty_question():
    response = client.post(
        "/chat",
        headers={"X-API-Key": API_KEY},
        json={"question": ""}
    )

    assert response.status_code == 422


def test_chat_with_long_question():
    response = client.post(
        "/chat",
        headers={"X-API-Key": API_KEY},
        json={"question": "A" * 2001}
    )

    assert response.status_code == 422


@patch("main.requests.post")
def test_successful_chat(mock_post):

    mock_post.return_value.json.return_value = {
        "response": "Python is a programming language."
    }

    mock_post.return_value.raise_for_status.return_value = None

    response = client.post(
        "/chat",
        headers={"X-API-Key": API_KEY},
        json={"question": "What is Python?"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["model"] == "qwen2.5:0.5b"
    assert data["answer"] == "Python is a programming language."

    mock_post.assert_called_once()


@patch("main.requests.post")
def test_ollama_connection_error(mock_post):

    import requests

    mock_post.side_effect = requests.exceptions.ConnectionError()

    response = client.post(
        "/chat",
        headers={"X-API-Key": API_KEY},
        json={"question": "Test"}
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "Ollama server is unavailable"


@patch("main.requests.post")
def test_ollama_timeout(mock_post):

    import requests

    mock_post.side_effect = requests.exceptions.Timeout()

    response = client.post(
        "/chat",
        headers={"X-API-Key": API_KEY},
        json={"question": "Test"}
    )

    assert response.status_code == 504
    assert response.json()["detail"] == "LLM response timed out"


@patch("main.requests.post")
def test_ollama_invalid_response(mock_post):

    mock_post.return_value.raise_for_status.return_value = None
    mock_post.return_value.json.return_value = {}

    response = client.post(
        "/chat",
        headers={"X-API-Key": API_KEY},
        json={"question": "Test"}
    )

    assert response.status_code == 502
    assert response.json()["detail"] == (
        "LLM server returned an invalid or failed response"
    )
