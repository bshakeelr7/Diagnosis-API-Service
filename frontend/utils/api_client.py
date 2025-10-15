import os
import requests
from typing import Tuple, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class APIClient:
    def __init__(self, base_url: str | None = None, timeout: int = 60):
        backend_url = os.getenv("BACKEND_URL")
        backend_port = os.getenv("BACKEND_PORT", "8000")

        # Default to localhost for local dev, 'backend' for Docker
        if backend_url:
            self.base_url = backend_url.rstrip("/")
        else:
            api_host = os.getenv("BACKEND_HOST", "127.0.0.1")
            self.base_url = f"http://{api_host}:{backend_port}"

        self.base_url = self.base_url.rstrip("/")
        self.timeout = timeout   

    def predict_image(self, disease: str, model_name: str, file_tuple: Tuple[str, bytes, str]) -> Dict[str, Any]:
        url = f"{self.base_url}/image/predict"
        files = {"file": file_tuple}
        data = {"disease": disease, "model_name": model_name}
        resp = requests.post(url, data=data, files=files, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def health(self) -> Dict[str, Any]:
        try:
            resp = requests.get(self.base_url, timeout=5)
            return {"ok": True, "status_code": resp.status_code, "text": resp.text}
        except Exception as e:
            return {"ok": False, "error": str(e)}

