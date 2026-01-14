'''
layout.py: include the entire UI layout - how would the app finally look like
- app.py just directly calls this layout file, and handles which function to call when.
- example code:
import streamlit as st
from ui.components import (
    header,
    upload_section
)

def render_app():
    header()

    file_text = upload_section()
    processed_text = processing_section(file_text)

    if processed_text is not None:
        output_section(processed_text)
'''