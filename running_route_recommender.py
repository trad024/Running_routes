import os
import requests
import streamlit as st
import google.generativeai as genai
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ---- 🔑 API key loader -----------------------------------------------
try:
    # Works when imported from a Streamlit app
    TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]
    ORS_API_KEY = st.secrets["ORS_API_KEY"]
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    # Fallback for plain-Python runs (pytest, notebook, etc.)
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    ORS_API_KEY = os.getenv("ORS_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TAVILY_API_KEY:
    raise RuntimeError(
        "Tavily API key not found. "
        "Add TAVILY_API_KEY to .streamlit/secrets.toml or an env variable."
    )
if not ORS_API_KEY:
    raise RuntimeError(
        "OpenRouteService API key not found. "
        "Add ORS_API_KEY to .streamlit/secrets.toml or an env variable."
    )
if not GEMINI_API_KEY:
    raise RuntimeError(
        "Gemini API key not found. "
        "Add GEMINI_API_KEY to .streamlit/secrets.toml or an env variable."
    )

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# ---- Functions -------------------------------------------------------

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

@st.cache_data
def get_running_route_geometry(start_coords: tuple, distance_km: float):
    """Fetch a running route geometry from OpenRouteService."""
    if not start_coords or start_coords == (None, None):
        return None
    lat, lon = start_coords
    # Create a simple out-and-back route by offsetting coordinates
    offset = (distance_km / 111) / 2  # Approx km to degrees (1 deg ~ 111 km)
    end_coords = [lat + offset, lon + offset]
    url = "https://api.openrouteservice.org/v2/directions/foot-running/geojson"
    headers = {
        "Content-Type": "application/json",
        "Authorization": ORS_API_KEY,
    }
    payload = {
        "coordinates": [[lon, lat], end_coords],
        "profile": "foot-running",
        "format": "geojson",
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "features" in data and data["features"]:
            coords = data["features"][0]["geometry"]["coordinates"]
            return [[c[1], c[0]] for c in coords]
        return None
    except requests.RequestException as e:
        st.error(f"OpenRouteService error: {str(e)}")
        return None

def estimate_run_time(distance_km, pace_min_per_km):
    """Calculate estimated run time based on distance and pace."""
    total_minutes = distance_km * pace_min_per_km
    minutes = int(total_minutes)
    seconds = int((total_minutes - minutes) * 60)
    return f"{minutes} minutes {seconds} seconds"

@st.cache_data
def get_coordinates(location):
    """Get coordinates for a location using OpenStreetMap Nominatim."""
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={location}"
    headers = {
        "User-Agent": "RunningRouteApp/1.0 (moataz.bentrad@etudiant-fst.utm.tn)"  
    }
    # Set up retry strategy
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    
    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
        else:
            st.error(f"No coordinates found for '{location}'. Try a more specific location (e.g., 'Paris, France').")
            return None, None
    except requests.exceptions.HTTPError as e:
        if response.status_code == 403:
            st.error(
                f"Access denied by Nominatim (HTTP 403) for '{location}'. "
                "Ensure the User-Agent in running_route_recommender.py includes a valid email (e.g., 'yourname@example.com')."
            )
        elif response.status_code == 429:
            st.error("Nominatim rate limit exceeded. Please wait a moment and try again.")
        else:
            st.error(f"Failed to fetch coordinates for '{location}': HTTP {response.status_code} - {str(e)}")
        return None, None
    except requests.RequestException as e:
        st.error(f"Network error fetching coordinates for '{location}': {str(e)}")
        return None, None
    finally:
        session.close()

@st.cache_data
def get_weather_open_meteo(lat, lon):
    """Fetch weather data using Open-Meteo API."""
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

@st.cache_data
def get_gemini_tips(query: str):
    """Fetch tips from Gemini API on running, goal chasing, or nutrition."""
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=(
                "You are a helpful AI assistant specializing in running, goal chasing, and nutrition. "
                "Provide concise, practical, and actionable tips tailored to the user's query. "
                "Focus on running techniques, motivation strategies, or nutrition advice for runners. "
                "Keep responses friendly, witty, and under 200 words."
            )
        )
        response = model.generate_content(query)
        return response.text.strip()
    except Exception as e:
        st.error(f"Gemini API error: {str(e)}")
        return "Sorry, I couldn't fetch tips right now. Try again later!"