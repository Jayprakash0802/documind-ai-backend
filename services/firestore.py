# firestore

from database import db

def update_document_status(user_id: str, document_id: str, update_data: dict):
    doc_ref = db.collection("users").document(user_id).collection("documents").document(document_id)
    doc_ref.update(update_data)  

def get_user_documents(user_id: str):
    docs_ref = db.collection("users").document(user_id).collection("documents")
    docs = docs_ref.stream()  

    return [doc.to_dict() | {"id": doc.id} for doc in docs] 
