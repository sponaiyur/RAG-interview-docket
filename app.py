''' 
app.py: 

Must only include:
- File upload widgets
- Button clicks
- Calling relevant pipeline functions
- Displaying output

app.py must not be very detailed, this file only calls functions and renders streamlit. 
All other functions to go into respective files

- example code:
import streamlit as st
from ui.layout import render_app

st.set_page_config(page_title="Demo App")

render_app()
'''
import streamlit as st
from ui.layout import render_app

st.set_page_config(page_title="Interview Docket Generator", layout="wide")

render_app()
