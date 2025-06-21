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
   streamlit run GUI.py
   ```
3. Open the provided URL (e.g., `http://localhost:8501`) in your browser.

## Usage
1. **Enter Preferences**:
   - In the sidebar, input your location (e.g., “Paris, France”), distance (e.g., 5 km), pace (e.g., 6 min/km), and check “Check weather?” if desired.
2. **Find Routes**:
   - Click “Find Running Routes” to display routes, a map, estimated run time, and weather.
3. **Manage Routes**:
   - Save routes to “Favorites” by clicking “Save to Favorites”.
   - Export routes as a CSV file using “Export Routes as CSV”.
4. **Get Tips**:
   - Use the Gemini chatbot to ask questions like “How can I improve my running form?” or “What should I eat before a run?”.

## Troubleshooting
- **HTTP 403 Error (Map Unavailable)**:
  - Ensure the User-Agent in `running_route_recommender.py` uses your real email.
  - Clear cache: `streamlit cache clear`.
  - Wait a minute and retry to avoid Nominatim rate limits (1 request/second).
- **API Key Errors**:
  - Verify `secrets.toml` contains valid keys.
- **No Routes Found**:
  - Check your internet connection and Tavily API key.
- **Chatbot Issues**:
  - Ensure the Gemini API key is valid and within the free tier limit (1,500 requests/day).

## License
MIT License

Copyright (c) 2025 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.