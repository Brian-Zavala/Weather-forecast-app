import requests
import streamlit as st
from datetime import datetime, timedelta
import time
import pytz
import folium
from streamlit_lottie import st_lottie_spinner
import json
from streamlit_extras.let_it_rain import rain
from plotly.subplots import make_subplots
import plotly.graph_objects as go

API_KEY = "99244869d28dc08abf57775616f75887"


def get_weather(place, days=None):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={place}&units=imperial&appid={API_KEY}"
    response = requests.get(url)
    data = response.json()
    filtered_data_weather = data["list"]
    if days is not None:
        fc_days = 8 * days
        filtered_data_weather = filtered_data_weather[:fc_days]
    city_info = {
        'name': data['city']['name'],
        'country': data['city']['country'],
        'population': data['city']['population'],
        'sunrise': data['city']['sunrise'],
        'sunset': data['city']['sunset']
    }

    return filtered_data_weather, city_info


def parse_api_datetime(dt_txt):
    return datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.UTC)


def get_weather_for_day(weather_data, days, local_tz):
    if not weather_data:
        return None
    target_date = parse_api_datetime(weather_data[0]['dt_txt']).astimezone(local_tz).date() + timedelta(days=days)
    day_data = [d for d in weather_data if parse_api_datetime(d['dt_txt']).astimezone(local_tz).date() == target_date
                and 4 < parse_api_datetime(d['dt_txt']).astimezone(local_tz).hour <= 16]  # 7 AM to 7 PM
    return max(day_data, key=lambda x: x['main']['temp']) if day_data else None


def get_weather_for_night(weather_data, days, local_tz):
    if not weather_data:
        return None
    target_date = parse_api_datetime(weather_data[0]['dt_txt']).astimezone(local_tz).date() + timedelta(days=days)
    night_data = [d for d in weather_data if parse_api_datetime(d['dt_txt']).astimezone(local_tz).date() == target_date
                  and (parse_api_datetime(d['dt_txt']).astimezone(local_tz).hour > 19
                       or parse_api_datetime(d['dt_txt']).astimezone(local_tz).hour <= 7)]  # 7 PM to 7 AM
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


def create_additional_weather_conditions_chart(df, city_info):
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces for temperature
    fig.add_trace(
        go.Scatter(x=df["Time/Date"], y=df["Temperature"], name="Temperature", line=dict(color="#FF9900", width=2)),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=df["Time/Date"], y=df["Real Feel"], name="Real Feel", line=dict(color="#FF5733", width=2)),
        secondary_y=False,
    )

    # Add trace for humidity
    fig.add_trace(
        go.Scatter(x=df["Time/Date"], y=df["Humidity"], name="Humidity", line=dict(color="#33A1FD", width=2)),
        secondary_y=True,
    )

    # Add trace for wind speed
    fig.add_trace(
        go.Scatter(x=df["Time/Date"], y=df["Wind Speed"], name="Wind Speed", line=dict(color="#2ECC71", width=2)),
        secondary_y=True,
    )

    # Add trace for cloud coverage
    fig.add_trace(
        go.Scatter(x=df["Time/Date"], y=df["Clouds"], name="Cloud Coverage", line=dict(color="#A569BD", width=2)),
        secondary_y=True,
    )

    # Add trace for precipitation probability
    fig.add_trace(
        go.Scatter(x=df["Time/Date"], y=df["Pop"], name="Precipitation Probability", line=dict(color="#3498DB", width=2)),
        secondary_y=True,
    )

    # Update layout
    fig.update_layout(
        title_text=f"Detailed Weather Forecast for {city_info['name']}, {city_info['country']} (Pop: {city_info['population']:,})",
        height=600,
        legend_title_text="Weather Variables",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # Set x-axis title
    fig.update_xaxes(title_text="Date and Time", tickangle=-45, tickformat="%b %d\n%I:%M %p")

    # Set y-axes titles
    fig.update_yaxes(title_text="Temperature (°F)", secondary_y=False)
    fig.update_yaxes(title_text="Weather Variables", secondary_y=True)

    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(visible=True),
            type="date"
        )
    )

    return fig


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
