from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from api.pydantic_models import QueryInput, DocumentInfo, DeleteFileRequest
from api.tourism_graph import get_tourism_graph
from api.db_utils import (
    insert_application_logs,
    get_chat_history,
    get_all_documents,
    insert_document_record,
    delete_document_record,
    get_filename_by_id
)
from api.chroma_utils import index_document_to_chroma, delete_doc_from_chroma, vectorstore
from api.bootstrap import preload_documents
import os, uuid, shutil, logging

logging.basicConfig(filename='app.log', level=logging.INFO)
app = FastAPI(title="OkooAI API", description="Tourism RAG assistant", version="1.0.0")

# ✅ Chat endpoint
@app.post("/chat")
def chat(query_input: QueryInput):
    session_id = query_input.session_id or str(uuid.uuid4())
    model_name = query_input.model or "qwen:0.5b"
    logging.info(f"Session ID: {session_id}, User Query: {query_input.question}, Model: {model_name}")

    chat_history = get_chat_history(session_id)
    rag_chain = get_tourism_graph(model=model_name)

    result = rag_chain({
        "input": query_input.question,
        "chat_history": chat_history,
        "model": model_name
    })

    answer = result["answer"]
    source_docs = result.get("source_documents", [])

    source_chunks = []
    for doc in source_docs:
        filename = doc.metadata.get("filename", "unknown")
        chunk_preview = doc.page_content.strip().replace("\n", " ")[:200]
        source_chunks.append(f"[{filename}] {chunk_preview}")

    source_text = "\n\n".join(source_chunks)

    insert_application_logs(session_id, query_input.question, answer, model_name)
    logging.info(f"Session ID: {session_id}, AI Response: {answer}")
    logging.info(f"Source Chunks:\n{source_text}")

    return {
        "answer": answer,
        "session_id": session_id,
        "model": model_name,
        "source": source_text
    }

# ✅ Explore Place endpoint
@app.post("/explore-place")
def explore_place_route(input: str = Form(...), session_id: str = Form(None)):
    model_name = "qwen:0.5b"
    rag_chain = get_tourism_graph(model=model_name)
    result = rag_chain({"input": input, "chat_history": [], "model": model_name})

    answer = result["answer"]
    source_docs = result.get("source_documents", [])
    source_chunks = [
        f"[{doc.metadata.get('filename', 'unknown')}] {doc.page_content.strip().replace('\n', ' ')[:200]}"
        for doc in source_docs
    ]

    return {
        "answer": answer,
        "source": "\n\n".join(source_chunks),
        "intent": "explore_place"
    }

# ✅ Plan Trip endpoint
@app.post("/plan-trip")
def plan_trip_route(input: str = Form(...), session_id: str = Form(None)):
    model_name = "qwen:0.5b"
    rag_chain = get_tourism_graph(model=model_name)
    result = rag_chain({"input": input, "chat_history": [], "model": model_name})
    return {"answer": result["answer"], "intent": "plan_trip"}

# ✅ Compare Hotels endpoint
@app.post("/compare-hotels")
def compare_hotels_route(input: str = Form(...), session_id: str = Form(None)):
    model_name = "qwen:0.5b"
    rag_chain = get_tourism_graph(model=model_name)
    result = rag_chain({"input": input, "chat_history": [], "model": model_name})

    answer = result["answer"]
    source_docs = result.get("source_documents", [])
    source_chunks = [
        f"[{doc.metadata.get('filename', 'unknown')}] {doc.page_content.strip().replace('\n', ' ')[:200]}"
        for doc in source_docs
    ]

    return {
        "answer": answer,
        "source": "\n\n".join(source_chunks),
        "intent": "compare_hotels"
    }

# ✅ Trace endpoint
@app.post("/trace")
def trace_route(input: str = Form(...)):
    from api.intent_classifier import classify_intent
    model_name = "qwen:0.5b"
    intent = classify_intent(input, model=model_name)
    return {"intent": intent}

# ✅ Upload document
@app.post("/upload-doc")
def upload_and_index_document(file: UploadFile = File(...)):
    allowed_extensions = ['.pdf', '.docx', '.html']
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed types are: {', '.join(allowed_extensions)}")

    temp_file_path = f"temp_{file.filename}"

    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_id = insert_document_record(file.filename)
        success = index_document_to_chroma(temp_file_path, file_id)

        if success:
            return {"message": f"File {file.filename} has been successfully uploaded and indexed.", "file_id": file_id}
        else:
            delete_document_record(file_id)
            raise HTTPException(status_code=500, detail=f"Failed to index {file.filename}.")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# ✅ List documents
@app.get("/list-docs", response_model=list[DocumentInfo])
def list_documents():
    return get_all_documents()

# ✅ Delete document
@app.post("/delete-doc")
def delete_document(request: DeleteFileRequest):
    chroma_delete_success = delete_doc_from_chroma(request.file_id)

    if chroma_delete_success:
        db_delete_success = delete_document_record(request.file_id)
        if db_delete_success:
            return {"message": f"Successfully deleted document with file_id {request.file_id} from the system."}
        else:
            return {"error": f"Deleted from Chroma but failed to delete document with file_id {request.file_id} from the database."}
    else:
        return {"error": f"Failed to delete document with file_id {request.file_id} from Chroma."}

# ✅ Ping
@app.get("/ping")
def ping():
    return {"status": "ok"}

# ✅ Debug chunks
@app.get("/debug-chunks")
def debug_chunks():
    docs = vectorstore.get()
    return {
        "total_chunks": len(docs["documents"]),
        "sample": [doc.page_content[:200] for doc in docs["documents"][:3]]
    }

# ✅ Preload documents on startup
preload_documents()