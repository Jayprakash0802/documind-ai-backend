from google.cloud import vision, storage
from config import Config
import os
import mimetypes
import json

bucket_name = Config.STORAGE_BUCKET

def process_pdf(gcs_file_path: str, client, user_id, document_id) -> str:
    """
    Processes a PDF stored in Google Cloud Storage using Google Cloud Vision API.
    """
    print(f"Processing PDF for user: {user_id}, document: {document_id}")

    feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)
    
    # Ensure proper output folder path (ending with '/')
    output_folder = f"processed_results/{user_id}/{document_id}/"
    
    # Correctly set the GCS destination folder
    output_uri_prefix = f"gs://{bucket_name}/{output_folder}"

    async_request = vision.AsyncAnnotateFileRequest(
        features=[feature],
        input_config=vision.InputConfig(
            gcs_source=vision.GcsSource(uri=f"gs://{bucket_name}/{gcs_file_path}"),
            mime_type="application/pdf"
        ),
        output_config=vision.OutputConfig(
            gcs_destination=vision.GcsDestination(uri=output_uri_prefix),
            batch_size=10  # Process 10 pages at a time
        )
    )

    operation = client.async_batch_annotate_files(requests=[async_request])
    print("Waiting for Vision API to process PDF...")
    operation.result(timeout=600)  # Increase timeout for large PDFs

    # Fetch all extracted text from multiple output JSON files
    print("Fetching extracted text from all JSON files in GCS output folder...")
    extracted_text = get_extracted_text_from_gcs(output_folder)

    return extracted_text


def process_image(image_content: bytes, client) -> str:
    """
    Processes an image file (read as bytes) and extracts text using Google Cloud Vision OCR.

    Args:
        image_content (bytes): Image file content in bytes.
        client: Google Cloud Vision API client.

    Returns:
        str: Extracted text from the image.
    """
    try:
        # Send the image content directly to Vision API
        image = vision.Image(content=image_content)
        response = client.text_detection(image=image)

        # Check for Vision API errors
        if response.error.message:
            raise Exception(f"Error in Vision API: {response.error.message}")

        # Extract detected text
        texts = response.text_annotations
        extracted_text = texts[0].description if texts else ""

        return extracted_text

    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return ""

def save_text_to_cloud(text: str, extracted_path: str, bucket):
    """
    Saves extracted text directly to a Google Cloud Storage file.

    Args:
        text (str): Extracted text to save.
        extracted_path (str): Path to save the text file in GCS.
        bucket: Google Cloud Storage bucket instance.
    """
    try:
        # Create a new blob (file) in GCS
        blob = bucket.blob(extracted_path)
        
        # Upload the extracted text as a plain text file
        blob.upload_from_string(text, content_type="text/plain")
        
        print(f"Extracted text saved successfully at: gs://{bucket.name}/{extracted_path}")

    except Exception as e:
        print(f"Error saving extracted text to Cloud Storage: {str(e)}")
        raise

def get_extracted_text_from_gcs(processed_gcs_folder: str) -> str:
    """
    Fetches and combines extracted text from multiple output JSON files in GCS.

    Args:
        processed_gcs_folder (str): Path to the processed JSON folder in GCS (e.g., "processed_results/user_id/document_id/").

    Returns:
        str: Extracted text from all output JSON files.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    # List all output JSON files in the directory
    blobs = list(bucket.list_blobs(prefix=processed_gcs_folder))

    if not blobs:
        raise FileNotFoundError(f"No processed text files found in {processed_gcs_folder}")

    extracted_text = ""

    # Iterate through all output files and merge extracted text
    for blob in sorted(blobs, key=lambda x: x.name):  # Sort to maintain page order
        print(f"Processing file: {blob.name}")  # Debugging output
        json_content = blob.download_as_text()
        response_data = json.loads(json_content)

        for page_response in response_data["responses"]:
            if "fullTextAnnotation" in page_response:
                extracted_text += page_response["fullTextAnnotation"]["text"] + "\n"

    return extracted_text.strip()


def extract_text(file_path: str, extracted_path: str, document_id: str, user_id: str) -> str:
    """
    Extracts text from an image or PDF file stored in Google Cloud Storage using Google Cloud Vision API.

    Args:
        file_path (str): Path of the file in GCS (e.g., "documents/user_id/document_id").
        extracted_path (str): Path to store the extracted text in GCS.
        document_id (str): Document ID for reference.
        user_id (str): User ID for reference.

    Returns:
        str: Extracted text from the file.
    """
    try:
        # Initialize Google Cloud clients
        vision_client = vision.ImageAnnotatorClient()
        storage_client = storage.Client()
        
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_path)

        # Check if the file exists
        if not blob.exists():
            raise FileNotFoundError(f"File {file_path} not found in bucket {bucket_name}")

        # Get MIME type from GCS metadata
        blob.reload()
        content_type = blob.content_type

        # Debugging metadata
        print(f"File metadata for {file_path}: {blob.metadata}, Content-Type: {content_type}")

        # If content_type is None, infer from file extension
        if content_type is None:
            _, ext = os.path.splitext(file_path)
            content_type = mimetypes.guess_type(file_path)[0]  # Guess MIME type
            if content_type is None:
                raise ValueError(f"Could not determine MIME type for {file_path}")

        # Read file content directly from GCS
        content = blob.download_as_bytes()
        print(f"Processing file of type: {content_type}")

        extracted_text = ""

        if content_type.startswith("image/"):
            extracted_text = process_image(content, vision_client)
        elif content_type == "application/pdf":
            extracted_text = process_pdf(file_path, vision_client, user_id, document_id)  # Pass GCS path for async processing
        else:
            raise ValueError(f"Unsupported file type: {content_type}")

        # Save extracted text directly to Cloud Storage
        save_text_to_cloud(extracted_text, extracted_path, bucket)

        return extracted_text

    except Exception as e:
        print(f"Error extracting text: {str(e)}")
        raise
