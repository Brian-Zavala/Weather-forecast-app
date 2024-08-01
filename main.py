import streamlit as st
from pygments.styles.dracula import red
from streamlit_lottie import st_lottie
import plotly.express as px
from backend import get_data
from backend import collect_and_display_feedback
import json
from datetime import datetime
import pytz


st.set_page_config(layout="wide")

st.logo("https://miro.medium.com/v2/resize:fit:1200/1*N9tLv5CqD4wtZQXheWEEKw.gif")


def get(path: str):
    with open(path, "r") as f:
        return json.load(f)


thumbDown = get("lottie/thumbs_down.json")
thumbUp = get("lottie/thumbs_up.json")
clear = get("lottie/clear.json")
clouds = get("lottie/cloudy.json")
rain = get("lottie/rain.json")
snow = get("lottie/snow.json")

page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
background-image: url("https://cdn2.vectorstock.com/i/1000x1000/06/56/clouds-background-vector-20700656.jpg");
background-size: 100%;
background-position: center;
background-attachment: local; 

}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# Add front-end to webpage title, widgets
st.title("5-Day Weather Forecast")

place = st.text_input("City Name & or State or Zip Code: ")

timeZone = st.selectbox("Select timezone to use: ", pytz.all_timezones)

days = st.slider("Next 5 days", 1, 5, help="Select the day you'd like to see")

choice = st.selectbox("Select data to view",
                      ("Temperature", "Sky"))



st.subheader(f"{choice} for the next {days} day(s) in {place}")


if place:
    # Use the imported data for temperature/sky
    filtered_data = get_data(place, days)

    if choice == "Temperature":
        temperature = [dict["main"]["temp"] for dict in filtered_data]

        date = []
        local_tz = pytz.timezone(timeZone)  # Replace with your local timezone, e.g., "America/New_York"

        for dict in filtered_data:
            dt = datetime.strptime(dict["dt_txt"], "%Y-%m-%d %H:%M:%S")
            dt = pytz.utc.localize(dt)  # Assume the API data is in UTC
            local_dt = dt.astimezone(local_tz)
            formatted_date = local_dt.strftime("%Y-%m-%d %I:%M %p")  # 12-hour format with AM/PM
            date.append(formatted_date)
        # Create a temperature line graph
        figure = px.bar(x=date, y=temperature, color=temperature, labels={"x": "Date", "y": "Temperature (F)"})

        figure.update_layout(
            xaxis_title="Date (Local Time)",
            yaxis_title="Temperature (°F)",
            xaxis_tickangle=-45  # Rotate x-axis labels for readability
        )

        st.plotly_chart(figure, use_container_width=True, theme="streamlit")

    if choice == "Sky":
        images = {"Clear": clear, "Clouds": clouds,
                  "Rain": rain, "Snow": snow}
        # Group the data by day
        daily_conditions = {}
        for data_point in filtered_data:
            date = data_point["dt_txt"].split()[0]  # Get just the date
            time = datetime.strptime(data_point["dt_txt"], "%Y-%m-%d %H:%M:%S").strftime("%I:%M %p")
            temperature = [dict["main"]["temp"] for dict in filtered_data]
            condition = data_point["weather"][0]["main"]
            if date not in daily_conditions:
                daily_conditions[date] = {"condition": condition,
                                          "time": time, "temperature": temperature}

        # Create columns for each day
        cols = st.columns(len(daily_conditions))

        # Display the weather condition for each day
        for i, (date, info) in enumerate(daily_conditions.items()):
            with cols[i]:
                st.write(f"{date} | {info['time']}")
                st.write(info["condition"])

                if info['condition'] in images:
                    st_lottie(images[info['condition']], height=175, key=f"lottie_{i}")
                else:
                    st.write(f"No animation for {info['condition']}")


collect_and_display_feedback()
