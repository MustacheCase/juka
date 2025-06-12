# One Song Each Day Bot

A Telegram bot that posts a random song each day with information about the song and artist.

## Features

- Posts a random song each day at 9:00 AM
- Fetches songs from Spotify's API
- Fetches detailed information about the song and artist from Genius
- Generates a summary using Google's Gemini AI
- Posts the song and information to a Telegram channel

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with the following variables:
   ```
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   GENIUS_ACCESS_TOKEN=your_genius_access_token
   GOOGLE_API_KEY=your_google_api_key
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TELEGRAM_CHANNEL_ID=your_telegram_channel_id
   ```
4. Run the bot:
   ```
   python main.py
   ```

## API Keys Required

- Spotify API credentials (Client ID and Client Secret)
- Genius API access token
- Google API key for Gemini
- Telegram Bot Token
- Telegram Channel ID

## How it Works

1. The bot fetches a random song from Spotify's API
2. It then fetches detailed information about the song and artist from Genius
3. The information is summarized using Google's Gemini AI
4. The song and information are posted to the specified Telegram channel

## Project Structure

```
.
├── main.py                 # Main script
├── requirements.txt        # Python dependencies
└── src/
    ├── services/          # Service classes
    │   ├── spotify_service.py
    │   ├── genius_service.py
    │   ├── gemini_service.py
    │   └── telegram_service.py
    └── utils/             # Utility functions
        └── config.py      # Configuration utilities
```

## Contributing

Feel free to submit issues and enhancement requests! 