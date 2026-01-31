import pytest
import os
from unittest.mock import MagicMock
from src.core.gemini_service import GeminiService

def test_gemini_init_warning(monkeypatch, capsys, mocker):
    """Test that a warning is printed if API key is missing."""
    # Ensure environment has no key
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    
    # Mock genai to prevent actual configure call error
    mock_genai = mocker.patch("src.core.gemini_service.genai")
    
    from src.core.gemini_service import GeminiService
    service = GeminiService()
    
    captured = capsys.readouterr()
    assert "Uyarı: GEMINI_API_KEY bulunamadı!" in captured.out

def test_analyze_chunk_parsing(mocker):
    """Test correct parsing of JSON response from Gemini."""
    # Mock the genai module
    mock_genai = mocker.patch("src.core.gemini_service.genai")
    
    # Setup Model Mock
    mock_model = MagicMock()
    mock_genai.GenerativeModel.return_value = mock_model
    
    # Setup Response Mock
    mock_response = MagicMock()
    # Simulate Markdown code block response
    mock_response.text = '''
    Other text
    ```json
    {
      "summary": {"total_questions_on_pages": 1},
      "questions": [
        {
          "page_index": 0,
          "text": "Tested Question",
          "coordinates": [0, 0, 100, 100]
        }
      ]
    }
    ```
    '''
    mock_model.generate_content.return_value = mock_response
    
    # Instantiate Service
    mocker.patch.dict(os.environ, {"GEMINI_API_KEY": "TEST_KEY"})
    service = GeminiService()
    
    # Call
    results = service.analyze_chunk(["dummy_path.png"])
    
    # Assert
    assert len(results) == 1
    assert results[0]["text"] == "Tested Question"
    assert results[0]["page_index"] == 0

def test_gemini_api_error_handling(mocker):
    """Test that API errors return empty list instead of crashing."""
    mock_genai = mocker.patch("src.core.gemini_service.genai")
    mock_model = MagicMock()
    mock_genai.GenerativeModel.return_value = mock_model
    
    # Make generate_content raise exception
    mock_model.generate_content.side_effect = Exception("Quota Exceeded")
    
    mocker.patch.dict(os.environ, {"GEMINI_API_KEY": "TEST_KEY"})
    service = GeminiService()
    
    results = service.analyze_chunk(["path"])
    assert results == []
