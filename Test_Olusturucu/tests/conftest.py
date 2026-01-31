import pytest
import os
import tempfile
import sys
from unittest.mock import MagicMock

from src.db.init_db import init_db
from src.db.db_manager import DBManager

@pytest.fixture
def db_session():
    """Provides a fresh database session for each test using a temporary file."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    init_db(path)
    manager = DBManager(path)
    
    yield manager
    
    if os.path.exists(path):
        os.unlink(path)

@pytest.fixture
def mock_gemini_response():
    """Standard mocked response from Gemini."""
    return [
        {
            "page_index": 0,
            "text": "Mock Question Text 1",
            "coordinates": [100, 100, 200, 200]
        },
        {
            "page_index": 0,
            "text": "Mock Question Text 2",
            "coordinates": [300, 100, 400, 200]
        }
    ]

@pytest.fixture
def mock_gemini_service(mock_gemini_response):
    """Mocks the GeminiService class methods."""
    mock_service = MagicMock()
    mock_service.analyze_chunk.return_value = mock_gemini_response
    mock_service.analyze_page.return_value = mock_gemini_response
    return mock_service
