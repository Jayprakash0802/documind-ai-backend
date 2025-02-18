# processing

from fastapi import APIRouter, HTTPException
from services.gcp_vision import extract_text
from services.gcp_summarization import summarize_text
from services.elasticsearch import index_document
from services.firestore import update_document_status
from services.bigquery import log_document_activity
from services.storage import save_text_to_file
from services.elasticsearch import enable_cache
from google.cloud import storage
from config import Config
# from schemas.models import DocumentMetadata

router = APIRouter()

storage_client = storage.Client()

@router.get("/process")
async def process_document(user_id: str, document_id: str):
    try:
        # Step 1: Extract text using GCP Vision
        summary_path = f"summary/{user_id}/{document_id}"
        bucket = storage_client.bucket(Config.STORAGE_BUCKET)
        blob = bucket.blob(summary_path)
        extracted_text = "Extracted text for deepseek"
        if not blob.exists():
            file_path = f"documents/{user_id}/{document_id}"
            extracted_path = f"extracted_documents/{user_id}/{document_id}"
            extracted_text = extract_text(file_path,extracted_path,document_id,user_id)
            
            # Step 2: Summarize text using GCP Natural Language
            # return {"message":extracted_text}
            print("text extracted successfully")
            summary = summarize_text(extracted_text)
            save_text_to_file(summary, summary_path)
            # return {"summary":summary,"extracted_text":extracted_text}
            # Step 3: Index document in Elasticsearch
        else :
            summary = blob.download_as_text() 
        enable_cache()
        title="Elastic search test"
        print(f"before indexing ")
        index_document(document_id, user_id,title,extracted_text,summary)
        print("after indexing")
        
        # Step 4: Update Firestore document status
        # update_document_status(user_id, document_id, {
        #     "ocr_text": extracted_text,
        #     "summary": summary,
        #     "status": "processed"
        # })
        return {"summary":summary,"extracted_text":"extracted_text"}
        
        # Step 5: Log activity in BigQuery
        log_document_activity(user_id, document_id, "processed")
        
        return {"message": "Document processed successfully", "summary": summary}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))