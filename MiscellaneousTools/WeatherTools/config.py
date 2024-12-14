import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Define the API key for weather API
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
