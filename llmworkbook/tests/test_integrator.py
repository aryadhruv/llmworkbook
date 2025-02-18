# pylint: skip-file
from llmworkbook import LLMConfig, LLMDataFrameIntegrator, LLMRunner
import pandas as pd
import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def sample_dataframe():
    """Fixture to create a sample DataFrame."""
    return pd.DataFrame(
        {
            "prompt_column": ["Hello, world!", "What is AI?", "", "Tell me a joke"],
            "other_column": [1, 2, 3, 4],
        }
    )

@pytest.fixture
def mock_config():
    """Fixture for creating an LLMConfig object."""
    return LLMConfig(
        provider="openai",
        api_key="test-api-key",
        system_prompt="Process these Data rows as per the provided prompt",
        options={
            "model_name": "gpt-4o-mini",
            "temperature": 1,
            "max_tokens": 1024,
        },
    )

@pytest.fixture
def mock_runner(mock_config):
    """Fixture to create a mock LLM runner."""
    mock = MagicMock(spec=LLMRunner(config=mock_config))
    mock.run_sync.side_effect = lambda x: f"Response to: {x}"
    mock.run = AsyncMock(side_effect=lambda x: f"Async response to: {x}")
    return mock


def test_add_llm_responses_sync(sample_dataframe, mock_runner):
    """Test synchronous LLM integration."""
    integrator = LLMDataFrameIntegrator(runner=mock_runner, df=sample_dataframe)

    updated_df = integrator.add_llm_responses(
        prompt_column="prompt_column", response_column="llm_response"
    )

    assert "llm_response" in updated_df.columns
    assert updated_df.loc[0, "llm_response"] == "Response to: Hello, world!"
    assert updated_df.loc[1, "llm_response"] == "Response to: What is AI?"
    assert pd.isna(
        updated_df.loc[2, "llm_response"]
    )  # Empty prompt should not have a response
    assert updated_df.loc[3, "llm_response"] == "Response to: Tell me a joke"

    # Verify the mock was called the expected number of times
    assert mock_runner.run_sync.call_count == 3


def test_add_llm_responses_async(sample_dataframe, mock_runner):
    """Test asynchronous LLM integration."""
    integrator = LLMDataFrameIntegrator(runner=mock_runner, df=sample_dataframe)

    updated_df = integrator.add_llm_responses(
        prompt_column="prompt_column", response_column="llm_response", async_mode=True
    )

    assert "llm_response" in updated_df.columns
    assert updated_df.loc[0, "llm_response"] == "Async response to: Hello, world!"
    assert updated_df.loc[1, "llm_response"] == "Async response to: What is AI?"
    assert pd.isna(
        updated_df.loc[2, "llm_response"]
    )  # Empty prompt should not have a response
    assert updated_df.loc[3, "llm_response"] == "Async response to: Tell me a joke"

    # Verify the async mock was called the expected number of times
    assert mock_runner.run.await_count == 3


def test_add_llm_responses_with_row_filter(sample_dataframe, mock_runner):
    """Test LLM responses with a subset of rows."""
    integrator = LLMDataFrameIntegrator(runner=mock_runner, df=sample_dataframe)

    updated_df = integrator.add_llm_responses(
        prompt_column="prompt_column", response_column="llm_response", row_filter=[0, 2]
    )

    assert "llm_response" in updated_df.columns
    assert updated_df.loc[0, "llm_response"] == "Response to: Hello, world!"
    assert pd.isna(updated_df.loc[1, "llm_response"])
    assert updated_df.loc[2, "llm_response"] is None  # Empty prompt should remain None
    assert pd.isna(updated_df.loc[3, "llm_response"])

    # Ensure only 2 calls were made
    assert mock_runner.run_sync.call_count == 1  # Only valid prompt processed


def test_reset_responses(sample_dataframe, mock_runner):
    """Test resetting response columns."""
    integrator = LLMDataFrameIntegrator(runner=mock_runner, df=sample_dataframe)
    integrator.df["llm_response"] = [
        "Some response",
        "Another response",
        None,
        "Last response",
    ]

    updated_df = integrator.reset_responses(response_column="llm_response")

    assert updated_df["llm_response"].isnull().all()


def test_add_llm_responses_creates_column_if_not_exist(sample_dataframe, mock_runner):
    """Test that a new response column is created if it does not exist."""
    integrator = LLMDataFrameIntegrator(runner=mock_runner, df=sample_dataframe)

    updated_df = integrator.add_llm_responses(
        prompt_column="prompt_column", response_column="new_response_column"
    )

    assert "new_response_column" in updated_df.columns
    assert updated_df.loc[0, "new_response_column"] == "Response to: Hello, world!"


def test_add_llm_responses_invalid_column(sample_dataframe, mock_runner):
    """Test handling when an invalid prompt column is provided."""
    integrator = LLMDataFrameIntegrator(runner=mock_runner, df=sample_dataframe)

    with pytest.raises(KeyError):
        integrator.add_llm_responses(prompt_column="non_existent_column")


def test_async_function(sample_dataframe, mock_runner):
    """Test the internal asynchronous processing of LLM responses."""
    integrator = LLMDataFrameIntegrator(runner=mock_runner, df=sample_dataframe)

    output_df = integrator.add_llm_responses(
        prompt_column="prompt_column", response_column="llm_response", async_mode=True
    )
    output_df
