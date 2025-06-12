import logging
import asyncio
from telegram import Bot
from telegram.error import TelegramError
from typing import Dict
from src.utils.config import TELEGRAM_CHANNEL_ID

logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self, bot_token: str, channel_id: str):
        """
        Initialize the Telegram service with bot token and channel ID.
        """
        self.bot = Bot(token=bot_token)
        self.channel_id = channel_id
        
    async def _send_message(self, text: str) -> None:
        """
        Send a message to the Telegram channel.
        """
        try:
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=text,
                parse_mode='HTML'
            )
            logger.info("Message sent successfully to Telegram")
        except TelegramError as e:
            logger.error(f"Error sending message to Telegram: {e}")
            raise
            
    def send_message(self, text: str) -> None:
        """
        Send a message to the Telegram channel synchronously.
        """
        asyncio.run(self._send_message(text))
        
    def send_error_message(self, error_message: str) -> None:
        """
        Send an error message to the Telegram channel.
        """
        message = f"❌ Error in Daily Song Bot:\n\n{error_message}"
        self.send_message(message)
        
    def send_song_info(self, song: Dict, genius_info: Dict, summary: str) -> None:
        """
        Send song information to the Telegram channel.
        """
        # Format the message with song info and summary
        message = f"""🎵 <b>Today's Song</b>

<b>{song['name']}</b> by <b>{song['artist']}</b>

{genius_info.get('description', '')}

{summary}

🔗 <a href="{genius_info.get('genius_url', '')}">View on Genius</a>
🎧 <a href="{song.get('spotify_url', '')}">Listen on Spotify</a>"""

        self.send_message(message) 