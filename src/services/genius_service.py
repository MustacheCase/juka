import logging
import requests
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class GeniusService:
    def __init__(self, access_token: str):
        """
        Initialize the Genius service with an access token.
        """
        self.access_token = access_token
        self.base_url = "https://api.genius.com"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "OneSongEachDay/1.0"
        }

    def get_song_info(self, song_name: str, artist_name: str) -> Optional[Dict]:
        """
        Get song information from Genius API.
        Returns a dictionary with song information or None if not found.
        """
        try:
            # Search for the song
            search_url = f"{self.base_url}/search"
            params = {
                "q": f"{song_name} {artist_name}"
            }
            
            response = requests.get(search_url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            hits = data.get("response", {}).get("hits", [])
            
            if not hits:
                logger.warning(f"No results found for {song_name} by {artist_name}")
                return None
                
            # Get the first hit
            hit = hits[0]
            song_data = hit.get("result", {})
            
            # Get the song details
            song_id = song_data.get("id")
            if not song_id:
                return None
                
            song_url = f"{self.base_url}/songs/{song_id}"
            song_response = requests.get(song_url, headers=self.headers)
            song_response.raise_for_status()
            
            song_details = song_response.json().get("response", {}).get("song", {})
            
            # Format the information
            return {
                "title": song_details.get("title", song_name),
                "artist": song_details.get("primary_artist", {}).get("name", artist_name),
                "album": song_details.get("album", {}).get("name", "Unknown Album"),
                "release_date": song_details.get("release_date_for_display", "Unknown"),
                "genius_url": song_details.get("url", ""),
                "description": song_details.get("description", {}).get("plain", ""),
                "producer_artists": [artist.get("name") for artist in song_details.get("producer_artists", [])],
                "writer_artists": [artist.get("name") for artist in song_details.get("writer_artists", [])],
                "featured_artists": [artist.get("name") for artist in song_details.get("featured_artists", [])],
                "genres": [genre.get("name") for genre in song_details.get("genres", [])],
                "tags": [tag.get("name") for tag in song_details.get("tags", [])]
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching song info from Genius: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Genius service: {e}")
            return None

    def format_info(self, info: Dict) -> str:
        """
        Format the song information into a readable string.
        """
        if not info:
            return "No information found on Genius."
            
        formatted = f"🎵 {info['title']} by {info['artist']}\n\n"
        
        if info.get('album'):
            formatted += f"💿 Album: {info['album']}\n"
        if info.get('release_date'):
            formatted += f"📅 Released: {info['release_date']}\n"
            
        if info.get('producer_artists'):
            formatted += f"\n🎛️ Producers: {', '.join(info['producer_artists'])}\n"
        if info.get('writer_artists'):
            formatted += f"✍️ Writers: {', '.join(info['writer_artists'])}\n"
        if info.get('featured_artists'):
            formatted += f"🎤 Featured Artists: {', '.join(info['featured_artists'])}\n"
            
        if info.get('genres'):
            formatted += f"\n🎼 Genres: {', '.join(info['genres'])}\n"
        if info.get('tags'):
            formatted += f"🏷️ Tags: {', '.join(info['tags'])}\n"
            
        if info.get('description'):
            formatted += f"\n📝 Description:\n{info['description']}\n"
            
        if info.get('genius_url'):
            formatted += f"\n🔗 More info: {info['genius_url']}"
            
        return formatted 