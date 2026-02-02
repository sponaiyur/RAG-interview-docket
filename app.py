import streamlit as st
from ui.layout import render_app
from ui.state import init_state

st.set_page_config(page_title="Interview Docket", page_icon="🧠", layout="wide")

init_state()
render_app()
