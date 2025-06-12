import pytest
from unittest.mock import Mock, patch
from src.services.gemini_service import GeminiService

@pytest.fixture
def gemini_service():
    return GeminiService(api_key="test_api_key")

def test_init(gemini_service):
    assert gemini_service.model is not None

def test_summarize_info_success(gemini_service):
    # Mock song and genius info
    song = {
        'name': 'Test Song',
        'artist': 'Test Artist'
    }
    genius_info = {
        'album': 'Test Album',
        'release_date': '2024-01-01',
        'description': 'A test song description'
    }
    
    # Mock the model's generate_content method
    mock_response = Mock()
    mock_response.text = "This is a test summary"
    gemini_service.model.generate_content = Mock(return_value=mock_response)
    
    summary = gemini_service.summarize_info(song, genius_info)
    
    assert summary == "This is a test summary"
    # Verify the model was called with a prompt containing our test data
    call_args = gemini_service.model.generate_content.call_args[0][0]
    assert song['name'] in call_args
    assert song['artist'] in call_args
    assert genius_info['album'] in call_args
    assert genius_info['description'] in call_args

def test_summarize_info_error(gemini_service):
    # Mock song and genius info
    song = {
        'name': 'Test Song',
        'artist': 'Test Artist'
    }
    genius_info = {
        'album': 'Test Album',
        'release_date': '2024-01-01',
        'description': 'A test song description'
    }
    
    # Mock the model's generate_content method to raise an exception
    gemini_service.model.generate_content = Mock(side_effect=Exception("API Error"))
    
    with pytest.raises(Exception) as exc_info:
        gemini_service.summarize_info(song, genius_info)
    assert "API Error" in str(exc_info.value)

def test_summarize_info_missing_data(gemini_service):
    # Test with minimal data
    song = {
        'name': 'Test Song',
        'artist': 'Test Artist'
    }
    genius_info = {}
    
    # Mock the model's generate_content method
    mock_response = Mock()
    mock_response.text = "This is a test summary"
    gemini_service.model.generate_content = Mock(return_value=mock_response)
    
    summary = gemini_service.summarize_info(song, genius_info)
    
    assert summary == "This is a test summary"
    # Verify the model was called with a prompt containing our test data
    call_args = gemini_service.model.generate_content.call_args[0][0]
    assert song['name'] in call_args
    assert song['artist'] in call_args
    assert "Unknown" in call_args  # For missing album
    assert "No description available" in call_args  # For missing description 