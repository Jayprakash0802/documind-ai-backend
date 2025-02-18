from pydantic import BaseModel
from datetime import datetime

class DocumentMetadata(BaseModel):
    file_name: str
    file_size: int
    status: str  # e.g., "uploaded", "processing", "processed"
    uploaded_at: datetime
    user_id: str
    document_id: str

class DocumentProcessed(DocumentMetadata):
    ocr_text: str
    summary: str

class SearchQuery(BaseModel):
    query: str
    filters: dict  # e.g., {"uploaded_at": "2023-10-01", "user_id": "12345"}