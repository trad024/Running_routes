# Running Route Recommender

A Streamlit web app that helps runners find the best running routes based on location, preferred distance, and pace. It integrates multiple APIs to provide route suggestions, interactive maps, weather updates, and personalized running tips via a chatbot.
## Features
- **Route Search**: Find up to 5 running routes using the Tavily API, tailored to your location and distance.
- **Interactive Map**: Visualize routes on a map with OpenRouteService and Nominatim APIs.
- **Weather Info**: Get current temperature and wind speed via Open-Meteo API.
- **Run Time Estimate**: Calculate estimated run time based on distance and pace.
- **Favorites**: Save favorite routes for quick access.
- **CSV Export**: Download route details as a CSV file.
- **Gemini Chatbot**: Ask for running, nutrition, or goal-chasing tips using Google’s Gemini API.

## Requirements
- Python 3.8+
- API keys for:
  - [Tavily](https://tavily.com) (route search)
  - [OpenRouteService](https://openrouteservice.org) (route geometry)
  - [Google AI Studio](https://aistudio.google.com) (Gemini chatbot)
- Internet connection for API calls

## Setup Instructions
1. **Clone or Download the Project**:
   - Place the project files in a directory (e.g., `C:\vs_code\running_project`).
2. **Install Dependencies**:
   - Open a terminal in the project directory and run:
     ```bash
     pip install streamlit folium streamlit-folium requests google-generativeai
     ```
3. **Configure API Keys**:
   - Create a `.streamlit` folder in the project directory.
   - Create a `secrets.toml` file in `.streamlit` with your API keys:
     ```toml
     TAVILY_API_KEY = "your_tavily_key"
     ORS_API_KEY = "your_openrouteservice_key"
     GEMINI_API_KEY = "your_gemini_key"
     ```
   - Obtain keys from Tavily, OpenRouteService, and Google AI Studio.
4. **Update User-Agent**:
   - Open `running_route_recommender.py` and find the `get_coordinates` function.
   - Replace the User-Agent placeholder with your real email:
     ```python
     headers = {
         "User-Agent": "RunningRouteApp/1.0 (your_email@example.com)"  # e.g., john.doe@gmail.com
     }
     ```
   - Save the file. This complies with Nominatim’s API policy to avoid 403 errors.
5. **Clear Streamlit Cache** (optional):
   - Run in terminal:
     ```bash
     streamlit cache clear
     ```
## Running the App
1. In the terminal, navigate to the project directory:
   ```bash
   cd C:\vs_code\running_project
   ```
2. Launch the Streamlit app:
   ```bash
   python -m streamlit run GUI.py
   ```
