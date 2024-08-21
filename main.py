import streamlit as st
import streamlit.components.v1 as components

from streamlit_lottie import st_lottie
import json
from datetime import datetime, timedelta
import pytz
from timezonefinder import TimezoneFinder
import pandas as pd
from backend import (get_weather, get_weather_for_day, get_weather_for_night, get_coordinates,
                     collect_and_display_feedback,
                     get_radar, create_map, parse_datetime)
import time
from streamlit_folium import folium_static
from plotly.subplots import make_subplots
import plotly.graph_objects as go

st.set_page_config(page_title="Weather App", page_icon="🌡️", layout="wide", initial_sidebar_state="expanded")
st.cache_data.clear()


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

st.markdown("""
<style>
@media (max-width: 600px) {
    .stApp {
        padding: 0;
    }
    .stSidebar {
        width: 100%;
        max-width: none;
    }
}
</style>
""", unsafe_allow_html=True)

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
background-color: red;
border-radius: 20 px
}
h3 {
color: Black;
}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style> 
div.st-emotion-cache-1whx7iy p {
color: Black;
font-family: "New Century Schoolbook", "TeX Gyre Schola", serif;
font-weight: 675px;
}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style> 


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
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)

st.markdown("""
       <style>
       div.st-emotion-cache-1mi2ry5 {
       background-image: url("{st.session_state.background_image}");
       background-size: cover;
       background-position: center;
       background-repeat: no-repeat;

       }
       div.st-emotion-cache-1wivap2{
       color: #F40009;
       font-weight: 650px;
       white-space: normal;
       line-height: 41.5px;
       text-overflow: clip;
       overflow: visible;
       margin-top: 0px;
       }
       div.st-emotion-cache-1whx7iy p {
       color: Black;
       font-size: 30px;
       font-weight: 675px;

       }
       .st-emotion-cache-1gwvy71 {
       background-image: url("{st.session_state.background_image}");
       background-size: cover;
       background-repeat: no-repeat;
       display: flex;
       }

       [class="eyeqlp53 st-emotion-cache-1f3w014 ex0cdmw0"] {
       color: red;
       font-weight: 500px;
       }
       </style>
       """, unsafe_allow_html=True)


def get_background_image(weather_condition):
    condition = weather_condition.lower()
    if "clear" in condition:
        return ("https://images.unsplash.com/photo-1601297183305-6df142704ea2?w=1600&auto=format&fit=crop&q=60&ixlib"
                "=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8Y2xlYXIlMjBza3l8ZW58MHx8MHx8fDA%3D")
    elif "cloud" in condition:
        return ("https://images.unsplash.com/photo-1534088568595-a066f410bcda?w=1600&auto=format&fit=crop&q=60&ixlib"
                "=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8Y2xvdWR5JTIwc2t5fGVufDB8fDB8fHww")
    elif "rain" in condition:
        return ("https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?w=1600&auto=format&fit=crop&q=60&ixlib"
                "=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8cmFpbnklMjBza3l8ZW58MHx8MHx8fDA%3D")
    elif "snow" in condition:
        return ("https://images.unsplash.com/photo-1547754980-3df97fed72a8?w=1600&auto=format&fit=crop&q=60&ixlib=rb-4"
                ".0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8c25vd3klMjBza3l8ZW58MHx8MHx8fDA%3D")
    else:
        return "https://cdn.dribbble.com/users/1081778/screenshots/5331658/weath2.gif"


DEFAULT_BACKGROUND = ("https://media4.giphy.com/media/2tNvsKkc0qFdNhJmKk/giphy.gif?cid"
                      "=6c09b952xrvybbti8zhka3kfc4du1li0vbw77ds2vi0ro993&ep=v1_gifs_search&rid=giphy.gif&ct=g")

# Add front-end to webpage title, widgets
# Initialize session state
if 'days' not in st.session_state:
    st.session_state.days = 1
if 'weather_data' not in st.session_state:
    st.session_state.weather_data = None
if 'background_image' not in st.session_state:
    st.session_state.background_image = DEFAULT_BACKGROUND


def filter_data_for_day(data, day):
    target_date = (datetime.now(pytz.timezone("America/Chicago")).astimezone() +
                   timedelta(days=day - 1)).date()
    return [d for d in data if parse_datetime(d['dt_txt']).date() == target_date]


def update_days_main():
    st.session_state.days = st.session_state.main_slider_days


def update_days_sidebar():
    st.session_state.days = st.session_state.sidebar_slider_days


# Set initial background
st.markdown(f"""
<style>
.stApp {{
    background-image: url("{st.session_state.background_image}");
    background-size: cover;
    back-ground-position: center;
    background-repeat: no-repeat;
}}
.st-emotion-cache-18ni7ap {{
    background-image: url("{st.session_state.background_image}");
    background-size: cover;
}}
</style>
""", unsafe_allow_html=True)

current_time = st.empty
# JavaScript to update time
js_code = """
<div id="current_time"></div>
<script>
function updateTime() {
    var now = new Date();
    var options = { timeZone: 'America/Chicago',
    hour: '2-digit', minute: '2-digit', second: '2-digit' };
    var formattedTime = now.toLocaleString('en-US', options);
    document.getElementById('current_time').innerHTML = 'Time: ' + formattedTime;
}
updateTime();
setInterval(updateTime, 1000);
</script>
"""

# Add front-end to webpage title, widgets
place = st.text_input("🏠 Location", placeholder="Enter City...")

# Main page slider
days = st.slider("5 day forecast", 1, 5,
                 key="main_slider_days",
                 value=st.session_state.days,
                 on_change=update_days_main,
                 help="Select the day you'd like to see")

selection = st.selectbox("🌞 Metric Data", ("Temperature", "Sky-View", "Radar"))

selected_date = (datetime.now(pytz.timezone("America/Chicago")).astimezone() +
                 timedelta(days=st.session_state.days - 1))

st.subheader(f"{selection} for {place} | {selected_date.strftime('%A''\n''%Y-%m-%d')}")

if place:
    try:
        # Fetch weather data and coordinates
        all_weather_data = get_weather(place, days=5)
        filtered_data_weather = filter_data_for_day(all_weather_data, st.session_state.days)
        lat, lon = get_coordinates(place)

        day_weather = get_weather_for_day(all_weather_data, st.session_state.days)
        night_weather = get_weather_for_night(all_weather_data, st.session_state.days)

        # Update background image based on weather condition
        if day_weather:
            weather_condition = day_weather['weather'][0]['description']
            st.session_state.background_image = get_background_image(weather_condition)
            # Set background image
            st.markdown(f"""
            <style>
            .stApp {{
                background-image: url("{st.session_state.background_image}");
                background-size: cover;
                background-attachment: scroll; 
            }}
            [class="st-emotion-cache-12fmjuu ezrtsby2"] {{
             background-image: url("{st.session_state.background_image}");
             background-size: cover;
             background-position: center;
             background-repeat: no-repeat;
            }}
            
            .st-emotion-cache-1gwvy71 {{
            background-image: url("{st.session_state.background_image}");
            background-size: cover;
            }}
            div.st-emotion-cache-1mi2ry5 {{
            background-image: url("https://data.textstudio.com/output/sample/animated/4/0/3/6/temperature-10-16304.gif");
            background-size: cover;
            background-position: ;
            background-repeat: repeat;

            }}
            """, unsafe_allow_html=True)

            with st.sidebar:
                components.html(js_code, height=50)
                st.sidebar.header(f"{selected_date.strftime('%A''\n''%Y-%m-%d')}")

                st.slider(" 5 Day Forecast ", 1, 5,
                          key="sidebar_slider_days",
                          value=st.session_state.days,
                          on_change=update_days_sidebar,
                          help="Select the day")

                if day_weather and night_weather:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(
                            value=f"{day_weather['main']['temp']:.1f}°F",
                            label="Day High °F",
                            delta=f"Real Feel {day_weather['main']['temp'] +
                                               day_weather['main']['feels_like'] -
                                               day_weather['main']['temp']:.1f}°F",
                            delta_color="inverse"
                        )

                        st.metric(
                            label="Day Low °F",
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
                            value=f"{day_weather['weather'][0]['description']}"
                        )

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
                local_time = parse_datetime(dict["dt_txt"])
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

        if selection == "Sky-View":
            images = {"Clear": clear, "Clouds": clouds, "Rain": rainy, "Snow": snow}

            # Use the filtered data for the selected day
            if filtered_data_weather:
                # Group the data by day
                daily_conditions = {}
                for data_point in filtered_data_weather:
                    local_time = parse_datetime(data_point["dt_txt"])
                    date = local_time.date()
                    if date not in daily_conditions:
                        daily_conditions[date] = {
                            "condition": data_point["weather"][0]["main"],
                            "time": local_time.strftime("%I:%M %p"),
                            "temperature": data_point["main"]["temp"]
                        }

                # Display the weather condition for each day
                for date, info in daily_conditions.items():
                    st.write(f"{date.strftime('%Y-%m-%d')} | {info['time']} ({timezone_str})")
                    st.write(info["condition"])
                    st.write(f"{info['temperature']}°F")

                    if info['condition'] in images:
                        st_lottie(images[info['condition']], height=200, key=f"lottie_{st.session_state.days}")
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
                else:
                    st.write("No weather data available for the selected day.")


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
                        get_weather_for_time(frame_time)


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
                        st.audio("ping.mp3", start_time=0, loop=True, autoplay=True, format="audio/mpeg")

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
    except KeyError:
        st.write("This place does not exist")

# Add the feedback system
with (st.expander(label="Click Me!", expanded=False, icon="🌤️")):
    collect_and_display_feedback()
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1], gap="large")
    with col1 and col2:
        image = st.camera_input("Leave A Snap!")
    with col3 and col4:
        st.write("")
        st.write("→Creator←")
        st.image("QuadFather.jpg", width=100)
        st.write("Brian Zavala")

st.markdown("""
<style>
[data-testid="stMarkdownContainer"] {
font-family: Comic Sans MS, Comic Sans, bold;
color: red;
}  
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
[class="st-emotion-cache-187vdiz e1nzilvr4"] {
font-family: Comic Sans MS, Comic Sans, bold;
color: red;
}  
</style>
""", unsafe_allow_html=True)
