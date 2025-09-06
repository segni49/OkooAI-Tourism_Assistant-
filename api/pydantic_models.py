from pydantic import BaseModel
from typing import Optional

class QueryInput(BaseModel):
    session_id: Optional[str]
    question: str
    model: Optional[str] = "qwen:0.5b"  # ✅ Added for model selection

class DocumentInfo(BaseModel):
    file_id: str
    filename: str

class DeleteFileRequest(BaseModel):
    file_id: str