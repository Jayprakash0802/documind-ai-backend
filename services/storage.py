from google.cloud import storage
from config import Config

storage_client = storage.Client()
bucket = storage_client.bucket(Config.STORAGE_BUCKET)

def save_text_to_file(content: str, file_path: str):
    """
    Saves a given text content as a file in Google Cloud Storage.
    """
    try:
        blob = bucket.blob(file_path)
        blob.upload_from_string(content, content_type="text/plain")
        print(f"Summary saved at {file_path}")
    except Exception as e:
        print(f"Error saving summary: {str(e)}")
        raise
