import os
import requests
from typing import Tuple, Dict, Any

class APIClient:
    def __init__(self, base_url: str | None = None, timeout: int = 60):
        self.base_url = (base_url or os.environ.get("API_URL") or "http://127.0.0.1:8000").rstrip("/")
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
