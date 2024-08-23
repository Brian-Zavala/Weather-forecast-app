import streamlit as st
import streamlit.components.v1 as components
from streamlit_lottie import st_lottie
import json
from datetime import datetime, timedelta
import pytz
from timezonefinder import TimezoneFinder
import pandas as pd
from backend import (get_weather, get_weather_for_day, get_weather_for_night, get_coordinates,
                     collect_and_display_feedback, create_additional_weather_conditions_chart,
                     get_radar, create_map, parse_api_datetime)
import time
from streamlit_folium import folium_static

st.set_page_config(page_title="Weather App", page_icon="🌡️", layout="wide", initial_sidebar_state="expanded")
st.cache_data.clear()

st.markdown("""
<style>
.clock-container {
    position: fixed;
    top: 10px;
    right: 10px;
    z-index: 1000;
}
</style>
""", unsafe_allow_html=True)
# Create a container for the clock
clock_container = st.container()


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
       .st-emotion-cache-1gwvy71 h2 {
       background-image: url("{st.session_state.background_image}");
       background-size: cover;
       background-repeat: no-repeat;
       color: red;
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

    # Clear skies
    if "clear" in condition:
        return ("https://images.unsplash.com/photo-1601297183305-6df142704ea2?w=1600&auto=format&fit=crop&q=60&ixlib"
                "=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8Y2xlYXIlMjBza3l8ZW58MHx8MHx8fDA%3D")
    # Cloudy conditions
    elif "broken clouds" in condition:
        return ("https://images.unsplash.com/photo-1501630834273-4b5604d2ee31?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid"
                "=M3wxMjA3fDB8MHxzZWFyY2h8M3x8b3ZlcmNhc3QlMjBza3l8ZW58MHx8MHx8fDA%3D")
    elif "scattered clouds" in condition:
        return ("https://img.freepik.com/free-photo/blue-sky-with-windy-clouds-vertical-shot_23-2148824938.jpg?t=st"
                "=1724337516~exp=1724341116~hmac=901fcc704543ef6fb3a62a22198891f8fbfe4e77456f814737827f9496f4bd35&w"
                "=740")
    elif "few clouds" in condition:
        return ("https://images.unsplash.com/photo-1601297183305-6df142704ea2?w=1600&auto=format&fit=crop&q=60&ixlib"
                "=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8Y2xlYXIlMjBza3l8ZW58MHx8MHx8fDA%3D")
    elif "overcast" in condition:
        return ("https://images.unsplash.com/photo-1594156596782-656c93e4d504?w=1600&auto=format&fit=crop&q=60&ixlib"
                "=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8YnJva2VuJTIwY2xvdWRzfGVufDB8fDB8fHww")
    elif "cloud" in condition:
        return ("https://images.unsplash.com/photo-1534088568595-a066f410bcda?w=1600&auto=format&fit=crop&q=60&ixlib"
                "=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8Y2xvdWR5JTIwc2t5fGVufDB8fDB8fHww")

    # Rainy conditions
    elif "light rain" in condition:
        return ("https://images.unsplash.com/photo-1438449805896-28a666819a20?w=1600&auto=format&fit=crop&q=60&ixlib"
                "=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8bGlnaHQlMjByYWlufGVufDB8fDB8fHww")
    elif "moderate rain" in condition:
        return ("https://images.unsplash.com/photo-1519692933481-e162a57d6721?w=1600&auto=format&fit=crop&q=60&ixlib"
                "=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8bW9kZXJhdGUlMjByYWlufGVufDB8fDB8fHww")
    elif "heavy rain" in condition:
        return ("https://images.unsplash.com/photo-1620385019253-b051a26048ce?w=1600&auto=format&fit=crop&q=60&ixlib"
                "=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8aGVhdnklMjByYWlufGVufDB8fDB8fHww")
    elif "rain" in condition:
        return ("https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?w=1600&auto=format&fit=crop&q=60&ixlib"
                "=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8cmFpbnklMjBza3l8ZW58MHx8MHx8fDA%3D")

    # Thunderstorm conditions
    elif "thunderstorm" in condition:
        return ("https://images.unsplash.com/photo-1605727216801-e27ce1d0cc28?w=1600&auto=format&fit=crop&q=60&ixlib"
                "=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8dGh1bmRlcnN0b3JtfGVufDB8fDB8fHww")

    # Snowy conditions
    elif "light snow" in condition:
        return ("https://images.unsplash.com/photo-1542601098-8fc114e148e2?w=1600&auto=format&fit=crop&q=60&ixlib=rb-4"
                ".0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8bGlnaHQlMjBzbm93fGVufDB8fDB8fHww")
    elif "heavy snow" in condition:
        return ("https://images.unsplash.com/photo-1517299321609-52687d1bc55a?w=1600&auto=format&fit=crop&q=60&ixlib"
                "=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8aGVhdnklMjBzbm93fGVufDB8fDB8fHww")
    elif "snow" in condition:
        return ("https://images.unsplash.com/photo-1547754980-3df97fed72a8?w=1600&auto=format&fit=crop&q=60&ixlib=rb-4"
                ".0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8c25vd3klMjBza3l8ZW58MHx8MHx8fDA%3D")

    # Misty or foggy conditions
    elif "mist" in condition or "fog" in condition:
        return ("https://images.unsplash.com/photo-1543968996-ee822b8176ba?w=1600&auto=format&fit=crop&q=60&ixlib=rb-4"
                ".0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8bWlzdHl8ZW58MHx8MHx8fDA%3D")

    # Hazy conditions
    elif "haze" in condition:
        return ("https://w0.peakpx.com/wallpaper/1022/864/HD-wallpaper-2-person-walking-on-pathway-between-trees"
                "-during-foggy-weather.jpg")

    # Default image for any other condition
    else:
        return ("https://media4.giphy.com/media/2tNvsKkc0qFdNhJmKk/giphy.gif?cid"
                "=6c09b952xrvybbti8zhka3kfc4du1li0vbw77ds2vi0ro993&ep=v1_gifs_search&rid=giphy.gif&ct=g")


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

# JavaScript to update time
js_code = """<div id="clock-container">
  <div id="analog-clock">
    <div class="hand hour-hand"></div>
    <div class="hand minute-hand"></div>
    <div class="hand second-hand"></div>
    <div class="center-dot"></div>
    <div class="number number1">1</div>
    <div class="number number2">2</div>
    <div class="number number3">3</div>
    <div class="number number4">4</div>
    <div class="number number5">5</div>
    <div class="number number6">6</div>
    <div class="number number7">7</div>
    <div class="number number8">8</div>
    <div class="number number9">9</div>
    <div class="number number10">10</div>
    <div class="number number11">11</div>
    <div class="number number12">12</div>
  </div>
  <div id="digital-clock"></div>
</div>

<style>
#clock-container {
  width: 200px;
  height: 250px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  backdrop-filter: blur(5px);
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: 20px auto;
}

#analog-clock {
  width: 150px;
  height: 150px;
  border: 2px solid #333;
  border-radius: 50%;
  position: relative;
  background: white;
}

.hand {
  position: absolute;
  bottom: 50%;
  left: 50%;
  transform-origin: 50% 100%;
  border-radius: 5px;
}

.hour-hand {
  width: 6px;
  height: 40px;
  background: #333;
}

.minute-hand {
  width: 4px;
  height: 60px;
  background: #666;
}

.second-hand {
  width: 2px;
  height: 70px;
  background: #f00;
}

.center-dot {
  width: 12px;
  height: 12px;
  background: #333;
  border-radius: 50%;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.number {
  position: absolute;
  width: 100%;
  height: 100%;
  text-align: center;
  font-size: 14px;
  font-weight: bold;
  transform: rotate(var(--rotation));
}

.number1 { --rotation: 30deg; }
.number2 { --rotation: 60deg; }
.number3 { --rotation: 90deg; }
.number4 { --rotation: 120deg; }
.number5 { --rotation: 150deg; }
.number6 { --rotation: 180deg; }
.number7 { --rotation: 210deg; }
.number8 { --rotation: 240deg; }
.number9 { --rotation: 270deg; }
.number10 { --rotation: 300deg; }
.number11 { --rotation: 330deg; }
.number12 { --rotation: 0deg; }

#digital-clock {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-top: 10px;
}
</style>

<script>
function updateClock() {
  const now = new Date();
  const hour = now.getHours() % 12;
  const minute = now.getMinutes();
  const second = now.getSeconds();

  const hourDeg = (hour + minute / 60) * 30;
  const minuteDeg = (minute + second / 60) * 6;
  const secondDeg = second * 6;

  document.querySelector('.hour-hand').style.transform = `rotate(${hourDeg}deg)`;
  document.querySelector('.minute-hand').style.transform = `rotate(${minuteDeg}deg)`;
  document.querySelector('.second-hand').style.transform = `rotate(${secondDeg}deg)`;

  const options = { 
    timeZone: 'America/Chicago',
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit',
    hour12: true
  };
  const timeString = now.toLocaleString('en-US', options);
  document.getElementById('digital-clock').textContent = timeString;
}

updateClock();
setInterval(updateClock, 1000);
</script> """

# put clock into empty container to move to corner of page
with clock_container:
    components.html(js_code, height=250)
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
                 timedelta(days=st.session_state.days - .50))

st.subheader(f"{selection} for {place} | {selected_date.strftime('%A''\n''%Y-%m-%d')}")

if place:
    try:
        # Fetch weather data and coordinates
        all_weather_data, city_info = get_weather(place, days)

        st.session_state.all_weather_data = all_weather_data
        st.session_state.city_info = city_info

        lat, lon = get_coordinates(place)

        # Get the timezone for the given coordinates
        tf = TimezoneFinder()
        timezone_str = tf.certain_timezone_at(lat=lat, lng=lon)
        local_tz = pytz.timezone(timezone_str)

        # Get weather for the selected day
        day_weather = get_weather_for_day(all_weather_data, st.session_state.days, local_tz)
        night_weather = get_weather_for_night(all_weather_data, st.session_state.days, local_tz)
        if day_weather:
            # Update background image based on weather condition
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
            st.sidebar.header(f"{selected_date.strftime('%A''\n''%Y-%m-%d')}")
            st.subheader(f"Weather in {city_info['name']}, {city_info['country']}")
            st.write(f"Population: {city_info['population']:,}")

            st.slider(" 5 Day Forecast ", 1, 5,
                      key="sidebar_slider_days",
                      value=st.session_state.days,
                      on_change=update_days_sidebar,
                      help="Select the day")

            day_weather = get_weather_for_day(all_weather_data, st.session_state.days, local_tz)
            night_weather = get_weather_for_night(all_weather_data, st.session_state.days, local_tz)

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

        if selection == "Temperature":
            if 'all_weather_data' not in st.session_state or not st.session_state.all_weather_data:
                st.write("No weather data available for the selected day(s).")
            else:
                all_weather_data = st.session_state.all_weather_data
                city_info = st.session_state.city_info

                chart_data = []
                for data in all_weather_data:
                    local_time = parse_api_datetime(data["dt_txt"]).astimezone(pytz.timezone("America/Chicago"))
                    chart_data.append({
                        "Time/Date": local_time,
                        "Temperature": data["main"]["temp"],
                        "Real Feel": data["main"]["feels_like"],
                        "Humidity": data["main"]["humidity"],
                        "Wind Speed": data["wind"]["speed"],
                        "Clouds": data["clouds"]["all"],
                        "Pressure": data["main"]["pressure"],
                        "Pop": data.get("pop", 0) * 100  # Convert probability of precipitation to percentage
                    })

                df = pd.DataFrame(chart_data)

                # Display city information
                st.subheader(f"Weather in {city_info['name']}, {city_info['country']}")
                st.write(f"Population: {city_info['population']:,}")

                # Create and display the main weather chart
                fig = create_additional_weather_conditions_chart(df, city_info)
                st.plotly_chart(fig, use_container_width=True)
                st.audio("summer_music.mp3", start_time=5, autoplay=True, format="audio/mpeg", loop=True)
                st.write(
                    f"Weather forecast from {df['Time/Date'].min().strftime('%B %d, %Y')} "
                    f"to {df['Time/Date'].max().strftime('%B %d, %Y')}")

                # Display raw data in a table (optional)
                if st.toggle("Show raw data"):
                    st.write(df)

        elif selection == "Sky-View":
            images = {"Clear": clear, "Clouds": clouds, "Rain": rainy, "Snow": snow}

            if all_weather_data:
                first_data_date = parse_api_datetime(all_weather_data[0]['dt_txt']).date()

                daily_conditions = {}
                for i in range(st.session_state.days):
                    target_date = first_data_date + timedelta(days=i)
                    day_data = [d for d in all_weather_data if parse_api_datetime(d['dt_txt']).date() == target_date]

                    if day_data:
                        mid_day_data = max(day_data, key=lambda x: parse_api_datetime(x['dt_txt']).hour)
                        local_time = parse_api_datetime(mid_day_data["dt_txt"]).astimezone()

                        daily_conditions[target_date] = {
                            "condition": mid_day_data["weather"][0]["main"],
                            "time": local_time.strftime("%I:%M %p"),
                            "temperature": mid_day_data["main"]["temp"]
                        }

                cols = st.columns(len(daily_conditions))
                for i, (date, info) in enumerate(daily_conditions.items()):
                    with cols[i]:
                        st.write(f"**{date.strftime('%A, %B %d')}**")
                        st.write(f"Time: {info['time']}")
                        st.write(f"Condition: {info['condition']}")
                        st.write(f"Temperature: {info['temperature']:.1f}°F")

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
                        return min(all_weather_data,
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
    except Exception as e:
        st.write(f"An error occurred: {str(e)}")

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
