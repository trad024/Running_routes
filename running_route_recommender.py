import os
import requests
import streamlit as st

# ---- 🔑 Tavily API key loader -----------------------------------------------
try:
    # Works when imported from a Streamlit app
    TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]
except Exception:
    # Fallback for plain-Python runs (pytest, notebook, etc.)
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise RuntimeError(
        "Tavily API key not found. "
        "Add TAVILY_API_KEY to .streamlit/secrets.toml or an env variable."
    )
# -----------------------------------------------------------------------------

@st.cache_data
def search_running_routes(location: str, distance_km: float):
    """Return up to 5 route titles + URLs from Tavily."""
    query = f"best running routes or parks in {location} around {distance_km} km"
    url = "https://api.tavily.com/search"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TAVILY_API_KEY}",
    }
    payload = {
        "query": query,
        "search_depth": "basic",
        "include_answer": False,
    }

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=15)
        r.raise_for_status()
        hits = r.json().get("results", [])
        return [f"{h['title']} - {h['url']}" for h in hits[:5]]
    except requests.RequestException as exc:
        st.error(f"Tavily API error: {exc}")
        return [f"❌ Tavily error: {exc}"]

# --- Run Time Calculator ---
def estimate_run_time(distance_km, pace_min_per_km):
    total_minutes = distance_km * pace_min_per_km
    minutes = int(total_minutes)
    seconds = int((total_minutes - minutes) * 60)
    return f"{minutes} minutes {seconds} seconds"

# --- Get Coordinates for Map (via OpenStreetMap Nominatim) ---
@st.cache_data
def get_coordinates(location):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={location}"
    headers = {
        "User-Agent": "RunningRouteApp/1.0 (your.actual.email@example.com)"  # Replace with your email
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
        else:
            st.warning(f"No coordinates found for '{location}'")
            return None, None
    except requests.RequestException as e:
        st.error(f"Failed to fetch coordinates for '{location}': {str(e)}")
        return None, None

# --- Weather Check Tool using Open-Meteo ---
@st.cache_data
def get_weather_open_meteo(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()["current_weather"]
        temp = data["temperature"]
        wind = data["windspeed"]
        return f"Temperature: {temp}°C, Wind Speed: {wind} km/h"
    except requests.RequestException as e:
        st.error(f"Failed to fetch weather data: {str(e)}")
        return "Weather data not available"