from flask import Flask, render_template, request, jsonify
from weather_api import get_temperature
import re

app = Flask(__name__)

def extract_location_and_country(user_input):
    # Try to extract "in city, country" or "at city, country"
    pattern = r'\b(?:in|at)\s+([a-zA-Z\s]+?)(?:,\s*([a-zA-Z]{2}))?(?:\?|$)'
    match = re.search(pattern, user_input, re.IGNORECASE)
    if match:
        city = match.group(1).strip().title()
        country = match.group(2).upper() if match.group(2) else ''
        return city, country

    # If user inputs like "New York, US" without 'in' or 'at'
    if ',' in user_input:
        parts = user_input.split(',')
        city = parts[0].strip().title()
        country = parts[1].strip().upper() if len(parts) > 1 else ''
        return city, country

    # Otherwise, treat whole input as city without country
    return user_input.strip().title(), ''

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form.get('message')
        city, country_code = extract_location_and_country(user_input)
        response = get_temperature(city, country_code)
        return jsonify({"response": response})
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
