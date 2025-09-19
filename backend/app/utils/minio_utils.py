from minio import Minio
import os

def download_models():
    client = Minio(
       "localhost:9000",
        access_key="admin",
        secret_key="admin123",
        secure=False
    )

    BUCKET_NAME = "models"
    DOWNLOAD_DIR = "backend/weights"

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    for obj in client.list_objects(BUCKET_NAME, recursive=True):
        local_path = os.path.join(DOWNLOAD_DIR, os.path.basename(obj.object_name))

        if os.path.exists(local_path):
            print(f"Already exists, skipping {local_path}")
            continue

        print(f"Downloading {obj.object_name} to {local_path}")
        client.fget_object(BUCKET_NAME, obj.object_name, local_path)

    print("Model download check complete!")
