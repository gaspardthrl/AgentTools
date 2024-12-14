import spotipy
from spotipy.oauth2 import SpotifyOAuth
from .config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE

def get_spotify_service():
    """
    Authenticate and return a Spotify service object.

    Returns:
        spotipy.Spotify: Authenticated Spotify client
    """
    auth_manager = SpotifyOAuth(client_id=CLIENT_ID,
                                 client_secret=CLIENT_SECRET,
                                 redirect_uri=REDIRECT_URI,
                                 scope=SCOPE)
    
    return spotipy.Spotify(auth_manager=auth_manager)
