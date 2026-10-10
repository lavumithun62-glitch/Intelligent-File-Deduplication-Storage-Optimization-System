
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import router


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="File Deduplication and Storage Optimization API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all API routers
app.include_router(router)


@app.on_event("startup")
def startup():
    # Create the file storage directory if it doesn't exist
    Path(settings.storage_dir).mkdir(parents=True, exist_ok=True)


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Intelligent File Deduplication System API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
    }
