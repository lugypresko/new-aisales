import pytest
import json
import os
from pathlib import Path
from src.utils.logger import SalesLogger
from src.cognitive.intent_classifier import IntentClassifier
from src.cognitive.rag_engine import RAGEngine
from src.cognitive.controller import Controller

# --- Paths ---
TEST_DIR = Path(__file__).parent
FIXTURES_DIR = TEST_DIR / "fixtures"
CONFIG_PATH = FIXTURES_DIR / "json" / "config.json"
LOG_PATH = TEST_DIR / "logs" / "test_interactions.jsonl"

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Ensure test directories exist."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if LOG_PATH.exists():
        os.remove(LOG_PATH)  # Clean start
    yield

@pytest.fixture
def mock_config_path():
    """Return path to test config."""
    return str(CONFIG_PATH)

@pytest.fixture
def test_logger(mock_config_path):
    """Return a logger instance configured for testing."""
    return SalesLogger(mock_config_path)

@pytest.fixture
def intent_classifier(mock_config_path):
    """Return an IntentClassifier instance."""
    return IntentClassifier(mock_config_path)

@pytest.fixture
def rag_engine(mock_config_path):
    """Return a RAGEngine instance."""
    return RAGEngine(mock_config_path)

@pytest.fixture
def controller(mock_config_path):
    """Return a Controller instance."""
    return Controller(mock_config_path)
