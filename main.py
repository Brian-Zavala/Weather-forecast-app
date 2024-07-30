import streamlit as st
import plotly.express as px


st.set_page_config(layout="wide")

st.title("Weather Forecast")

place = st.text_input("Location:")

days = st.slider("Forecast Days", 1, 5, help="Select the day you'd like to see")

data = st.selectbox("Select data to view",
                   ("Temperature", "sky"))

st.subheader(f"Temperature for the next {days} days in {place}")

dates = ["2022-25-10", "2022-26-10", "2022-27-10", "2022-28-10", "2022-29-10",]
temperature = ["100", "99", "87", "96", "107"]
temperature = [days * i for i in temperature]

figure = px.line(x=dates, y=temperature, labels={"x": "Date", "y": "Temperature"},)
st.plotly_chart(figure, use_container_width=True)
