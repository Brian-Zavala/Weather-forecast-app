import requests
import streamlit as st
from datetime import datetime, timedelta
import time
import folium
from streamlit_lottie import st_lottie_spinner
import json
from streamlit_extras.let_it_rain import rain
import functools

API_KEY = "6d88b1e8f4d58057b86ef9f8375c356a"


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


def get_weather_for_day(filtered_data_weather, selected_day):
    selected_date = (datetime.now() + timedelta(days=selected_day)).strftime("%Y-%m-%d")
    day_weather = [data for data in filtered_data_weather if data['dt_txt'].startswith(selected_date)]
    if day_weather:
        # Return the weather for the middle of the day (noon) if available, otherwise the first entry
        high_weather = next((w for w in day_weather if w['dt_txt'].endswith("13:30:30")), day_weather[0])
        return high_weather
    return None


def get_weather_for_night(filtered_data_weather, selected_day):
    selected_date = (datetime.now() + timedelta(days=selected_day)).strftime("%Y-%m-%d")
    night_weather = [data for data in filtered_data_weather if data['dt_txt'].startswith(selected_date)]
    if night_weather:
        # Return the weather for the middle of the day (noon) if available, otherwise the first entry
        low_weather = next((w for w in night_weather if w['dt_txt'].endswith("12:30:30")), night_weather[0])
        return low_weather
    return None


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
