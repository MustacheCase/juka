import pytest
from unittest.mock import Mock, patch
import requests
from src.services.genius_service import GeniusService

@pytest.fixture
def genius_service():
    return GeniusService(access_token="test_token")

def test_init(genius_service):
    assert genius_service.access_token == "test_token"
    assert genius_service.base_url == "https://api.genius.com"
    assert "Authorization" in genius_service.headers
    assert "User-Agent" in genius_service.headers

@patch('requests.get')
def test_get_song_info_success(mock_get, genius_service):
    # Mock successful API responses
    mock_search_response = Mock()
    mock_search_response.json.return_value = {
        "response": {
            "hits": [{
                "result": {
                    "id": 123,
                    "title": "Test Song",
                    "primary_artist": {"name": "Test Artist"},
                    "url": "https://genius.com/song/123"
                }
            }]
        }
    }
    mock_search_response.raise_for_status = Mock()
    
    mock_song_response = Mock()
    mock_song_response.json.return_value = {
        "response": {
            "song": {
                "title": "Test Song",
                "primary_artist": {"name": "Test Artist"},
                "album": {"name": "Test Album"},
                "release_date_for_display": "2024-01-01",
                "url": "https://genius.com/song/123",
                "description": {"plain": "Test description"},
                "producer_artists": [{"name": "Producer 1"}],
                "writer_artists": [{"name": "Writer 1"}],
                "featured_artists": [{"name": "Featured 1"}],
                "genres": [{"name": "Rock"}],
                "tags": [{"name": "Classic"}]
            }
        }
    }
    mock_song_response.raise_for_status = Mock()
    
    # Set up the mock to return different responses for different URLs
    def mock_get_side_effect(*args, **kwargs):
        if "search" in args[0]:
            return mock_search_response
        return mock_song_response
    
    mock_get.side_effect = mock_get_side_effect
    
    # Test getting song info
    result = genius_service.get_song_info("Test Song", "Test Artist")
    
    assert result is not None
    assert result["title"] == "Test Song"
    assert result["artist"] == "Test Artist"
    assert result["album"] == "Test Album"
    assert result["release_date"] == "2024-01-01"
    assert result["genius_url"] == "https://genius.com/song/123"
    assert result["description"] == "Test description"
    assert "Producer 1" in result["producer_artists"]
    assert "Writer 1" in result["writer_artists"]
    assert "Featured 1" in result["featured_artists"]
    assert "Rock" in result["genres"]
    assert "Classic" in result["tags"]

@patch('requests.get')
def test_get_song_info_no_results(mock_get, genius_service):
    # Mock empty search response
    mock_response = Mock()
    mock_response.json.return_value = {"response": {"hits": []}}
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response
    
    # Test getting song info for non-existent song
    result = genius_service.get_song_info("Non Existent Song", "Unknown Artist")
    
    assert result is None

@patch('requests.get')
def test_get_song_info_api_error(mock_get, genius_service):
    # Mock API error
    mock_get.side_effect = requests.exceptions.RequestException("API Error")
    
    # Test getting song info with API error
    result = genius_service.get_song_info("Test Song", "Test Artist")
    
    assert result is None

def test_format_info(genius_service):
    # Test data
    info = {
        "title": "Test Song",
        "artist": "Test Artist",
        "album": "Test Album",
        "release_date": "2024-01-01",
        "genius_url": "https://genius.com/song/123",
        "description": "Test description",
        "producer_artists": ["Producer 1"],
        "writer_artists": ["Writer 1"],
        "featured_artists": ["Featured 1"],
        "genres": ["Rock"],
        "tags": ["Classic"]
    }
    
    # Test formatting info
    formatted = genius_service.format_info(info)
    
    # Verify all information is included in the formatted string
    assert info["title"] in formatted
    assert info["artist"] in formatted
    assert info["album"] in formatted
    assert info["release_date"] in formatted
    assert info["genius_url"] in formatted
    assert info["description"] in formatted
    assert "Producer 1" in formatted
    assert "Writer 1" in formatted
    assert "Featured 1" in formatted
    assert "Rock" in formatted
    assert "Classic" in formatted

def test_format_info_empty(genius_service):
    # Test formatting empty info
    formatted = genius_service.format_info(None)
    
    assert formatted == "No information found on Genius." 