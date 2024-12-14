import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Define the required Gmail API scopes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify"
]

# Path to the credentials files
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"
