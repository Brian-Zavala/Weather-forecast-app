import requests
import streamlit as st
from datetime import datetime, timedelta
import time
import pytz
import folium
from streamlit_lottie import st_lottie_spinner
import json
from streamlit_extras.let_it_rain import rain
import functools

API_KEY = "3bf7caa87020b27d3fa66e62172e5af6"


def cache_with_timeout(timeout_seconds):
    def decorator(func):
        cache = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            current_time = time.time()
            if key in cache:
                result, timestamp = cache[key]
                if current_time - timestamp < timeout_seconds:
                    return result
            result = func(*args, **kwargs)
            cache[key] = (result, current_time)
            return result

        return wrapper

    return decorator


@cache_with_timeout(300)  # Cache for 5 minutes
def get_weather(place, days=None):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={place}&units=imperial&appid={API_KEY}"
    response = requests.get(url)
    data = response.json()
    filtered_data_weather = data["list"]
    if days is not None:
        fc_days = 8 * days
        filtered_data_weather = filtered_data_weather[:fc_days]
    return filtered_data_weather


def parse_datetime(dt_str):
    return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.UTC)


def get_weather_for_day(weather_data, days):
    target_date = (datetime.now(pytz.UTC) + timedelta(days=days)).date()
    day_data = [d for d in weather_data if parse_datetime(d['dt_txt']).date() == target_date
                and 7 <= parse_datetime(d['dt_txt']).hour < 18]
    return max(day_data, key=lambda x: x['main']['temp']) if day_data else None


def get_weather_for_night(weather_data, days):
    target_date = (datetime.now(pytz.UTC) + timedelta(days=days)).date()
    night_data = [d for d in weather_data if parse_datetime(d['dt_txt']).date() == target_date
                  and (parse_datetime(d['dt_txt']).hour < 16 or parse_datetime(d['dt_txt']).hour > 23)]
    return min(night_data, key=lambda x: x['main']['temp']) if night_data else None


def get_radar():
    API_URL = f"https://api.rainviewer.com/public/weather-maps.json"
    response = requests.get(API_URL)
    return response.json()


def create_map(data, selected_frame, frame_type, place):
    lat, lon = get_coordinates(place)

    m = folium.Map(location=[lat, lon], zoom_start=8)

    tile_url = f"{data['host']}{selected_frame['path']}/256/{{z}}/{{x}}/{{y}}/2/1_1.png"
    folium.TileLayer(
        tiles=tile_url,
        name=f"{frame_type.capitalize()} Radar",
        attr="RainViewer",
        overlay=True,
        controls=True
    ).add_to(m)

    coverage_url = f"{data['host']}/v2/coverage/0/256/{{z}}/{{x}}/{{y}}/0/0_0.png"
    folium.TileLayer(
        tiles=coverage_url,
        attr='RainViewer',
        name='Radar Coverage',
        overlay=True,
        control=True
    ).add_to(m)

    folium.Marker(
        location=[lat, lon],
        popup="Selected Location",
        tooltip="Selected Location"
    ).add_to(m)

    return m


def get_coordinates(place):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={place}&units=imperial&appid={API_KEY}"
    response = requests.get(url)
    data = response.json()
    city_info = data['city']
    lat = city_info['coord']['lat']
    lon = city_info['coord']['lon']
    return lat, lon


def get(path: str):
    with open(path, "r") as f:
        return json.load(f)


def celebration1():
    rain(
        emoji="😇👏",
        font_size=54,
        falling_speed=4,
        animation_length="0.65"
    )


def celebration2():
    rain(
        emoji="👹😭",
        font_size=54,
        falling_speed=4,
        animation_length="0.65"
    )


thumbDown = get("lottie/cry.json")
thumbUp = get("lottie/confetti.json")


def collect_and_display_feedback():
    # Initialize session state for storing feedback
    if 'feedback_list' not in st.session_state:
        st.session_state.feedback_list = []
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")

    st.subheader("😇 Feedback Available 👹")

    # Create columns for thumbs up and down buttons
    col1, col2, col3 = st.columns([0.6, 0.6, 1.8], gap='large')

    with col1:
        thumbs_up = st.button("👍")
        if thumbs_up:
            with st_lottie_spinner(thumbUp, quality="high", speed=1):
                st.audio("cheer.mp3", format="audio/mpeg", autoplay=True)
                time.sleep(6)
                celebration1()

    with col2:
        thumbs_down = st.button("👎")
        if thumbs_down:
            with st_lottie_spinner(thumbDown, speed=1):
                st.audio("fail.wav", format="audio/wav", autoplay=True)
                time.sleep(6)
                celebration2()

    # Text input for comment
    comment = st.text_input("Add a comment (optional)")

    # Check if either button is clicked
    if thumbs_up or thumbs_down:
        feedback_type = "" if thumbs_up else ""

        # Add the new feedback to the list
        st.session_state.feedback_list.append({
            'type': feedback_type,
            'comment': comment if comment else 'No comment',
            'timestamp': datetime.now().strftime("%Y-%m-%d %I:%M %p")
        })

        # Clear the comment input
        st.session_state.widget_key = datetime.now().strftime("%Y%m%d%H%M%S")

        # Show a success message
        st.success(f"{feedback_type} Thanks for your feedback!")

    # Display the feedback list
    st.subheader("Feedback List")
    if st.session_state.feedback_list:
        for idx, item in enumerate(st.session_state.feedback_list, 1):
            icon = "👍" if item['type'] == "Thumbs Up" else "👎"
            st.write(f"{idx}. {icon} {item['type']} - {item['timestamp']}")
            if item['comment'] != 'No comment':
                st.write(f"   Comment: {item['comment']}")
            st.write("---")
    else:
        st.write("No feedback submitted yet.")


if __name__ == '__main__':
    print(get_weather(place="Houston", days=5))
    print(get_coordinates(place="Houston"))
