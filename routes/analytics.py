# analytics

from fastapi import APIRouter
from services.bigquery import get_analytics

router = APIRouter()

@router.get("/analytics")
async def get_document_analytics():
    analytics = "fetched from backend"
    # analytics = get_analytics()
    return {"analytics": analytics}