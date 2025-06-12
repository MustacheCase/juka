from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

print(f"Using Client ID: {client_id}")
print(f"Using Client Secret: {client_secret}")

# Initialize Spotify client
auth_manager = SpotifyClientCredentials(
    client_id=client_id,
    client_secret=client_secret
)
sp = Spotify(auth_manager=auth_manager)

# Test basic search
print("\nTesting basic search...")
results = sp.search('Bohemian Rhapsody', limit=1)
print(f"Search successful: {results['tracks']['items'][0]['name']}")

# Test getting track features
print("\nTesting track features...")
track_id = results['tracks']['items'][0]['id']
features = sp.audio_features(track_id)
print(f"Features retrieved: {features[0] if features else 'None'}") 