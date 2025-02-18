from google.cloud import bigquery
from datetime import datetime, timezone
import os

# Set up the BigQuery client
client = bigquery.Client()

# Replace with your actual GCP project and dataset details
PROJECT_ID = "your-gcp-project-id"
DATASET_ID = "your_dataset"
TABLE_ID = "document_activity"

def log_document_activity(user_id: str, document_id: str, status: str):
    """
    Logs document activity in Google BigQuery.

    :param user_id: ID of the user who uploaded the document.
    :param document_id: Unique document ID.
    :param status: Status of the document (e.g., 'uploaded', 'processed').
    """
    
    # Define the full BigQuery table reference
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    # Create a dictionary of data to insert
    row_to_insert = [
        {
            "user_id": user_id,
            "document_id": document_id,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    ]

    try:
        # Insert the row into BigQuery
        errors = client.insert_rows_json(table_ref, row_to_insert)

        if errors:
            print(f"BigQuery Insert Errors: {errors}")
        else:
            print(f"Document activity logged successfully in BigQuery: {row_to_insert}")

    except Exception as e:
        print(f"Error logging document activity to BigQuery: {e}")
