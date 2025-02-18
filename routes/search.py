# search.py

from fastapi import APIRouter, Query
from services.elasticsearch import search_documents

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/")
async def search(
    query: str,
    date_start: str = None,
    date_end: str = None,
    user_id: str = None,
    document_id: str = None,  # Changed from doc_id to match indexing function
):
    """
    Search documents in Elasticsearch with optional filters for date, user_id, and document_id.
    """
    filters = {}
    
    if date_start and date_end:
        filters["timestamp"] = {"gte": date_start, "lte": date_end}  # Changed from upload_time to timestamp

    if user_id:
        filters["user_id"] = user_id

    if document_id:
        filters["document_id"] = document_id  # Changed from doc_id to match indexed field name

    print(f"query:{query} filters:{filters}")
    results = search_documents(query, filters)
    return results
