import streamlit as st
import plotly.express as px
from backend import get_data

st.set_page_config(layout="wide")

st.title("Weather Forecast")

place = st.text_input("Location:")

days = st.slider("Forecast Days", 1, 14, help="Select the day you'd like to see")

data = st.selectbox("Select data to view",
                   ("Temperature", "sky"))

st.subheader(f"Temperature for the next {days} days in {place}")

p, t = get_data(place, days, option)


figure = px.line(x=dates, y=temperature, labels={"x": "Date", "y": "Temperature"},)
st.plotly_chart(figure, use_container_width=True)
