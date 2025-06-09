import streamlit as st
from duckduckgo_search import DDGS
import requests
import folium
from streamlit_folium import st_folium

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

# --- Get Coordinates for Map (via OpenStreetMap Nominatim) ---
def get_coordinates(location):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={location}"
    response = requests.get(url).json()
    if response:
        return float(response[0]['lat']), float(response[0]['lon'])
    return None, None

# --- Weather Check Tool using Open-Meteo ---
def get_weather_open_meteo(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()["current_weather"]
        temp = data["temperature"]
        wind = data["windspeed"]
        return f"Temperature: {temp}°C, Wind Speed: {wind} km/h"
    return "Weather data not available"

# --- Streamlit GUI ---
def main():
    st.set_page_config(page_title="Running Route Recommender", layout="wide")
    st.title("🏃 Running Route Recommender")

    with st.sidebar:
        st.header("Your Preferences")
        location = st.text_input("Enter your city or area", "Paris")
        distance_km = st.number_input("Preferred distance (km)", min_value=1.0, value=5.0)
        pace = st.number_input("Your pace (min/km)", min_value=2.0, value=6.0)
        show_weather = st.checkbox("Check weather?", value=True)

    if st.button("Find Running Routes"):
        st.subheader(f"📍 Running Routes in {location}")

        routes = search_running_routes(location, distance_km)
        if routes:
            for i, route in enumerate(routes, 1):
                st.markdown(f"**{i}.** {route}")
        else:
            st.warning("No routes found. Try another location.")

        run_time = estimate_run_time(distance_km, pace)
        st.info(f"⏱️ Estimated run time for {distance_km}km: {run_time}")

        # Map and Weather
        st.subheader("🗺️ Route Area Map")
        lat, lon = get_coordinates(location)
        if lat and lon:
            m = folium.Map(location=[lat, lon], zoom_start=13)
            folium.Marker([lat, lon], tooltip="Start Location").add_to(m)
            st_folium(m, width=700)

            if show_weather:
                st.subheader("☁️ Weather Info")
                weather = get_weather_open_meteo(lat, lon)
                st.text(weather)
        else:
            st.warning("Could not fetch map or weather for this location.")

if __name__ == "__main__":
    main()
