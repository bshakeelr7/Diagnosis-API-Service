import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes import image
from backend.app.config import API_HOST, API_PORT
from backend.app.utils.minio_utils import download_models

app = FastAPI(title="Dementia Platform Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(image.router)

@app.on_event("startup")
async def startup_event():
    download_models()

if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host=API_HOST, port=API_PORT, reload=True)
