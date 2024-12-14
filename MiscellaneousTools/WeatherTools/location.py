import requests
from langchain_core.tools import tool

@tool
def find_location() -> str:
    """
    Retrieve the current location of user if no location was specified in the query.
    
    Returns:
        str: The city of the user
        str: The region of the user
        str: The country of the user
    """
    try:
        response = requests.get("https://ipinfo.io/")
        data = response.json()
        city = data["city"]
        region = data["region"]
        country = data["country"]
        return city, region, country
    except requests.RequestException as e:
        return f"Error fetching location: {e}"

