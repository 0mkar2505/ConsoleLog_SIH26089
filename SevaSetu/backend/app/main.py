"""
FastAPI application entrypoint for SevaSetu.
Provides initial healthcheck and foundation for REST and WebSocket APIs.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SevaSetu API",
    description="Cooperative Gig Services Platform for Household & Community Services (PS 26089)",
    version="0.1.0",
)

# Enable CORS for local development across dashboard and mobile
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Welcome to SevaSetu API",
        "docs_url": "/docs",
        "health_check": "/api/health",
        "status": "online",
    }


@app.get("/api/health")
def health_check():
    """Healthcheck endpoint to verify API service status."""
    return {
        "status": "healthy",
        "service": "sevasetu-backend",
        "version": "0.1.0",
        "message": "SevaSetu FastAPI Backend is running successfully."
    }
