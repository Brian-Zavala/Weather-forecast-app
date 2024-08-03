import requests
import streamlit as st
from datetime import datetime
import time
from streamlit_lottie import st_lottie_spinner
import json
from streamlit_extras.let_it_rain import rain

API_KEY = "6d88b1e8f4d58057b86ef9f8375c356a"


def get_weather(place, days=None):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={place}&units=imperial&appid={API_KEY}"
    response = requests.get(url)
    data = response.json()
    filtered_data_weather = data["list"]
    if days is not None:
        fc_days = 8 * days
        filtered_data_weather = filtered_data_weather[:fc_days]
    return filtered_data_weather


def get_coordinates(place, lat=None, lon=None):
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
        emoji="😁",
        font_size=54,
        falling_speed=5,
        animation_length="0.65"
    )


def celebration2():
    rain(
        emoji="😭",
        font_size=54,
        falling_speed=5,
        animation_length="0.65"
    )


thumbDown = get("lottie/thumbs_down.json")
thumbUp = get("lottie/thumbs_up.json")


def collect_and_display_feedback():
    # Initialize session state for storing feedback
    if 'feedback_list' not in st.session_state:
        st.session_state.feedback_list = []

    st.subheader("Provide Feedback")

    # Create columns for thumbs up and down buttons
    col1, col2 = st.columns(2)

    with col1:
        thumbs_up = st.button("👍 Thumbs Up")
        if thumbs_up:
            with st_lottie_spinner(thumbUp, height=200):
                time.sleep(1)
                celebration1()

    with col2:
        thumbs_down = st.button("👎 Thumbs Down")
        if thumbs_down:
            with st_lottie_spinner(thumbDown, height=220):
                time.sleep(1)
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
    print(get_coordinates(place="Houston", lat="", lon=""))
