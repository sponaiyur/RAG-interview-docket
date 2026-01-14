'''
components.py: save all the components here, app.py must call these components
- this is required to keep the codebase modular
- example code (just assume these functions as ):
import streamlit as st

def header():
    st.title("Simple Processing App")
    st.write("Upload a file and process it.")

def upload_section():
    st.subheader("Upload")
    uploaded_file = st.file_uploader("Upload a text file", type=["txt"])

    if uploaded_file is not None:
        text = uploaded_file.read().decode("utf-8")
        st.text_area("File Content", text, height=150)
        return text

    return None
'''