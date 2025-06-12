import random
import logging
from spotipy.exceptions import SpotifyException

logger = logging.getLogger(__name__)

class SpotifyService:
    def __init__(self, sp_client):
        self.sp = sp_client
        self.genres = [
            'rock', 'pop', 'hip-hop', 'jazz', 'classical',
            'electronic', 'folk', 'country', 'blues', 'metal'
        ]
        # Test the connection
        self._test_connection()

    def _test_connection(self):
        """
        Test the Spotify connection and credentials.
        """
        try:
            # Try a simple API call to test the connection
            logger.info("Testing Spotify connection...")
            logger.info(f"Using client ID: {self.sp._auth_manager.client_id}")
            results = self.sp.search('test', limit=1)
            logger.info("Successfully connected to Spotify API")
        except SpotifyException as e:
            if e.http_status == 403:
                logger.error(f"Spotify API authentication failed. Status: {e.http_status}, Message: {e.msg}")
                raise Exception(f"Spotify API authentication failed. Status: {e.http_status}, Message: {e.msg}")
            else:
                logger.error(f"Error connecting to Spotify API: {e}")
                raise
        except Exception as e:
            logger.error(f"Unexpected error testing Spotify connection: {e}")
            raise

    def get_random_song(self):
        """
        Get a random song from Spotify using their API.
        Raises:
            Exception: If there's an error fetching the song from Spotify
        """
        try:
            # Select a random genre
            genre = random.choice(self.genres)
            logger.info(f"Searching for songs in genre: {genre}")
            
            # Search for tracks in the selected genre
            results = self.sp.search(q=f'genre:{genre}', type='track', limit=50)
            
            if not results['tracks']['items']:
                raise Exception(f"No tracks found for genre: {genre}")
            
            # Select a random track from the results
            track = random.choice(results['tracks']['items'])
            logger.info(f"Selected track: {track['name']} by {track['artists'][0]['name']}")
            
            return self._format_song_info(track)
        except SpotifyException as e:
            if e.http_status == 403:
                logger.error(f"Spotify API authentication failed. Status: {e.http_status}, Message: {e.msg}")
                raise Exception(f"Spotify API authentication failed. Status: {e.http_status}, Message: {e.msg}")
            else:
                logger.error(f"Error fetching song from Spotify: {e}")
                raise
        except Exception as e:
            logger.error(f"Error fetching song from Spotify: {e}")
            raise

    def _format_song_info(self, track):
        """
        Format track information into a dictionary.
        """
        try:
            return {
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'album': track['album']['name'],
                'release_date': track['album']['release_date'],
                'spotify_url': track['external_urls']['spotify'],
                'popularity': track['popularity'],
                'duration_ms': track['duration_ms']
            }
        except Exception as e:
            logger.error(f"Error formatting song info: {e}")
            raise

    def get_multiple_songs(self):
        """
        Get multiple songs from Spotify. Currently returns a list with one random song.
        """
        song = self.get_random_song()
        return [song] 