import streamlit as st
from sidebar import display_sidebar
from chat_interface import display_chat_interface

st.set_page_config(page_title="OkooAI", layout="wide")
st.title("🌍 OkooAI — Tourism Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "documents" not in st.session_state:
    st.session_state.documents = []

display_sidebar()
display_chat_interface()