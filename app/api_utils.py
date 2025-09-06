import requests
import streamlit as st
from typing import Optional, List

API_BASE_URL = "http://localhost:8000"

def get_api_response(question: str, session_id: Optional[str]) -> Optional[dict]:
    url = f"{API_BASE_URL}/chat"
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    payload = {
        "question": question,
        "model": "qwen:0.5b",  # 🔒 Locked model
        "session_id": session_id
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Error during API request: {str(e)}")
        return None

def upload_document(file) -> Optional[dict]:
    url = f"{API_BASE_URL}/upload-doc"
    try:
        mime_type = file.type or "application/octet-stream"
        files = {"file": (file.name, file, mime_type)}
        response = requests.post(url, files=files)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Error uploading file: {str(e)}")
        return None

def list_documents() -> List[dict]:
    url = f"{API_BASE_URL}/list-docs"
    try:
        response = requests.get(url)
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        st.error(f"Error fetching documents: {str(e)}")
        return []

def delete_document(file_id: int) -> Optional[dict]:
    url = f"{API_BASE_URL}/delete-doc"
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    payload = {"file_id": file_id}
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Error deleting document: {str(e)}")
        return None