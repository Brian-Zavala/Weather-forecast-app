import streamlit as st
from streamlit_lottie import st_lottie
import plotly.express as px
import json
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder
import pandas as pd

# Import the functions from the provided backend code
from backend import get_weather, get_coordinates, collect_and_display_feedback

st.set_page_config(layout="wide")


# Load Lottie files
def get(path: str):
    with open(path, "r") as f:
        return json.load(f)


thumbDown = get("lottie/thumbs_down.json")
thumbUp = get("lottie/thumbs_up.json")
clear = get("lottie/clear.json")
clouds = get("lottie/cloudy.json")
rainy = get("lottie/rain.json")
snow = get("lottie/snow.json")

# Set background image
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
background-image: url("https://cdn.dribbble.com/users/1081778/screenshots/5331658/weath2.gif");
background-size: 34%;
background-position: center;
background-attachment: local; 
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# Add front-end to webpage title, widgets
st.title("5-Day Weather Forecast")

place = st.text_input("City Name & or State or Zip Code: ")

days = st.slider("Next 5 days", 1, 5, help="Select the day you'd like to see")

choice = st.selectbox("Select data to view", ("Temperature", "Sky-View", "Map"))

st.subheader(f"{choice} for the next {days} day(s) in {place}")

if place:
    try:
        # Fetch weather data and coordinates
        filtered_data_weather = get_weather(place, days)
        lat, lon = get_coordinates(place)

        # Get the timezone for the given coordinates
        tf = TimezoneFinder()
        timezone_str = tf.certain_timezone_at(lat=lat, lng=lon)
        local_tz = pytz.timezone(timezone_str)

        if choice == "Temperature":
            temperature = [dict["main"]["temp"] for dict in filtered_data_weather]
            date = []

            for dict in filtered_data_weather:
                # Parse the UTC time
                utc_time = datetime.strptime(dict["dt_txt"], "%Y-%m-%d %H:%M:%S")
                utc_time = utc_time.replace(tzinfo=pytz.UTC)
                # Convert to local time
                local_time = utc_time.astimezone(local_tz)
                fixed_time = local_time.strftime("%m-%d  -   %I:%M %p")
                date.append(fixed_time)

            # Create a temperature line graph
            figure = px.line(x=date, y=temperature, labels={"x": "Date",
                                                            "y": "Temperature (F))"})

            figure.update_layout(
                hovermode="y",
                xaxis_title=f"Date (Local Time - {timezone_str})",
                yaxis_title="Temperature (°F)",
                xaxis_tickangle=-45  # Rotate x-axis labels for readability
            )

            st.plotly_chart(figure, use_container_width=True, theme="streamlit")

        if choice == "Sky-View":
            images = {"Clear": clear, "Clouds": clouds, "Rain": rainy, "Snow": snow}
            # Group the data by day
            daily_conditions = {}
            for data_point in filtered_data_weather:
                utc_time = datetime.strptime(data_point["dt_txt"], "%Y-%m-%d %H:%M:%S")
                utc_time = utc_time.replace(tzinfo=pytz.UTC)
                local_time = utc_time.astimezone(local_tz)
                date = local_time.strftime("%Y-%m-%d")
                time = local_time.strftime("%I:%M %p")
                temperature = data_point["main"]["temp"]
                condition = data_point["weather"][0]["main"]
                if date not in daily_conditions:
                    daily_conditions[date] = {"condition": condition, "time": time, "temperature": temperature}

            # Create columns for each day
            cols = st.columns(len(daily_conditions))

            # Display the weather condition for each day
            for i, (date, info) in enumerate(daily_conditions.items()):
                with cols[i]:
                    st.write(f"{date} | {info['time']} ({timezone_str})")
                    st.write(info["condition"])
                    st.write(f"{info['temperature']}°F")

                    if info['condition'] in images:
                        st_lottie(images[info['condition']], height=175, key=f"lottie_{i}")
                    else:
                        st.write(f"No animation for {info['condition']}")

        if choice == "Map":
            map_data = pd.DataFrame({'lat': [lat], 'lon': [lon]})
            st.map(map_data, color="#42a5f5", size=200)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Add the feedback system
collect_and_display_feedback()
