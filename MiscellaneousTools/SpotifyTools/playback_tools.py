import subprocess
import time
import re
from difflib import SequenceMatcher
from .spotify_service import get_spotify_service
from langchain_core.tools import tool

sp = get_spotify_service()

def calculate_similarity(a, b):
    """
    Calculate string similarity using SequenceMatcher.
    
    Args:
        a (str): First string to compare
        b (str): Second string to compare
    
    Returns:
        float: Similarity ratio between 0 and 1
    """
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def parse_query(query):
    """
    Parse search query to extract song and artist if specified.
    
    Args:
        query (str): Search query
    
    Returns:
        dict: Parsed search parameters
    """
    # Regex to match variations like "Song by Artist", "Song - Artist", "Song Artist"
    patterns = [
        r'^(.+)\s+(?:by|from|of)\s+(.+)$',  # "Song by Artist"
        r'^(.+)\s*-\s*(.+)$',               # "Song - Artist"
    ]
    
    for pattern in patterns:
        match = re.match(pattern, query, re.IGNORECASE)
        if match:
            return {
                'song': match.group(1).strip(),
                'artist': match.group(2).strip(),
                'search_type': 'track'
            }
    
    # If no specific artist mentioned, default to track search
    return {
        'song': query.strip(),
        'artist': None,
        'search_type': 'track'
    }

@tool
def search_and_play(query, search_type=None, retrying=False):
    """
    Search for and play music on Spotify with improved relevance and flexibility.
    
    Args:
        query (str): Search term (can include song and artist)
        search_type (str, optional): Override search type
        retrying (bool): Flag indicating whether this is a retry attempt
    
    Returns:
        bool: True if playback started successfully, False otherwise
    """
    # Parse the query
    parsed_query = parse_query(query)
    
    # Override search type if explicitly provided
    if search_type:
        parsed_query['search_type'] = search_type
    
    # Perform search
    results = sp.search(
        q=parsed_query['song'], 
        type='track', 
        limit=20
    )
    
    # Filter tracks by artist if specified
    tracks = results['tracks']['items']
    if parsed_query['artist']:
        tracks = [
            track for track in tracks 
            if calculate_similarity(parsed_query['artist'], track['artists'][0]['name']) > 0.6
        ]
    
    # Select most relevant track
    most_relevant_track = None
    highest_similarity = 0
    
    for track in tracks:
        similarity = calculate_similarity(parsed_query['song'], track['name'])
        if similarity > highest_similarity:
            highest_similarity = similarity
            most_relevant_track = track
    
    # If no relevant track found
    if not most_relevant_track:
        print(f'No track found matching "{query}".')
        return False

    # Playback logic (similar to previous implementation)
    devices = sp.devices()
    available_devices = devices['devices']

    if available_devices:
        # Prefer active device
        for device in available_devices:
            if device['is_active']:
                device_id = device['id']
                sp.start_playback(device_id=device_id, uris=[most_relevant_track['uri']])
                print(f'Playing "{most_relevant_track["name"]}" by {most_relevant_track["artists"][0]["name"]} on active device: {device["name"]}')
                return True

        # If no active device, use the first available
        device_id = available_devices[0]['id']
        sp.start_playback(device_id=device_id, uris=[most_relevant_track['uri']])
        print(f'Playing "{most_relevant_track["name"]}" by {most_relevant_track["artists"][0]["name"]} on device: {available_devices[0]["name"]}')
        return True

    # No devices available - attempt to launch Spotify
    if not retrying:
        print('No available devices for playback.')
        print('Attempting to launch Spotify Desktop app...')
        try:
            subprocess.run(["open", "-a", "Spotify"])  # macOS-specific
            print("Spotify Desktop app launched.")
            time.sleep(5)
            return search_and_play(query, retrying=True)
        except Exception as e:
            print(f"Failed to launch Spotify Desktop app: {e}")
            return False

    print("No available devices for playback after retrying.")
    return False