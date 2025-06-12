import pytest
from unittest.mock import Mock, patch
from spotipy.exceptions import SpotifyException
from src.services.spotify_service import SpotifyService

@pytest.fixture
def mock_spotify_client():
    return Mock()

@pytest.fixture
def spotify_service(mock_spotify_client):
    return SpotifyService(mock_spotify_client)

def test_init_success(mock_spotify_client):
    # Mock successful search response
    mock_spotify_client.search.return_value = {'tracks': {'items': [{'name': 'test'}]}}
    
    service = SpotifyService(mock_spotify_client)
    assert service.sp == mock_spotify_client
    assert len(service.genres) > 0

def test_init_failure(mock_spotify_client):
    # Mock failed search response
    mock_spotify_client.search.side_effect = SpotifyException(http_status=403, msg="Invalid credentials", code=403)
    
    with pytest.raises(Exception) as exc_info:
        SpotifyService(mock_spotify_client)
    assert "Spotify API authentication failed" in str(exc_info.value)

def test_get_random_song_success(mock_spotify_client, spotify_service):
    # Mock successful search response
    mock_track = {
        'name': 'Test Song',
        'artists': [{'name': 'Test Artist'}],
        'album': {'name': 'Test Album', 'release_date': '2024-01-01'},
        'external_urls': {'spotify': 'https://spotify.com/track/123'},
        'popularity': 80,
        'duration_ms': 180000
    }
    mock_spotify_client.search.return_value = {'tracks': {'items': [mock_track]}}
    
    song = spotify_service.get_random_song()
    
    assert song['name'] == 'Test Song'
    assert song['artist'] == 'Test Artist'
    assert song['album'] == 'Test Album'
    assert song['spotify_url'] == 'https://spotify.com/track/123'
    assert song['popularity'] == 80
    assert song['duration_ms'] == 180000

def test_get_random_song_no_results(mock_spotify_client, spotify_service):
    # Mock empty search response
    mock_spotify_client.search.return_value = {'tracks': {'items': []}}
    
    with pytest.raises(Exception) as exc_info:
        spotify_service.get_random_song()
    assert "No tracks found" in str(exc_info.value)

def test_get_random_song_api_error(mock_spotify_client, spotify_service):
    # Mock API error
    mock_spotify_client.search.side_effect = SpotifyException(http_status=500, msg="Internal server error", code=500)
    
    with pytest.raises(Exception) as exc_info:
        spotify_service.get_random_song()
    assert "Internal server error" in str(exc_info.value)

def test_get_multiple_songs(spotify_service):
    # Mock get_random_song to return a test song
    test_song = {
        'name': 'Test Song',
        'artist': 'Test Artist',
        'album': 'Test Album',
        'release_date': '2024-01-01',
        'spotify_url': 'https://spotify.com/track/123',
        'popularity': 80,
        'duration_ms': 180000
    }
    
    with patch.object(spotify_service, 'get_random_song', return_value=test_song):
        songs = spotify_service.get_multiple_songs()
        assert len(songs) == 1
        assert songs[0] == test_song 