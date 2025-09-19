from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "weights"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

API_HOST = "127.0.0.1"
API_PORT = 8000
