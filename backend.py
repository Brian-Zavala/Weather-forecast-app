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
import pandas as pd

API_KEY = "99244869d28dc08abf57775616f75887"


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


def get_weather_for_day(weather_data, days, local_tz):
    if not weather_data:
        return None
    target_date = parse_datetime(weather_data[0]['dt_txt']).astimezone(local_tz).date() + timedelta(days=days - .93)
    day_data = [d for d in weather_data if parse_datetime(d['dt_txt']).astimezone(local_tz).date() == target_date
                and 7 < parse_datetime(d['dt_txt']).astimezone(local_tz).hour <= 19]  # 7 AM to 7 PM
    return max(day_data, key=lambda x: x['main']['temp']) if day_data else None

def get_weather_for_night(weather_data, days, local_tz):
    if not weather_data:
        return None
    target_date = parse_datetime(weather_data[0]['dt_txt']).astimezone(local_tz).date() + timedelta(days=days - .93)
    night_data = [d for d in weather_data if parse_datetime(d['dt_txt']).astimezone(local_tz).date() == target_date
                  and (parse_datetime(d['dt_txt']).astimezone(local_tz).hour > 19
                       or parse_datetime(d['dt_txt']).astimezone(local_tz).hour <= 7)]  # 7 PM to 7 AM
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


def create_additional_weather_conditions_chart(df):
    # Function to parse the date-time string
    def parse_datetime(date_string):
        try:
            # Try parsing with year
            return pd.to_datetime(date_string, format='%Y-%m-%d %I:%M %p')
        except ValueError:
            try:
                # If year is missing, assume current year
                current_year = datetime.now().year
                return pd.to_datetime(f"{current_year}-{date_string}", format='%Y-%m-%d %I:%M %p')
            except ValueError:
                # If all else fails, return NaT (Not a Time)
                return pd.NaT

    # Ensure the Time/Date column is in datetime format
    df['Time/Date'] = df['Time/Date'].apply(parse_datetime)

    # Remove any rows with invalid dates
    df = df.dropna(subset=['Time/Date'])

    # Create a new column for weekday
    df['Weekday'] = df['Time/Date'].dt.strftime('%a %I:%M %p')  # e.g., "Mon 03PM"

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Define color scheme
    colors = {
        "Clouds": "skyblue",
        "Pop": "blue",
        "Humidity": "green",
        "Wind Speed": "orange",
        "Pressure": "red",
        "Temperature": "darkred",
        "Real Feel": "purple",
        "Visibility": "brown"
    }

    # Add traces for each weather condition
    primary_y_vars = ["Clouds", "Pop", "Humidity", "Wind Speed", "Temperature", "Real Feel"]
    for var in primary_y_vars:
        if var in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df["Weekday"],
                    y=df[var],
                    name=f"{var} ({get_unit(var)})",
                    line=dict(color=colors[var]),
                    hovertemplate='%{text}<br>%{y:.1f}' + get_unit(var),
                    text=[f"{date.strftime('%Y-%m-%d %I:%M %p')}<br>{var}" for date in df['Time/Date']]
                ),
                secondary_y=False,
            )

    # Add pressure on secondary y-axis
    if "Pressure" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df["Weekday"],
                y=df["Pressure"],
                name=f"Pressure ({get_unit('Pressure')})",
                line=dict(color=colors["Pressure"]),
                hovertemplate='%{text}<br>%{y:.1f}' + get_unit('Pressure'),
                text=[f"{date.strftime('%Y-%m-%d %I:%M %p')}<br>Pressure" for date in df['Time/Date']]
            ),
            secondary_y=True,
        )

    # Add visibility if available
    if "Visibility" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df["Weekday"],
                y=df["Visibility"],
                name=f"Visibility ({get_unit('Visibility')})",
                line=dict(color=colors["Visibility"]),
                hovertemplate='%{text}<br>%{y:.1f}' + get_unit('Visibility'),
                text=[f"{date.strftime('%Y-%m-%d %I:%M %p')}<br>Visibility" for date in df['Time/Date']]
            ),
            secondary_y=False,
        )

    # Update layout
    fig.update_layout(
        title_text="Comprehensive Weather Conditions",
        height=600,
        legend_title_text="Weather Variables",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # Set x-axis title and format
    fig.update_xaxes(
        title_text="Day of Week",
        tickangle=-45,
        tickmode='array',
        tickvals=df['Weekday'][::4],  # Show every 4th tick to avoid overcrowding
        ticktext=df['Weekday'][::4]
    )

    # Set y-axes titles
    fig.update_yaxes(title_text="Values", secondary_y=False)
    fig.update_yaxes(title_text=f"Pressure ({get_unit('Pressure')})", secondary_y=True)

    return fig


def get_unit(variable):
    """Return the appropriate unit for each weather variable."""
    units = {
        "Clouds": "%",
        "Pop": "%",
        "Humidity": "%",
        "Wind Speed": "mph",
        "Pressure": "hPa",
        "Temperature": "°F",
        "Real Feel": "°F",
        "Visibility": "m"
    }
    return units.get(variable, "")


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
