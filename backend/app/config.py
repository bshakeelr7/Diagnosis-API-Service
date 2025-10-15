from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "weights"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

API_HOST = "127.0.0.1"

API_HOST = "127.0.0.1"
API_PORT = int(os.getenv("BACKEND_PORT", 8000))

MINIO_HOST = os.getenv("MINIO_HOST", "minio") 
MINIO_PORT = os.getenv("MINIO_PORT", "9000")