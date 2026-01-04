from google.cloud import storage
import os

# Initialize client (will use default credentials or fail gracefully if not set)
try:
    storage_client = storage.Client()
except Exception:
    storage_client = None

BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "my-image-stats-bucket")

async def upload_to_gcs(file_obj, filename: str) -> str:
    if not storage_client:
        # Mock URL for local testing if no GCS creds
        return f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    # Reset file pointer just in case
    file_obj.seek(0)
    blob.upload_from_file(file_obj)
    return blob.public_url
