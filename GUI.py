import streamlit as st
import re
import folium
from streamlit_folium import st_folium

from running_route_recommender import (
    search_running_routes,
    estimate_run_time,
    get_coordinates,
    get_weather_open_meteo,
    get_running_route_geometry,
    get_gemini_tips,
    TAVILY_API_KEY,
)

for key, value in {
    "routes": [],
    "coords": None,
    "weather": "",
    "favorites": [],
    "route_geometry": None,
    "chat_history": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = value
def main() -> None:
    st.set_page_config(page_title="Running Route Recommender", layout="wide")
    st.title("🏃 Running Route Recommender")
    with st.sidebar:
        st.header("Your Preferences")
        location = st.text_input("Enter your city or area", "Paris, France", help="Use format: City, Country (e.g., Paris, France)")
        distance_km = st.number_input("Preferred distance (km)", min_value=0.1, value=5.0)
        pace = st.number_input("Your pace (min/km)", min_value=1.0, value=6.0)
        show_weather = st.checkbox("Check weather?", value=True)
        if not location.strip():
            st.error("Please enter a valid location.")
            st.stop()
        if not re.match(r"^[a-zA-Z\s,.-]+$", location.strip()):
            st.error("Location should contain letters, spaces, commas, periods, or hyphens only (e.g., 'Paris, France').")
            st.stop()
        if distance_km <= 0:
            st.error("Distance must be greater than 0 km.")
            st.stop()
        if pace <= 0:
            st.error("Pace must be greater than 0 min/km.")
            st.stop()

    if st.button("Find Running Routes"):
        # Fetch and cache routes
        st.session_state.routes = search_running_routes(location, distance_km)

        # Fetch and cache coordinates
        st.session_state.coords = get_coordinates(location)

        # Fetch route geometry
        if st.session_state.coords and st.session_state.coords != (None, None):
            st.session_state.route_geometry = get_running_route_geometry(st.session_state.coords, distance_km)
        else:
            st.session_state.route_geometry = None

        # Optionally fetch weather
        if show_weather and st.session_state.coords and st.session_state.coords != (None, None):
            lat, lon = st.session_state.coords
            st.session_state.weather = get_weather_open_meteo(lat, lon)
        else:
            st.session_state.weather = ""

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

    if st.session_state.routes:
        csv = "\n".join([f"{i+1},{r}" for i, r in enumerate(st.session_state.routes)])
        st.download_button(
            label="Export Routes as CSV",
            data=f"Route,Details\n{csv}",
            file_name=f"routes_{location}.csv",
            mime="text/csv"
        )

    # Display favorite routes
    if st.session_state.favorites:
        st.subheader("🌟 Favorite Routes")
        for r in st.session_state.favorites:
            title, url = r.rsplit(" - ", 1) if " - " in r else (r, "#")
            st.markdown(f"- [{title}]({url})")

    run_time = estimate_run_time(distance_km, pace)
    st.info(f"⏱️ Estimated run time for {distance_km} km: {run_time}")

    #Map
    if st.session_state.coords and st.session_state.coords != (None, None):
        lat, lon = st.session_state.coords
        m = folium.Map(location=[lat, lon], zoom_start=13)
        folium.Marker([lat, lon], tooltip="Start Location").add_to(m)
        if st.session_state.route_geometry:
            folium.PolyLine(st.session_state.route_geometry, color="blue", weight=5, tooltip="Running Route").add_to(m)
        st.subheader("🗺️ Route Area Map")
        st_folium(m, width=700)
    else:
        st.error(f"Map unavailable: Could not fetch coordinates for '{location}'. Please check your location input (e.g., 'Paris, France') and ensure a valid User-Agent is set in running_route_recommender.py.")

    #Weather
    if show_weather and st.session_state.weather:
        st.subheader("🌤️ Weather Info")
        st.text(st.session_state.weather)

    #Chatbot
    st.subheader("💬 Chat with Gemini for Running Tips")
    st.write("Ask for tips on running, nutrition, or goal chasing (e.g., 'How can I improve my running form?' or 'What should I eat before a run?').")
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if prompt := st.chat_input("Type your question here..."):
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        response = get_gemini_tips(prompt)
        with chat_container:
            with st.chat_message("assistant"):
                st.markdown(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()