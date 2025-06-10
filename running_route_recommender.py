from duckduckgo_search import DDGS
import requests

# --- DuckDuckGo Search Tool ---
def search_running_routes(location, distance_km):
    query = f"popular running trails {location} {distance_km}km"
    with DDGS() as ddgs:
        results = ddgs.text(query)
        return [r['title'] + " - " + r['href'] for r in results[:5]]

# --- Run Time Calculator ---
def estimate_run_time(distance_km, pace_min_per_km):
    total_minutes = distance_km * pace_min_per_km
    minutes = int(total_minutes)
    seconds = int((total_minutes - minutes) * 60)
    return f"{minutes} minutes {seconds} seconds"

# --- Get Coordinates for Map ---
'''def get_coordinates(location):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={location}"
    headers = {
        "User-Agent": "RunningRouteApp/1.0 (your_email@example.com)"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                return float(data[0]['lat']), float(data[0]['lon'])
            else:
                return None, None
        else:
            return None, None
    except Exception as e:
        print("Error fetching coordinates:", e)
        return None, None'''


# --- Weather using Open-Meteo ---
def get_weather_open_meteo(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()["current_weather"]
        temp = data["temperature"]
        wind = data["windspeed"]
        return f"Temperature: {temp}°C, Wind Speed: {wind} km/h"
    return "Weather data not available"
