# config

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Firebase
    FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")
    
    # GCP
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
    STORAGE_BUCKET = os.getenv("STORAGE_BUCKET")
    
    # Elasticsearch
    ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL")
    ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST")
    ELASTICSEARCH_INDEX = "documents"
    
    # BigQuery
    BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET")
    BIGQUERY_TABLE = os.getenv("BIGQUERY_TABLE")

    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")