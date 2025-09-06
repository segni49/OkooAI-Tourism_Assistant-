from api.chroma_utils import index_document_to_chroma, vectorstore
import os
import logging

def preload_documents():
    logging.info("📦 Starting document indexing from /data...")

    try:
        existing_docs = vectorstore.get()
        if existing_docs and len(existing_docs["documents"]) > 0:
            logging.info("🧠 Chroma DB already populated with chunks. Skipping indexing.")
            return
    except Exception as e:
        logging.warning(f"⚠️ Could not inspect Chroma DB: {e}")

    data_dir = os.path.join(os.getcwd(), "data")
    if not os.path.exists(data_dir):
        logging.warning("⚠️ /data directory does not exist.")
        return

    for filename in os.listdir(data_dir):
        file_path = os.path.join(data_dir, filename)

        if not os.path.isfile(file_path):
            continue
        if not filename.lower().endswith(('.pdf', '.docx', '.html', '.csv')):
            logging.info(f"⏩ Skipping unsupported file: {filename}")
            continue

        logging.info(f"📄 Indexing file: {filename}")
        success = index_document_to_chroma(file_path, file_id=None)

        if success:
            logging.info(f"✅ Indexed: {filename}")
        else:
            logging.warning(f"❌ Failed to index: {filename}")

    logging.info("🎯 All files in /data indexed.")