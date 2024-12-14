import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Define the required Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Path to the credentials files
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "calendar_token.json"
