import streamlit as st


st.set_page_config(layout="wide")

st.title("Weather Forecast")

place = st.text_input("Location:")

days = st.slider("Forecast Days", 1, 5, help="Select the day you'd like to see")

data = st.selectbox("Select data to view",
                   ("Temperature", "sky"))

st.subheader(f"Temperature for the next {days} days in {place}")