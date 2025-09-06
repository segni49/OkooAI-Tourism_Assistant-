import streamlit as st
from api_utils import upload_document, list_documents, delete_document
from typing import List, Dict

def display_sidebar():
    # 📄 File upload
    uploaded_file = st.sidebar.file_uploader("Choose a file", type=["pdf", "docx", "html"])
    if uploaded_file and st.sidebar.button("Upload"):
        with st.spinner("Uploading..."):
            upload_response = upload_document(uploaded_file)
            if upload_response:
                st.sidebar.success(f"File uploaded with ID {upload_response['file_id']}")
                st.session_state.documents = list_documents()

    # 📜 Document list
    st.sidebar.header("Uploaded Documents")
    if st.sidebar.button("Refresh Document List"):
        st.session_state.documents = list_documents()

    _display_document_list(st.session_state.get("documents", []))

def _display_document_list(documents: List[Dict]):
    if not documents:
        st.sidebar.info("No documents uploaded yet.")
        return

    for doc in documents:
        st.sidebar.text(f"{doc['filename']} (ID: {doc['id']})")

    selected_file_id = st.sidebar.selectbox(
        "Select a document to delete",
        options=[doc['id'] for doc in documents],
        format_func=lambda x: next((doc['filename'] for doc in documents if doc['id'] == x), str(x))
    )

    if st.sidebar.button("Delete Selected Document"):
        delete_response = delete_document(selected_file_id)
        if delete_response:
            st.sidebar.success("Document deleted successfully.")
            st.session_state.documents = list_documents()