from minio import Minio
import os
import logging
from dotenv import load_dotenv
from backend.app.config import MINIO_HOST, MINIO_PORT

def download_models():
    minio_endpoint = f"{MINIO_HOST}:{MINIO_PORT}"
    client = Minio(
        minio_endpoint,  
        access_key="admin",
        secret_key="admin123",
        secure=False
    )

    BUCKET_NAME = "models"
    DOWNLOAD_DIR = "backend/weights"

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    try:
        for obj in client.list_objects(BUCKET_NAME, recursive=True):
            local_path = os.path.join(DOWNLOAD_DIR, os.path.basename(obj.object_name))

            if os.path.exists(local_path):
                print(f"Already exists, skipping {local_path}")
                continue

            print(f"Downloading {obj.object_name} to {local_path}")
            client.fget_object(BUCKET_NAME, obj.object_name, local_path)

        print("Model download check complete!")

    except Exception as e:
        # Log error if MinIO connection fails
        logging.error(f"Error connecting to MinIO: {e}")
        print("MinIO is unavailable, skipping model download.")


