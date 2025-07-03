from timezonefinder import TimezoneFinder
import pytz
import re
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from weather_api import get_current_weather, get_hourly_forecast, get_5_day_forecast

app = Flask(__name__, static_folder='static', template_folder='templates')


def generate_response(user_message: str) -> dict:
    """
    Basic intent parsing to decide which weather info to fetch.
    Returns a dict with keys: reply, location, lat, lon
    """
    message = user_message.lower()
    location = extract_location(message)

    if not location:
        return {
            "reply": "Please specify a location to get weather information.",
            "location": None,
            "lat": None,
            "lon": None,
        }

    # Call weather APIs depending on intent keywords
    if "hourly" in message:
        response = get_hourly_forecast(location)
    elif "5 day" in message or "5-day" in message or "five day" in message:
        response = get_5_day_forecast(location)
    elif "current" in message or "weather" in message:
        response = get_current_weather(location)
    else:
        return {
            "reply": "Sorry, I didn't understand. You can ask for current weather, hourly forecast, or 5 day forecast.",
            "location": None,
            "lat": None,
            "lon": None,
        }

    # Adjust UTC time in reply to local time if lat/lon and reply exist
    try:
        lat = response.get("lat")
        lon = response.get("lon")
        reply = response.get("reply", "")

        if lat is not None and lon is not None and reply:
            tf = TimezoneFinder()
            timezone_str = tf.timezone_at(lat=lat, lng=lon)
            if timezone_str:
                # Extract time substring e.g. "As of 07:42 AM UTC"
                match = re.search(r"As of (\d{2}:\d{2} [AP]M) UTC", reply)
                if match:
                    utc_time_str = match.group(1)
                    # Parse time string (hour:min AM/PM)
                    utc_time = datetime.strptime(utc_time_str, "%I:%M %p")

                    # Attach current date to utc_time
                    now_utc = datetime.utcnow()
                    utc_time = utc_time.replace(year=now_utc.year, month=now_utc.month, day=now_utc.day)

                    # Convert to timezone-aware datetime
                    utc_zone = pytz.timezone("UTC")
                    local_zone = pytz.timezone(timezone_str)
                    utc_time = utc_zone.localize(utc_time)
                    local_time = utc_time.astimezone(local_zone)

                    # Format new time string like "08:12 AM IST"
                    local_time_str = local_time.strftime("%I:%M %p %Z")

                    # Replace in the reply
                    reply = reply.replace(f"As of {utc_time_str} UTC", f"As of {local_time_str}")

                    response["reply"] = reply
    except Exception as e:
        print(f"Error adjusting time zone: {e}")

    return response


def extract_location(text: str) -> str:
    """
    Simple location extractor by removing known keywords.
    """
    keywords = ["current", "weather", "hourly", "forecast", "in", "5 day", "5-day", "five day", "of"]
    lowered = text.lower()
    for kw in keywords:
        lowered = lowered.replace(kw, "")
    location = lowered.strip()
    return location if location else None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        response_data = generate_response(data.get('message', ''))
        result = {
            "reply": response_data.get("reply", ""),
            "lat": response_data.get("lat"),
            "lon": response_data.get("lon"),
            "location": response_data.get("location")
        }
        print("DEBUG → /api/chat returns:", result)
        return jsonify(result), 200
    except Exception as e:
        print("ERROR /api/chat:", e)
        return jsonify({
            "reply": "Something went wrong, please try again.",
            "lat": None, "lon": None, "location": None
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
