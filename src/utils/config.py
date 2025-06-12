import os
import logging
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import google.generativeai as genai
from telegram import Bot

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Config:
    """
    Configuration class to handle environment variables.
    """
    def __init__(self):
        """
        Initialize configuration by loading environment variables.
        """
        load_dotenv()
        
    def get(self, key: str, default: str = None) -> str:
        """
        Get an environment variable.
        
        Args:
            key: The environment variable name
            default: Default value if the variable is not found
            
        Returns:
            The environment variable value or default if not found
            
        Raises:
            ValueError: If the variable is not found and no default is provided
        """
        value = os.getenv(key)
        if value is None and default is None:
            raise ValueError(f"Required environment variable {key} not found")
        return value if value is not None else default

# Environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

def init_services():
    """
    Initialize all required services with proper error handling.
    """
    services = {}
    
    # Initialize Spotify client
    try:
        if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
            raise ValueError("Spotify credentials not found in environment variables")
            
        auth_manager = SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET
        )
        sp = Spotify(auth_manager=auth_manager)
        services['spotify'] = sp
        logger.info("Spotify client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Spotify client: {e}")
        raise
    
    # Initialize Gemini
    try:
        if not GOOGLE_API_KEY:
            raise ValueError("Google API key not found in environment variables")
            
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        services['gemini'] = model
        logger.info("Gemini model initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini model: {e}")
        raise
    
    # Initialize Telegram bot
    try:
        if not TELEGRAM_BOT_TOKEN:
            raise ValueError("Telegram bot token not found in environment variables")
            
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        services['telegram'] = bot
        logger.info("Telegram bot initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Telegram bot: {e}")
        raise
    
    return services 