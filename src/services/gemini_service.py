import logging
import google.generativeai as genai
from typing import Dict

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self, api_key: str):
        """
        Initialize the Gemini service with an API key.
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        
    def summarize_info(self, song: Dict, genius_info: Dict) -> str:
        """
        Generate a summary of the song information using Gemini.
        """
        try:
            # Create a prompt that includes both song and Genius info
            prompt = f"""Please provide a concise and engaging summary of this song:

Title: {song['name']}
Artist: {song['artist']}
Album: {genius_info.get('album', 'Unknown')}
Release Date: {genius_info.get('release_date', 'Unknown')}

Additional Information:
{genius_info.get('description', 'No description available.')}

Please include:
1. A brief overview of the song's significance
2. Any notable facts about its creation or impact
3. The song's style and genre
4. Any interesting connections to other artists or works

Keep the summary concise and engaging, focusing on the most interesting aspects."""

            # Generate the summary
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            raise 