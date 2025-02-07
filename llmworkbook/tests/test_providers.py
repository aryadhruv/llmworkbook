# pylint: skip-file
import pytest
from unittest.mock import AsyncMock, patch

from ..providers import call_llm_openai, call_llm_ollama, call_llm_gpt4all


class MockConfig:
    """Mock class to simulate the configuration object."""

    def __init__(self, api_key=None, system_prompt=None, options=None):
        self.api_key = api_key or "test-api-key"
        self.system_prompt = system_prompt
        self.options = options or {"model": "gpt-4o-mini", "temperature": 0.7}


@pytest.mark.asyncio
async def test_call_llm_openai():
    """Test OpenAI LLM call with mocked OpenAI response."""
    config = MockConfig()
    prompt = "Hello, world!"
    mock_response = AsyncMock()
    mock_response.choices = [AsyncMock()]
    mock_response.choices[0].message = AsyncMock()
    mock_response.choices[0].message.content = "Mocked response text"

    with patch(
        "openai.resources.chat.completions.Completions.create",
        return_value=mock_response,
    ) as mock_create:
        response = await call_llm_openai(config, prompt)
        # Assertions
        assert response == "Mocked response text"

    mock_create


@pytest.mark.asyncio
async def test_call_llm_openai_api_failure():
    """Test OpenAI LLM call when API returns an error (missing choices)."""
    config = MockConfig()
    prompt = "Hello, world!"
    mock_response = AsyncMock()
    mock_response.choices = []

    with patch(
        "openai.resources.chat.completions.Completions.create",
        return_value=mock_response,
    ) as mock_create:
        response = await call_llm_openai(config, prompt)

        assert response == str(mock_response)
        mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_call_llm_ollama():
    """Test Ollama LLM call with mocked aiohttp response."""
    config = MockConfig()
    prompt = "Tell me a joke."

    mock_response_json = {"response": "Mocked Ollama Response"}

    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = mock_response_json
        mock_session.__aenter__.return_value = mock_response
        mock_post.return_value = mock_session

        response = await call_llm_ollama(config, prompt)

    assert response == "Mocked Ollama Response"
    mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_call_llm_ollama_api_failure():
    """Test Ollama LLM call when API returns an error."""
    config = MockConfig()
    prompt = "Tell me a joke."

    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text.return_value = "Internal Server Error"
        mock_session.__aenter__.return_value = mock_response
        mock_post.return_value = mock_session

        response = await call_llm_ollama(config, prompt)

    assert response == "Error: 500, Internal Server Error"
    mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_call_llm_gpt4all():
    """Test GPT4ALL LLM call with mocked aiohttp response."""
    config = MockConfig()
    prompt = "Summarize this text."

    mock_response_json = {
        "choices": [{"message": {"content": "Mocked GPT4ALL Response"}}]
    }

    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = mock_response_json
        mock_session.__aenter__.return_value = mock_response
        mock_post.return_value = mock_session

        response = await call_llm_gpt4all(config, prompt)

    assert response == "Mocked GPT4ALL Response"
    mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_call_llm_gpt4all_api_failure():
    """Test GPT4ALL LLM call when API returns an error."""
    config = MockConfig()
    prompt = "Summarize this text."

    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.text.return_value = "Bad Request"
        mock_session.__aenter__.return_value = mock_response
        mock_post.return_value = mock_session

        response = await call_llm_gpt4all(config, prompt)

    assert response == "Error: 400, Bad Request"
    mock_post.assert_called_once()
