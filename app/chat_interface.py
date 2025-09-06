import streamlit as st
from api_utils import get_api_response
from typing import Dict

def display_chat_interface():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Query:"):
        st.session_state.messages.append({"role": "human", "content": prompt})
        with st.chat_message("human"):
            st.markdown(prompt)

        with st.spinner("Generating response..."):
            session_id = st.session_state.get("session_id")
            response: Dict | None = get_api_response(prompt, session_id)

            if response:
                st.session_state.session_id = response.get("session_id")
                st.session_state.messages.append({"role": "ai", "content": response["answer"]})
                with st.chat_message("ai"):
                    st.markdown(response["answer"])
                _display_response_details(response)
            else:
                st.error("Failed to get a response from the API.")

def _display_response_details(response: Dict):
    with st.expander("Details"):
        st.subheader("Generated Answer")
        st.code(response["answer"])
        st.subheader("Model Used")
        st.code(response["model"])
        st.subheader("Session ID")
        st.code(response["session_id"])