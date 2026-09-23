"""
FastAPI application entrypoint for Console Log platform.
Provides REST APIs for Customer, Worker, Dispatch Engine, Services, and Auth.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.services import router as services_router
from app.routers.auth import router as auth_router
from app.routers.requests import router as requests_router
from app.routers.worker import router as worker_router

app = FastAPI(
    title="Console Log API",
    description="Cooperative Service Allocation & Dispatch Platform API",
    version="0.2.0",
)

# Enable CORS for local development across dashboard and mobile apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(services_router)
app.include_router(auth_router)
app.include_router(requests_router)
app.include_router(worker_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to Console Log API",
        "docs_url": "/docs",
        "health_check": "/api/health",
        "status": "online",
    }


@app.get("/api/health")
def health_check():
    """Healthcheck endpoint to verify API service status."""
    return {
        "status": "healthy",
        "service": "consolelog-backend",
        "version": "0.2.0",
        "message": "Console Log FastAPI Backend is running successfully."
    }
