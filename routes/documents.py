# documents

from fastapi import APIRouter, Depends, HTTPException
from services.firestore import get_user_documents
from services.firebase_auth import get_current_user

router = APIRouter()

@router.get("/documents")
async def get_documents(user_id: str = Depends(get_current_user)):
    try:
        return get_user_documents(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))