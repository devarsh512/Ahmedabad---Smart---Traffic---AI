# =====================================================
# Ahmedabad Smart Traffic AI
# Full City Coverage Edition
# =====================================================

# -----------------------
# ENV VARIABLES
# -----------------------

from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# -----------------------
# IMPORTS
# -----------------------

import streamlit as st
import requests
import joblib
import pandas as pd
from datetime import datetime
import plotly.express as px
import random
from streamlit_autorefresh import st_autorefresh

# -----------------------
# PAGE CONFIG
# -----------------------

st.set_page_config(
    page_title="Ahmedabad Smart Traffic AI",
    layout="wide"
)

# Auto refresh every 5 minutes
st_autorefresh(interval=300000, key="traffic_refresh")

st.title("🚦 Ahmedabad Smart Traffic Prediction System")

# -----------------------
# LOAD MODEL
# -----------------------

model = joblib.load("model/traffic_congestion_model.pkl")

# -----------------------
# WEATHER + PREDICTION
# -----------------------

def get_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Ahmedabad,IN&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        st.error("Weather API Error")
        return None

    return (
        data['main']['temp'],
        data.get('rain', {}).get('1h', 0),
        data.get('snow', {}).get('1h', 0),
        data['clouds']['all']
    )

def predict_live():
    weather = get_weather()
    if weather is None:
        return None

    temp, rain, snow, clouds = weather
    now = datetime.now()

    input_data = pd.DataFrame([{
        'temp': temp,
        'rain_1h': rain,
        'snow_1h': snow,
        'clouds_all': clouds,
        'hour': now.hour,
        'day_of_week': now.weekday(),
        'month': now.month,
        'is_weekend': 1 if now.weekday() in [5,6] else 0
    }])

    prediction = model.predict(input_data)[0]
    return prediction, temp

# -----------------------
# RUN SYSTEM
# -----------------------

result = predict_live()

if result is not None:

    prediction, temp = result

    color_map = {
        "Low": "#22c55e",
        "Medium": "#f59e0b",
        "High": "#ef4444"
    }

    # STATUS PANEL
    st.markdown(
        f"""
        <div style="
            background-color:{color_map[prediction]};
            padding:30px;
            border-radius:15px;
            text-align:center;
            color:white;
            font-size:26px;
            font-weight:700;">
            CITY TRAFFIC STATUS: {prediction}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    # -----------------------
    # COMPLETE AHMEDABAD ZONES
    # -----------------------

    zones = {

        # WEST
        "SG Highway": (23.0722, 72.5167),
        "Science City": (23.0800, 72.4940),
        "Thaltej": (23.0590, 72.5070),
        "Satellite": (23.0260, 72.5265),
        "Bopal": (23.0300, 72.4650),
        "Vastrapur": (23.0390, 72.5300),
        "Memnagar": (23.0520, 72.5330),
        "Gota": (23.0940, 72.5200),

        # CENTRAL
        "CG Road": (23.0350, 72.5600),
        "Ashram Road": (23.0422, 72.5714),
        "Navrangpura": (23.0380, 72.5630),
        "Paldi": (23.0120, 72.5660),
        "Ellisbridge": (23.0220, 72.5700),
        "Income Tax Circle": (23.0395, 72.5660),
        "Lal Darwaja": (23.0265, 72.5830),

        # EAST
        "Maninagar": (22.9967, 72.6040),
        "Naroda": (23.0685, 72.6535),
        "Odhav": (23.0190, 72.6430),
        "Bapunagar": (23.0410, 72.6260),
        "Khokhra": (23.0030, 72.6140),
        "Vastral": (23.0000, 72.6500),

        # NORTH
        "Chandkheda": (23.1070, 72.5800),
        "Motera": (23.0920, 72.5970),
        "Sabarmati": (23.0750, 72.5880),
        "Ranip": (23.0935, 72.5580),

        # SOUTH
        "Isanpur": (22.9770, 72.6000),
        "Vatva": (22.9690, 72.6350),
        "Jashoda Nagar": (22.9890, 72.6050),

        # OUTER CONNECTORS
        "Sarkhej": (22.9820, 72.4980),
        "Sanand Road": (22.9920, 72.4600),
    }

    col1, col2, col3 = st.columns(3)
    col1.metric("🌡 Temperature", f"{temp} °C")
    col2.metric("📍 Total Zones", len(zones))
    col3.metric("⏱ Updated", datetime.now().strftime("%H:%M:%S"))

    st.write("")

    # -----------------------
    # MAP DATA
    # -----------------------

    latitudes = []
    longitudes = []
    zone_names = []
    congestion_levels = []

    for zone, coords in zones.items():

        latitudes.append(coords[0])
        longitudes.append(coords[1])
        zone_names.append(zone)

        if prediction == "High":
            level = random.choices(["High", "Medium"], weights=[0.7, 0.3])[0]
        elif prediction == "Medium":
            level = random.choice(["Low", "Medium", "High"])
        else:
            level = random.choices(["Low", "Medium"], weights=[0.7, 0.3])[0]

        congestion_levels.append(level)

    df = pd.DataFrame({
        "Zone": zone_names,
        "Latitude": latitudes,
        "Longitude": longitudes,
        "Congestion": congestion_levels
    })

    size_map = {"Low": 10, "Medium": 18, "High": 25}
    df["Size"] = df["Congestion"].map(size_map)

    fig = px.scatter_mapbox(
        df,
        lat="Latitude",
        lon="Longitude",
        hover_name="Zone",
        hover_data={"Congestion": True},
        color="Congestion",
        size="Size",
        color_discrete_map=color_map,
        zoom=9,
        height=750
    )

    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox=dict(center=dict(lat=23.03, lon=72.57)),
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0)
    )

    st.plotly_chart(fig, width="stretch")

    st.markdown(
        "<div style='text-align:center;'>🟢 Low | 🟠 Medium | 🔴 High</div>",
        unsafe_allow_html=True
    )