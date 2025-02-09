# pylint: skip-file
import subprocess
import pytest
import os
from ..cli.cli import show_version


@pytest.fixture
def sample_csv(tmp_path):
    """Create a temporary sample CSV file for testing."""
    csv_path = tmp_path / "sample.csv"
    with open(csv_path, "w") as f:
        f.write("prompt,Reviews,Language\n")
        f.write("Summarize this,Great product,en\n")
        f.write("Translate this,Muy bueno,es\n")
    return str(csv_path)


@pytest.fixture
def sample_json(tmp_path):
    """Create a temporary sample JSON file for testing."""
    json_path = tmp_path / "sample.json"
    with open(json_path, "w") as f:
        f.write(
            '[["Summarize this", "Great product", "en"], ["Translate this", "Muy bueno", "es"]]'
        )
    return str(json_path)


@pytest.fixture
def sample_prompts(tmp_path):
    """Create a temporary text file with prompts."""
    txt_path = tmp_path / "prompts.txt"
    with open(txt_path, "w") as f:
        f.write("Summarize this\n")
        f.write("Translate this\n")
    return str(txt_path)


def test_cli_wrap_dataframe(sample_csv, tmp_path):
    """Test wrapping a DataFrame from CSV input using the CLI."""
    output_path = tmp_path / "wrapped_output.csv"
    result = subprocess.run(
        [
            "llmworkbook",
            "wrap_dataframe",
            sample_csv,
            str(output_path),
            "prompt",
            "Reviews,Language",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "✅ Wrapped DataFrame saved" in result.stdout
    assert os.path.exists(output_path)


def test_cli_wrap_array(sample_json, tmp_path):
    """Test wrapping a 2D array from JSON input using the CLI."""
    output_path = tmp_path / "wrapped_array.csv"
    result = subprocess.run(
        ["llmworkbook", "wrap_array", sample_json, str(output_path), "0", "1,2"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "✅ Wrapped Array saved" in result.stdout
    assert os.path.exists(output_path)


def test_cli_wrap_prompts(sample_prompts, tmp_path):
    """Test wrapping a list of prompts from a text file using the CLI."""
    output_path = tmp_path / "wrapped_prompts.csv"
    result = subprocess.run(
        ["llmworkbook", "wrap_prompts", sample_prompts, str(output_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "✅ Wrapped Prompts saved" in result.stdout
    assert os.path.exists(output_path)


def test_cli_llm_connection(mocker):
    """Test the LLM connection check via the CLI."""

    result = subprocess.run(
        ["llmworkbook", "test", "fake_api_key"], capture_output=True, text=True
    )

    assert result.returncode == 0
    assert (
        "✅ LLM Connection Successful!" in result.stdout
        or "❌ LLM Connection Failed!" in result.stdout
    )


def test_cli_version():
    """Test CLI version command."""
    result = subprocess.run(["llmworkbook", "version"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "LLMWORKBOOK version: %s", show_version() in result.stdout


def test_cli_help():
    """Test CLI help command."""
    result = subprocess.run(["llmworkbook", "--help"], capture_output=True, text=True)

    assert result.returncode == 0
    assert "CLI for wrapping data and testing LLM connectivity." in result.stdout
