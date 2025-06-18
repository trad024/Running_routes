import streamlit as st
import folium
from streamlit_folium import st_folium

from running_route_recommender import (
    search_running_routes,
    estimate_run_time,
    get_coordinates,
    get_weather_open_meteo,
    TAVILY_API_KEY,
)

# ──────────────────────────────────────────────────────────────────────────────
# 1 )  Initialise session-state placeholders (persist across reruns)
# ──────────────────────────────────────────────────────────────────────────────
for key, default in {
    "routes": [],
    "coords": None,
    "weather": "",
    "favorites": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ──────────────────────────────────────────────────────────────────────────────
# 2 )  Main GUI
# ──────────────────────────────────────────────────────────────────────────────
def main() -> None:
    st.set_page_config(page_title="Running Route Recommender", layout="wide")
    st.title("🏃 Running Route Recommender")

    # — Sidebar inputs —
    with st.sidebar:
        st.header("Your Preferences")
        location = st.text_input("Enter your city or area", "Paris")
        distance_km = st.number_input("Preferred distance (km)", min_value=0.1, value=5.0)
        pace = st.number_input("Your pace (min/km)", min_value=1.0, value=6.0)
        show_weather = st.checkbox("Check weather?", value=True)

        # Input validation
        if not location.strip():
            st.error("Please enter a valid location.")
            st.stop()
        if distance_km <= 0:
            st.error("Distance must be greater than 0 km.")
            st.stop()
        if pace <= 0:
            st.error("Pace must be greater than 0 min/km.")
            st.stop()

    # — Run search only when button pressed —
    if st.button("Find Running Routes"):
        # ① Fetch and cache routes
        st.session_state.routes = search_running_routes(location, distance_km)

        # ② Fetch and cache coordinates
        st.session_state.coords = get_coordinates(location)

        # ③ Optionally fetch weather
        if show_weather and st.session_state.coords and st.session_state.coords != (None, None):
            lat, lon = st.session_state.coords
            st.session_state.weather = get_weather_open_meteo(lat, lon)
        else:
            st.session_state.weather = ""

    # ───────────────────────── Display cached results ─────────────────────────
    st.subheader(f"📍 Running Routes in {location}")
    if st.session_state.routes:
        for i, r in enumerate(st.session_state.routes, start=1):
            title, url = r.rsplit(" - ", 1) if " - " in r else (r, "#")
            st.markdown(f"**{i}.** [{title}]({url})")
            if st.button("Save to Favorites", key=f"save_{i}"):
                if r not in st.session_state.favorites:
                    st.session_state.favorites.append(r)
                    st.success(f"Saved '{title}' to favorites!")
    else:
        st.info("No routes yet – click **Find Running Routes**")

    # Display favorite routes
    if st.session_state.favorites:
        st.subheader("⭐ Favorite Routes")
        for r in st.session_state.favorites:
            title, url = r.rsplit(" - ", 1) if " - " in r else (r, "#")
            st.markdown(f"- [{title}]({url})")

    run_time = estimate_run_time(distance_km, pace)
    st.info(f"⏱️ Estimated run time for {distance_km} km: {run_time}")

    # — Map —
    if st.session_state.coords and st.session_state.coords != (None, None):
        lat, lon = st.session_state.coords
        m = folium.Map(location=[lat, lon], zoom_start=13)
        folium.Marker([lat, lon], tooltip="Start Location").add_to(m)
        st.subheader("🗺️ Route Area Map")
        st_folium(m, width=700)
    else:
        st.warning("Map unavailable: Could not fetch coordinates for the location.")

    # — Weather —
    if show_weather and st.session_state.weather:
        st.subheader("☁️ Weather Info")
        st.text(st.session_state.weather)

if __name__ == "__main__":
    main()