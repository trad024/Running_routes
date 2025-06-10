import streamlit as st
import folium
from streamlit_folium import st_folium

from running_route_recommender import (
    search_running_routes,
    estimate_run_time,
    #get_coordinates,
    get_weather_open_meteo
)

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
