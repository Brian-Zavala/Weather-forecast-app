import streamlit as st
from streamlit_lottie import st_lottie
import plotly.express as px
from backend import get_data
import json

st.set_page_config(layout="wide")


def get(path: str):
    with open(path, "r") as f:
        return json.load(f)

clear = get("lottie/clear.json")
clouds = get("lottie/cloudy.json")
rain = get("lottie/rain.json")
snow = get("lottie/snow.json")



# Add front-end to webpage title, widgets
st.title("Weather Forecast")

place = st.text_input("Location:")

days = st.slider("Forecast Days", 1, 5, help="Select the day you'd like to see")

choice = st.selectbox("Select data to view",
                      ("Temperature", "Sky"))

st.subheader(f"{choice} for the next {days} days in {place}")


if place:
    # Use the imported data for temperature/sky
    filtered_data = get_data(place, days)

    if choice == "Temperature":
        temperature = [dict["main"]["temp"] for dict in filtered_data]
        date = [dict["dt_txt"] for dict in filtered_data]

        # Create a temperature line graph
        figure = px.line(x=date, y=temperature, labels={"x": "Date", "y": "Temperature (F)"}, )
        st.plotly_chart(figure)

    if choice == "Sky":
        images = {"Clear": clear, "Clouds": clouds,
                  "Rain": rain, "Snow": snow}
        # Group the data by day
        daily_conditions = {}
        for data_point in filtered_data:
            date = data_point["dt_txt"].split()[0]  # Get just the date part
            condition = data_point["weather"][0]["main"]
            if date not in daily_conditions:
                daily_conditions[date] = condition

        # Create columns for each day
        cols = st.columns(len(daily_conditions))

        # Display the weather condition for each day
        for i, (date, condition) in enumerate(daily_conditions.items()):
            with cols[i]:
                st.write(date)
                if condition in images:
                    st_lottie(images[condition], height=200, key=f"lottie_{i}")
                else:
                    st.write(f"No animation for {condition}")



