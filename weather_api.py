import requests
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/"

def get_current_weather(location):
    try:
        params = {
            "q": location,
            "appid": API_KEY,
            "units": "metric"
        }
        response = requests.get(BASE_URL + "weather", params=params)
        data = response.json()

        if response.status_code != 200:
            return {
                "reply": f"Could not get current weather for '{location}'. Please check the location name.",
                "lat": None,
                "lon": None,
                "location": location
            }

        name = data.get("name", location.title())
        weather_desc = data["weather"][0]["description"].capitalize()
        temp = data["main"]["temp"]
        dt = datetime.utcfromtimestamp(data["dt"]).strftime('%I:%M %p')
        lat = data["coord"]["lat"]
        lon = data["coord"]["lon"]

        text = f"As of {dt} UTC, it’s {temp}°C and {weather_desc} in {name}."

        return {
            "reply": text,
            "lat": lat,
            "lon": lon,
            "location": name
        }

    except Exception as e:
        return {
            "reply": f"Error retrieving current weather: {str(e)}",
            "lat": None,
            "lon": None,
            "location": location
        }


def get_hourly_forecast(location):
    try:
        params = {
            "q": location,
            "appid": API_KEY,
            "units": "metric",
            "cnt": 8  # Next 24 hours (3-hour steps)
        }
        response = requests.get(BASE_URL + "forecast", params=params)
        data = response.json()

        if response.status_code != 200:
            return {
                "reply": f"Could not get hourly forecast for '{location}'. Please check the location name.",
                "lat": None,
                "lon": None,
                "location": location
            }

        city = data.get("city", {})
        lat = city.get("coord", {}).get("lat")
        lon = city.get("coord", {}).get("lon")
        city_name = city.get("name", location.title())

        forecast_lines = [f"Hourly forecast for {city_name}:"]
        for item in data["list"]:
            time = datetime.utcfromtimestamp(item["dt"]).strftime('%Y-%m-%d %H:%M')
            temp = item["main"]["temp"]
            desc = item["weather"][0]["description"].capitalize()
            forecast_lines.append(f"{time}: {temp}°C, {desc}")

        text = "\n".join(forecast_lines)

        return {
            "reply": text,
            "lat": lat,
            "lon": lon,
            "location": city_name
        }

    except Exception as e:
        return {
            "reply": f"Error retrieving hourly forecast: {str(e)}",
            "lat": None,
            "lon": None,
            "location": location
        }


def get_5_day_forecast(location):
    try:
        location = location.strip().strip('"').strip("'")
        params = {
            "q": location,
            "appid": API_KEY,
            "units": "metric"
        }
        response = requests.get(BASE_URL + "forecast", params=params)
        data = response.json()

        if response.status_code != 200:
            return {
                "reply": f"Could not get 5 day forecast for '{location}'. Please check the location name.",
                "lat": None,
                "lon": None,
                "location": location
            }

        city = data.get("city", {})
        lat = city.get("coord", {}).get("lat")
        lon = city.get("coord", {}).get("lon")
        city_name = city.get("name", location.title())

        daily_forecasts = {}
        for item in data["list"]:
            dt_txt = item["dt_txt"]
            if "12:00:00" in dt_txt:
                date = dt_txt.split(" ")[0]
                temp = item["main"]["temp"]
                desc = item["weather"][0]["description"].capitalize()
                daily_forecasts[date] = (temp, desc)

        forecast_lines = [f"5-day forecast for {city_name}:"]
        for date, (temp, desc) in daily_forecasts.items():
            forecast_lines.append(f"{date}: {temp}°C, {desc}")

        text = "\n".join(forecast_lines)

        return {
            "reply": text,
            "lat": lat,
            "lon": lon,
            "location": city_name
        }

    except Exception as e:
        return {
            "reply": f"Error retrieving 5 day forecast: {str(e)}",
            "lat": None,
            "lon": None,
            "location": location
        }
