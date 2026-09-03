import os
import json
from typing import Any, Dict

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

WEATHERSTACK_API_KEY = os.getenv("WEATHERSTACK_API_KEY")


def fetch_weather_details(city_name: str) -> Dict[str, Any]:
    """Fetch weather details for a city and save the API response as JSON."""
    city_name = (city_name or "").strip()

    if not city_name:
        return {"error": "Please enter a city name."}

    if not WEATHERSTACK_API_KEY:
        return {"error": "Missing WEATHERSTACK_API_KEY in your .env file."}

    url = "http://api.weatherstack.com/current"
    params = {
        "access_key": WEATHERSTACK_API_KEY,
        "query": city_name,
    }

    try:
        response = requests.get(url, params=params, timeout=20)
        data = response.json()

        with open("weather_response.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

        if response.status_code != 200 or "current" not in data or "location" not in data:
            return {"error": f"Could not fetch data for the city: {city_name}"}

        current = data.get("current", {})
        location = data.get("location", {})

        return {
            "city": location.get("name", city_name),
            "country": location.get("country", "N/A"),
            "region": location.get("region", "N/A"),
            "temperature": current.get("temperature", "N/A"),
            "weather_description": current.get("weather_descriptions", ["N/A"])[0],
            "humidity": current.get("humidity", "N/A"),
            "raw": data,
        }
    except requests.RequestException:
        return {"error": f"Could not fetch data for the city: {city_name}"}


st.set_page_config(page_title="Weather Dashboard", page_icon="☀️", layout="wide")

st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 60%, #38bdf8 100%);
            color: white;
        }
        .block-container {
            padding-top: 2rem;
        }
        div[data-testid="stMetricValue"] {
            color: white;
            font-size: 2rem;
        }
        .stTextInput > div > div > input {
            color: black !important;
            background: white !important;
        }
        .stButton > button {
            background: linear-gradient(135deg, #38bdf8 0%, #2563eb 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            padding: 0.7rem 1.3rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("☀️ Subhanshu - Jain Weather Predictor")
st.subheader("Enter a city name and get the live weather")

city = st.text_input("City name", placeholder="Example: London, Delhi, Paris")

if st.button("Get Weather", use_container_width=True):
    result = fetch_weather_details(city)

    if "error" in result:
        st.error(result["error"])
    else:
        st.markdown(f"## {result['city']}, {result['country']}")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Temperature", f"{result['temperature']}°C")
        with col2:
            st.metric("Humidity", f"{result['humidity']}%")
        with col3:
            st.metric("Region", result["region"])
        with col4:
            st.metric("Condition", result["weather_description"].title())

        st.write(f"Weather description: {result['weather_description']}")
        st.write(f"City: {result['city']}")
        st.write(f"Country: {result['country']}")
        st.write(f"Region: {result['region']}")

        with st.expander("View full JSON response"):
            st.json(result["raw"])

