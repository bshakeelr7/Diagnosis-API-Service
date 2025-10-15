import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes import image
from backend.app.utils.minio_utils import download_models 
import os
from backend.app.config import API_PORT
app = FastAPI(title="Dementia Platform Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router for image-related routes
app.include_router(image.router)

@app.on_event("startup")
async def startup_event():
    """
    This event is triggered when the app starts.
    Calls the function to download models from MinIO.
    The function will handle the case if MinIO is unavailable.
    """
    download_models()

if __name__ == "__main__":
    backend_port = API_PORT
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=backend_port, reload=True)


