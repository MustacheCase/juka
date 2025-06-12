import pytest
import os
from unittest.mock import Mock

@pytest.fixture(autouse=True)
def mock_env_vars():
    """
    Mock environment variables for testing.
    This fixture runs automatically for all tests.
    """
    # Store original environment
    original_env = dict(os.environ)
    
    # Set test environment variables
    os.environ.update({
        'SPOTIFY_CLIENT_ID': 'test_spotify_client_id',
        'SPOTIFY_CLIENT_SECRET': 'test_spotify_client_secret',
        'GOOGLE_API_KEY': 'test_google_api_key',
        'TELEGRAM_BOT_TOKEN': 'test_telegram_bot_token',
        'TELEGRAM_CHANNEL_ID': 'test_telegram_channel_id'
    })
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)

@pytest.fixture
def mock_spotify_client():
    """
    Create a mock Spotify client for testing.
    """
    client = Mock()
    client.search.return_value = {
        'tracks': {
            'items': [{
                'name': 'Test Song',
                'artists': [{'name': 'Test Artist'}],
                'album': {'name': 'Test Album', 'release_date': '2024-01-01'},
                'external_urls': {'spotify': 'https://spotify.com/track/123'},
                'popularity': 80,
                'duration_ms': 180000
            }]
        }
    }
    return client

@pytest.fixture
def mock_genius_response():
    """
    Create a mock Genius API response for testing.
    """
    return {
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

@pytest.fixture
def mock_telegram_bot():
    """
    Create a mock Telegram bot for testing.
    """
    bot = Mock()
    bot.send_message = Mock()
    return bot 