import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Define the Spotify API credentials and redirect URI
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID', 'default_client_id')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET', 'default_client_secret')
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:8888/callback/')

# Define the scopes for playback control
SCOPE = 'user-read-playback-state user-modify-playback-state'