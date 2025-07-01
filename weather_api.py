import requests
from datetime import datetime, timezone, timedelta

import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

API_KEY = os.getenv("OPENWEATHER_API_KEY")



# Emoji mapping based on weather condition
weather_emojis = {
    "Clear": "☀️",
    "Clouds": "⛅",
    "Rain": "🌧️",
    "Drizzle": "🌦️",
    "Thunderstorm": "⛈️",
    "Snow": "❄️",
    "Mist": "🌫️",
    "Smoke": "🌫️",
    "Haze": "🌫️",
    "Dust": "🌪️",
    "Fog": "🌫️",
    "Sand": "🌪️",
    "Ash": "🌋",
    "Squall": "🌬️",
    "Tornado": "🌪️"
}

def get_temperature(city, country_code=''):
    if country_code:
        query = f"{city},{country_code}"
    else:
        query = city

    url = f"https://api.openweathermap.org/data/2.5/weather?q={query}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and "main" in data:
        temp = data["main"]["temp"]
        condition = data["weather"][0]["main"]
        emoji = weather_emojis.get(condition, "🌈")

        timestamp = data["dt"]
        timezone_offset = data["timezone"]  # seconds offset from UTC

        city_tz = timezone(timedelta(seconds=timezone_offset))
        local_time = datetime.fromtimestamp(timestamp, tz=timezone.utc).astimezone(city_tz)
        time_str = local_time.strftime("%I:%M %p")

        city_name = data.get("name", city)

        return f"As of {time_str}, it’s {temp}°C and {condition} in {city_name} {emoji}"

    elif "message" in data:
        return "Sorry, I couldn't find the weather for that location. Please try a city name."
    else:
        return "Sorry, something went wrong fetching the weather."
