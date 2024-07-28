import streamlit as st


st.set_page_config(layout="wide")

st.header("Weather Forecast")

place = st.text_input("Place:")

days = st.slider("Forecast Days", 1, 7)

data = st.selectbox("Select data to view", options='')