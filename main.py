import streamlit as st
from streamlit_lottie import st_lottie
import json
from datetime import datetime, timedelta
import pytz
from timezonefinder import TimezoneFinder
import pandas as pd
from backend import (get_weather, get_weather_for_day, get_weather_for_night, get_coordinates, collect_and_display_feedback,
                     get_radar, create_map)
import time
from streamlit_folium import folium_static
from plotly.subplots import make_subplots
import plotly.graph_objects as go

st.set_page_config(page_title="Weather App", page_icon="🌡️", layout="wide", initial_sidebar_state="auto")


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
[data-testid="stAppViewContainer"] > .main {
background-image: url("https://cdn.dribbble.com/users/1081778/screenshots/5331658/weath2.gif");
background-size: 25%;
background-position: center;
background-attachment: local; 
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
background-size: 15%;
background-attachment: local; 


}
</style>
"""
st.markdown("""
<style>
.stAudio {
    display: none;
}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
[class="st-emotion-cache-1vzeuhh ew7r33m3"] {
background-color: Gold;
}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
[class="st-at st-av st-aw st-au st-c6 st-c7 st-ah st-c8 st-c9"] {
background-color: DeepSkyBlue;
border-radius: 20 px
}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style> 
div.st-emotion-cache-1whx7iy p {
color: Black;
font-family: "Gerogia", serif;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
[class="eyeqlp53 st-emotion-cache-1pbsqtx ex0cdmw0"] {
display: none;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
        <style>
               .block-container {
                    padding-top: 0rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)
st.markdown("""
<style>
div.st-emotion-cache-1gwvy71 {
background-image: url("https://media.gettyimages.com/id/1255467655/photo/lightning-strikes-and-severe-weather-on-the-great-plains.jpg?s=612x612&w=0&k=20&c=fwozMFiGpnBhmK5Lh-l-hus3NTDl43hySIlIQlwsGfY=");
background-size: cover;
background-repeat: no-repeat;

}
div.st-emotion-cache-1wivap2{

color: White;
white-space: normal;
line-height: 33.5px;
text-overflow: clip;
overflow: visible;
margin-top: 0px;

}
div.st-emotion-cache-1whx7iy p {
color: Snow;
font-size: 30px;
}
.st-emotion-cache-1mi2ry5 {
background-image: url("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTaQZXiwxn2YTOc_gUOy8byb2IPAQBZCFSP3w&s");
background-size: 100%;
display: flex;

}
</style>
""", unsafe_allow_html=True)

st.markdown(page_bg_img, unsafe_allow_html=True)
st.markdown(header_bg_img, unsafe_allow_html=True)

# Add front-end to webpage title, widgets
place = st.text_input("🏠 City, State or Zip Code ", placeholder="Enter... ")

days = st.slider("5 day forecast", 1, 6, help="Select the day you'd like to see")
if days:
    with st.spinner(text="Loading Day..."):
        time.sleep(1)




selection = st.selectbox("🌞 Select data to view", ("Temperature", "Sky-View", "Radar"))

st.subheader(f"{selection} for {place} | {(datetime.now() + timedelta(days=days - 1)).strftime('%Y-%m-%d')}")

if place:
    try:
        # Fetch weather data and coordinates
        filtered_data_weather = get_weather(place, days)
        lat, lon = get_coordinates(place)

        day_weather = get_weather_for_day(filtered_data_weather, days)
        night_weather = get_weather_for_night(filtered_data_weather, days)

        with st.sidebar:

            if day_weather and night_weather:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        label="Today's High °F",
                        value=f"{day_weather['main']['temp']:.1f}°F",
                        delta=f"Real Feel {day_weather['main']['temp'] +
                                           day_weather['main']['feels_like'] -
                                           day_weather['main']['temp']:.1f}°F",
                        delta_color="inverse"
                    )

                    st.metric(
                        label="Today's Low °F",
                        value=f"{night_weather['main']['temp']:.1f}°F",
                        delta=f"Real Feel {night_weather['main']['temp'] +
                                           night_weather['main']['feels_like'] -
                                           night_weather['main']['temp']:.1f}°F",
                        delta_color="inverse"
                    )
                    st.metric(
                        label="Humidity",
                        value=f"{day_weather['main']['humidity']}%"
                    )
                with col2:

                    st.metric(
                        label="Wind Speed",
                        value=f"{day_weather['wind']['speed']:.1f} MPH",
                        delta=f"Wind Gust {day_weather['wind']['speed'] +
                                           day_weather['wind']['gust']:.1f} MPH",
                        delta_color="inverse"
                    )

                    st.metric(
                        label="Sky",
                        value=f"{day_weather['weather'][0]["description"]}")

        # Get the timezone for the given coordinates
        tf = TimezoneFinder()
        timezone_str = tf.certain_timezone_at(lat=lat, lng=lon)
        local_tz = pytz.timezone(timezone_str)

        if selection == "Temperature":
            temperature = [dict["main"]["temp"] for dict in filtered_data_weather]
            humidity = [dict["main"]["humidity"] for dict in filtered_data_weather]
            wind = [dict["wind"]["speed"] for dict in filtered_data_weather]
            real_feel = [dict["main"]["feels_like"] for dict in filtered_data_weather]
            date = []
            chart_data = []
            for dict in filtered_data_weather:
                # Parse the UTC time
                utc_time = datetime.strptime(dict["dt_txt"], "%Y-%m-%d %H:%M:%S")
                utc_time = utc_time.replace(tzinfo=pytz.UTC)
                # Convert to local time
                local_time = utc_time.astimezone(local_tz)
                fixed_time = local_time.strftime("%m-%d  -   %I:%M %p")
                date.append(fixed_time)

                chart_data.append({
                    "Time/Date": local_time.strftime("%m-%d %I:%M %p"),
                    "Temperature": dict["main"]["temp"],
                    "Real Feel": dict["main"]["feels_like"]
                })

            col6, col7 = st.columns([2, 2])

            with col6:
                df = pd.DataFrame(chart_data)  # Create a temperature line graph
                fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                                    subplot_titles=("Temperature", "Real Feel Temperature"))

                fig.add_trace(
                    go.Scatter(x=df["Time/Date"], y=df["Temperature"], name="Temperature", mode="lines"),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=df["Time/Date"], y=df["Real Feel"], name="Real Feel", mode="lines"),
                    row=1, col=1
                )
                fig.update_layout(
                    height=350,  # Adjust the height as needed
                    hovermode="x unified",
                    xaxis_title=f"Date (Local Time - {timezone_str})",
                    xaxis_tickangle=-45,
                )

                fig.update_yaxes(title_text="Temperature °F", row=1, col=1)
                fig.update_yaxes(title_text="Real Feel °F", row=1, col=1)

                st.plotly_chart(fig, use_container_width=True, theme="streamlit")

            with col7:
                humidity_data = pd.DataFrame({"Time/Date": date, "Humidity %": humidity, "Wind Speed MPH": wind})

                st.area_chart(data=humidity_data, x="Time/Date", y=["Humidity %", "Wind Speed MPH"],
                              use_container_width=True)

            st.audio("summer_music.mp3", start_time=131, autoplay=True, format="audio/mpeg")
            pass

        if selection == "Sky-View":
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
                                     start_time=0, end_time=30, loop=True, autoplay=True)
                        elif "Rain" in info['condition'] and "Rain" in images:
                            st.audio("Rain.wav", format="audio/wav",
                                     start_time=0, end_time=30, loop=True, autoplay=True)
                        elif "Clouds" in info["condition"] and "Clouds" in images:
                            st.audio("Clouds.wav", format="audio/wav",
                                     start_time=0, end_time=30, loop=True, autoplay=True)
                        elif "Snow" in info['condition'] and "Snow" in images:
                            st.audio("Snow.mp3", format="audio/mpeg",
                                     start_time=0, end_time=30, loop=True, autoplay=True)

                    else:
                        st.write(f"No animation for {info['condition']}")


        def find_closest_time(target_time, time_list):
            return min(time_list, key=lambda x: abs(x - target_time))


        if selection == "Radar":
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
                            st.audio("ping.mp3", start_time=0, loop=True, autoplay=True, format="audio/mpeg")


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
with (st.expander(label="Click Me!", expanded=False, icon="🌤️")):
    collect_and_display_feedback()
    col1, col2, col3, col4 = st.columns([1, 2, 1.2, 0.8], gap="medium")
    with col4:
        st.write("")
        st.write("→Creator←")
        st.image("QuadFather.jpg", width=110)
        st.write("Brian Zavala")

st.markdown("""
<style>
[data-testid="stMarkdownContainer"] {
font-family: Comic Sans MS, Comic Sans, bold;
color: White;
}  
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
[class="st-emotion-cache-187vdiz e1nzilvr4"] {
font-family: Comic Sans MS, Comic Sans, bold;
color: Black;
}  
</style>
""", unsafe_allow_html=True)
