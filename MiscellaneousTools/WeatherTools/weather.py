import requests
import datetime
from typing import Optional
from .config import WEATHER_API_KEY

from langchain_core.tools import tool

@tool
def current_weather(location: str) -> str:
    """
    Retrieve current weather for a given location.

    Args:
        location (str): City name to search current weather for
    
    Returns:
        str: Detailed current weather information
    """
    base_url = "http://api.weatherapi.com/v1/current.json"
    
    try:
        params = {
            "key": WEATHER_API_KEY,
            "q": location,
            "aqi": "no"  # No air quality data
        }
        
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        current = data['current']
        location_info = data['location']
        
        weather_info = (
            f"Current Weather in {location_info['name']}, {location_info['country']}:\n"
            f"Temperature: {current['temp_c']}°C (Feels like {current['feelslike_c']}°C)\n"
            f"Condition: {current['condition']['text']}\n"
            f"Humidity: {current['humidity']}%\n"
            f"Wind: {current['wind_kph']} km/h {current['wind_dir']} (Gusts up to {current['gust_kph']} km/h)\n"
            f"Visibility: {current['vis_km']} km\n"
            f"UV Index: {current['uv']}\n"
            f"Precipitation: {current['precip_mm']} mm"
        )
        
        return weather_info
    
    except requests.RequestException as e:
        return f"Error fetching current weather: {e}"

@tool
def forecast_weather(location: str, date: Optional[str] = None) -> str:
    """
    Retrieve weather forecast for a given location and optional date.

    Args:
        location (str): City name to search weather forecast for
        date (Optional[str]): Specific date for forecast (YYYY-MM-DD)

    Returns:
        str: Detailed weather forecast information
    """
    base_url = "http://api.weatherapi.com/v1/forecast.json"
    
    try:
        forecast_days = abs((datetime.datetime.strptime(date, '%Y-%m-%d').date() - datetime.datetime.now().date()).days) + 1 if date else 3
        params = {
            "key": WEATHER_API_KEY,
            "q": location,
            "days": forecast_days,
            "aqi": "no"
        }
        
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        forecast_day = data['forecast']['forecastday'][0] if not date else next(
            (day for day in data['forecast']['forecastday'] if day['date'] == date), 
            data['forecast']['forecastday'][0]
        )
        
        day_forecast = forecast_day['day']
        astro = forecast_day['astro']
        
        hour_forecasts = forecast_day['hour']
        
        forecast_info = (
            f"Weather Forecast for {location} on {forecast_day['date']}:\n"
            f"Day Condition: {day_forecast['condition']['text']}\n"
            f"Max Temperature: {day_forecast['maxtemp_c']}°C\n"
            f"Min Temperature: {day_forecast['mintemp_c']}°C\n"
            f"Average Temperature: {day_forecast['avgtemp_c']}°C\n"
            f"Chance of Rain: {day_forecast['daily_chance_of_rain']}%\n"
            f"Total Precipitation: {day_forecast['totalprecip_mm']} mm\n"
            f"Max Wind Speed: {day_forecast['maxwind_kph']} km/h\n"
            f"Sunrise: {astro['sunrise']}\n"
            f"Sunset: {astro['sunset']}\n"
            f"Moon Phase: {astro['moon_phase']}\n\n"
            "Hourly Forecast Highlights:\n" +
            "\n".join([
                f"{hour['time'].split()[-1]}: {hour['temp_c']}°C, {hour['condition']['text']}, "
                f"Rain Chance: {hour['chance_of_rain']}%, Wind: {hour['wind_kph']} km/h"
                for hour in hour_forecasts[::3]
            ])
        )
        
        return forecast_info
    
    except requests.RequestException as e:
        return f"Error fetching weather forecast: {e}"
