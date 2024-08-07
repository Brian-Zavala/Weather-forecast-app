import streamlit as st
from streamlit_lottie import st_lottie
import plotly.express as px
import json
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder
import pandas as pd
from backend import get_weather, get_coordinates, collect_and_display_feedback, get_radar, create_map
import time
from streamlit_folium import folium_static

st.set_page_config(page_title="Weather App", page_icon="🌡️", layout="wide")


# Load Lottie files
def get(path: str):
    with open(path, "r") as f:
        return json.load(f)


thumbDown = get("lottie/cry.json")
thumbUp = get("lottie/confetti.json")
clear = get("lottie/clear.json")
clouds = get("lottie/cloudy.json")
rainy = get("lottie/rain.json")
snow = get("lottie/snow.json")

# Set background image
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
background-image: url("https://cdn.dribbble.com/users/1081778/screenshots/5331658/weath2.gif");
background-size: 25%;
background-position: center;
background-attachment: scroll; 
background-repeat: repeat;
}
</style>
"""

header_bg_img = """
<style>
[class="st-emotion-cache-12fmjuu ezrtsby2"] {
background-image: url("https://thekashmirhorizon.com/wp-content/uploads/Weather-Forecast.jpg");
background-position: center;
background-repeat: repeat;
background-size: 12%;

}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)
st.markdown(header_bg_img, unsafe_allow_html=True)

# Add front-end to webpage title, widgets
place = st.text_input("City Name & or State or Zip Code: ")

days = st.slider("Next 5 days", 1, 5, help="Select the day you'd like to see")

choice = st.selectbox("Select data to view", ("Temperature", "Sky-View", "Radar"))
st.write("🌦️🌧️🌞⛅🌤️🌥️🍃❄️🌨️🏂☃️🌦️🌧️🌞⛅🌤️🌥️🍃❄️🌨️🏂☃️🌦️🌧️🌞⛅🌤️🌥️🍃❄️🌨️🏂☃️🌦️🌧️🌞⛅🌤️🌥️🍃❄️🌨️🏂☃️🌦️🌧️🌞⛅🌤️🌥️")
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
            humidity = [dict["main"]["humidity"] for dict in filtered_data_weather]
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
            df_date = date
            df_humidity = humidity
            data = pd.DataFrame({"Time/Date": df_date, "Humidity %": df_humidity})

            st.bar_chart(data=data, x="Time/Date", y="Humidity %", horizontal=True, color=(0, 170, 255),
                         use_container_width=True, x_label="Humidity %", y_label="Time")

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
                        st_lottie(images[info['condition']], height=200, key=f"lottie_{i}")
                        if "Clear" in info['condition'] and "Clear" in images:
                            st.audio("Clear.mp3", format="audio/mpeg",
                                     start_time=0, end_time=1, loop=False, autoplay=True)
                        if "Rain" in info['condition'] and "Rain" in images:
                            st.audio("Rain.mp3", format="audio/mpeg",
                                     start_time=0, end_time=1, loop=False, autoplay=True)
                        if "Clouds" in info["condition"] and "Clouds" in images:
                            st.audio("Clouds.mp3", format="audio/mpeg",
                                     start_time=0, end_time=1, loop=False, autoplay=True)
                        if "Snow" in info['condition'] and "Snow" in images:
                            st.audio("Snow.mp3", format="audio/mpeg",
                                     start_time=0, end_time=1, loop=False, autoplay=True)

                    else:
                        st.write(f"No animation for {info['condition']}")



        def find_closest_time(target_time, time_list):
            return min(time_list, key=lambda x: abs(x - target_time))


        if choice == "Radar":
            # Fetch radar data
            radar_data = get_radar()
            if not radar_data or 'radar' not in radar_data or 'past' not in radar_data['radar']:
                st.error("Unable to fetch radar data. The radar service might be temporarily unavailable.")
            else:
                st.header("Doppler Radar")
                past_frames = radar_data['radar']['past']

                if not past_frames:
                    st.warning("No past radar data available for the selected location.")
                else:
                    # Initialize session state
                    if 'playing' not in st.session_state:
                        st.session_state.playing = False
                    if 'current_frame_index' not in st.session_state:
                        st.session_state.current_frame_index = 0


                    # Function to get weather data for a specific time
                    def get_weather_for_time(target_time):
                        return min(filtered_data_weather,
                                   key=lambda x: abs(datetime.strptime(x['dt_txt'], "%Y-%m-%d %H:%M:%S") - target_time))


                    # Function to update map and weather information
                    def update_map_and_info():
                        current_frame = past_frames[st.session_state.current_frame_index]
                        m = create_map(radar_data, current_frame, "past", place)
                        with map_placeholder.container():
                            folium_static(m)

                        frame_time = datetime.fromtimestamp(current_frame['time'])
                        time_display.write(f"Current frame time: {frame_time.strftime('%I:%M %p')}")

                        # Get and display weather information
                        weather_data = get_weather_for_time(frame_time)
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric(value=weather_data['main']['temp'],label="Temperature F°")
                        with col2:
                            st.metric(value=weather_data['main']['humidity'],label="Humidity %")
                        with col3:
                            st.metric(value=weather_data['wind']['speed'],label="Wind Speed MPH")
                        with col4:
                            st.metric(value=weather_data['wind']['deg'],label="Wind Direction")

                    # Function to toggle play/pause
                    def toggle_play():
                        st.session_state.playing = not st.session_state.playing


                    # Create play/pause button
                    st.button("Play/Pause", on_click=toggle_play)

                    # Create map, time display, and weather info placeholders
                    map_placeholder = st.empty()
                    time_display = st.empty()
                    weather_info = st.empty()
                    status_display = st.empty()

                    # Initial map and info update
                    update_map_and_info()


                    # Custom callback to update the map and weather info
                    def custom_callback():
                        while st.session_state.playing:
                            st.session_state.current_frame_index = (st.session_state.current_frame_index + 1) % len(
                                past_frames)
                            update_map_and_info()
                            status_display.write("Status: Playing")
                            time.sleep(1.29)  # Wait for 1.29 seconds before next update
                        status_display.write("Status: Paused")


                    # Use st.empty() to create a container for the custom callback
                    callback_placeholder = st.empty()

                    # Run the custom callback if playing
                    if st.session_state.playing:
                        callback_placeholder.markdown("Animation running...")
                        custom_callback()
                    else:
                        callback_placeholder.markdown("Animation paused.")


    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

    # Add the feedback system
collect_and_display_feedback()
