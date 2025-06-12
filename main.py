import os
import random
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from telegram import Bot
import schedule
import time
from dotenv import load_dotenv
import logging
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import Spotify
from src.utils.config import init_services, logger, Config
from src.services.spotify_service import SpotifyService
from src.services.telegram_service import TelegramService
from src.services.gemini_service import GeminiService
from src.services.genius_service import GeniusService
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure API keys
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Initialize Telegram bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

def get_random_song():
    """
    Get a random song from Spotify using their API.
    """
    try:
        # List of popular genres to choose from
        genres = [
            'rock', 'pop', 'hip-hop', 'jazz', 'classical',
            'electronic', 'folk', 'country', 'blues', 'metal'
        ]
        
        # Select a random genre
        genre = random.choice(genres)
        
        # Search for tracks in the selected genre
        results = sp.search(q=f'genre:{genre}', type='track', limit=50)
        
        if results['tracks']['items']:
            # Select a random track from the results
            track = random.choice(results['tracks']['items'])
            
            # Get track details
            track_name = track['name']
            artist_name = track['artists'][0]['name']
            album_name = track['album']['name']
            release_date = track['album']['release_date']
            spotify_url = track['external_urls']['spotify']
            
            # Get additional track features
            track_id = track['id']
            features = sp.audio_features(track_id)[0]
            
            # Format the song information
            song_info = {
                'name': track_name,
                'artist': artist_name,
                'album': album_name,
                'release_date': release_date,
                'spotify_url': spotify_url,
                'popularity': track['popularity'],
                'duration_ms': track['duration_ms'],
                'features': features
            }
            
            return song_info
            
    except Exception as e:
        logger.error(f"Error fetching song from Spotify: {e}")
        # Fallback to a default song if Spotify API fails
        return {
            'name': 'Bohemian Rhapsody',
            'artist': 'Queen',
            'album': 'A Night at the Opera',
            'release_date': '1975-10-31',
            'spotify_url': 'https://open.spotify.com/track/6l8GvAyoUZwWDgF1e4822w',
            'popularity': 100,
            'duration_ms': 354000,
            'features': {}
        }

def get_song_info(song_info):
    """
    Fetch information about the song and artist from Wikipedia.
    """
    try:
        # Search Wikipedia for the artist
        artist = song_info['artist']
        search_url = f"https://en.wikipedia.org/wiki/{artist.replace(' ', '_')}"
        response = requests.get(search_url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get the first paragraph of the article
            content = soup.find('div', {'class': 'mw-parser-output'})
            if content:
                paragraphs = content.find_all('p')
                for p in paragraphs:
                    if p.text.strip():
                        return p.text.strip()
        
        return f"Could not find detailed information about {artist}."
    except Exception as e:
        logger.error(f"Error fetching song info: {e}")
        return f"Error fetching information about {song_info['name']} by {song_info['artist']}."

def summarize_info(song_info, wiki_info):
    """
    Use Gemini to summarize the information about the song and artist.
    """
    try:
        # Format song features for the prompt
        features_text = ""
        if song_info['features']:
            features_text = f"""
            Song Features:
            - Danceability: {song_info['features'].get('danceability', 'N/A')}
            - Energy: {song_info['features'].get('energy', 'N/A')}
            - Tempo: {song_info['features'].get('tempo', 'N/A')} BPM
            - Key: {song_info['features'].get('key', 'N/A')}
            - Mode: {song_info['features'].get('mode', 'N/A')}
            """
        
        prompt = f"""
        Please provide a concise and interesting summary about this song and artist:
        
        Song: {song_info['name']}
        Artist: {song_info['artist']}
        Album: {song_info['album']}
        Release Date: {song_info['release_date']}
        {features_text}
        
        Wikipedia Information: {wiki_info}
        
        Include:
        1. A brief background about the artist
        2. The song's significance or impact
        3. Any interesting facts or trivia
        4. The song's musical characteristics
        
        Keep it engaging and suitable for a daily music post.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return f"Error generating summary for {song_info['name']}."

def send_to_telegram(message, spotify_url):
    """
    Send the message to the Telegram channel.
    """
    try:
        # Add Spotify link to the message
        message += f"\n\n🎧 <a href='{spotify_url}'>Listen on Spotify</a>"
        
        bot.send_message(
            chat_id=TELEGRAM_CHANNEL_ID,
            text=message,
            parse_mode='HTML',
            disable_web_page_preview=False
        )
        logger.info("Message sent successfully to Telegram")
    except Exception as e:
        logger.error(f"Error sending message to Telegram: {e}")

def process_song(services: dict, song: dict) -> bool:
    """
    Process a single song: get info from Genius, generate summary, and send to Telegram.
    Returns True if successful, False if no info found.
    """
    try:
        # Get song info from Genius
        genius_info = services['genius'].get_song_info(song['name'], song['artist'])
        if not genius_info:
            logger.warning(f"No Genius info found for {song['name']} by {song['artist']}")
            return False
            
        # Generate summary using Gemini
        summary = services['gemini'].summarize_info(song, genius_info)
        
        # Send to Telegram
        services['telegram'].send_song_info(song, genius_info, summary)
        return True
        
    except Exception as e:
        logger.error(f"Error processing song: {e}")
        return False

def daily_song_task(services: dict):
    """
    Main task that runs daily to get a random song and send it to Telegram.
    """
    try:
        # Get multiple songs from Spotify
        songs = services['spotify'].get_multiple_songs()
        
        # Try each song until we find one with Genius info
        for song in songs:
            if process_song(services, song):
                return
                
        # If we get here, no songs had Genius info
        error_msg = "Failed to find information for any songs after multiple attempts."
        logger.error(error_msg)
        services['telegram'].send_error_message(error_msg)
        
    except Exception as e:
        logger.error(f"Critical error: {e}")
        sys.exit(1)

def main():
    # Initialize services
    config = Config()

    # Create Spotipy client
    sp_auth = SpotifyClientCredentials(
        client_id=config.get('SPOTIFY_CLIENT_ID'),
        client_secret=config.get('SPOTIFY_CLIENT_SECRET')
    )
    sp_client = Spotify(auth_manager=sp_auth)

    services = {
        'spotify': SpotifyService(sp_client),
        'genius': GeniusService(
            access_token=config.get('GENIUS_ACCESS_TOKEN')
        ),
        'gemini': GeminiService(
            api_key=config.get('GOOGLE_API_KEY')
        ),
        'telegram': TelegramService(
            bot_token=config.get('TELEGRAM_BOT_TOKEN'),
            channel_id=config.get('TELEGRAM_CHANNEL_ID')
        )
    }
    
    # Run the task immediately on startup
    daily_song_task(services)
    
    # Exit after running the task
    sys.exit(0)

if __name__ == "__main__":
    main() 