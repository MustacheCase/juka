import pytest
from unittest.mock import Mock, patch, AsyncMock
from telegram.error import TelegramError
from src.services.telegram_service import TelegramService

@pytest.fixture
def telegram_service():
    return TelegramService(bot_token="test_token", channel_id="test_channel")

@pytest.mark.asyncio
async def test_send_message_success(telegram_service):
    # Create a new mock bot with async send_message
    mock_bot = AsyncMock()
    telegram_service.bot = mock_bot
    
    # Test sending a message
    await telegram_service._send_message("Test message")
    
    # Verify the bot was called with correct parameters
    mock_bot.send_message.assert_called_once_with(
        chat_id="test_channel",
        text="Test message",
        parse_mode='HTML'
    )

@pytest.mark.asyncio
async def test_send_message_error(telegram_service):
    # Create a new mock bot with async send_message
    mock_bot = AsyncMock()
    mock_bot.send_message.side_effect = TelegramError("API Error")
    telegram_service.bot = mock_bot
    
    # Test sending a message that will fail
    with pytest.raises(TelegramError) as exc_info:
        await telegram_service._send_message("Test message")
    assert "API Error" in str(exc_info.value)

def test_send_error_message(telegram_service):
    # Mock the send_message method
    telegram_service.send_message = Mock()
    
    # Test sending an error message
    telegram_service.send_error_message("Test error")
    
    # Verify send_message was called with formatted error message
    telegram_service.send_message.assert_called_once_with(
        "❌ Error in Daily Song Bot:\n\nTest error"
    )

def test_send_song_info(telegram_service):
    # Mock the send_message method
    telegram_service.send_message = Mock()
    
    # Test data
    song = {
        'name': 'Test Song',
        'artist': 'Test Artist',
        'spotify_url': 'https://spotify.com/track/123'
    }
    genius_info = {
        'description': 'Test description',
        'genius_url': 'https://genius.com/song/123'
    }
    summary = "Test summary"
    
    # Test sending song info
    telegram_service.send_song_info(song, genius_info, summary)
    
    # Verify send_message was called with formatted message
    call_args = telegram_service.send_message.call_args[0][0]
    assert song['name'] in call_args
    assert song['artist'] in call_args
    assert genius_info['description'] in call_args
    assert summary in call_args
    assert song['spotify_url'] in call_args
    assert genius_info['genius_url'] in call_args

def test_send_song_info_missing_data(telegram_service):
    # Mock the send_message method
    telegram_service.send_message = Mock()
    
    # Test with minimal data
    song = {
        'name': 'Test Song',
        'artist': 'Test Artist'
    }
    genius_info = {}
    summary = "Test summary"
    
    # Test sending song info with missing data
    telegram_service.send_song_info(song, genius_info, summary)
    
    # Verify send_message was called with formatted message
    call_args = telegram_service.send_message.call_args[0][0]
    assert song['name'] in call_args
    assert song['artist'] in call_args
    assert summary in call_args
    # Verify empty strings for missing URLs
    assert 'href=""' in call_args 