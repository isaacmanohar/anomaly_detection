"""
FastAPI backend for Identity Anomaly Detection System.
Replaces Streamlit frontend with a REST API.
"""

import sys
import os

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.services.ml_service import MLService
from backend.routes import dashboard, detection, models, performance, alerts


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load data and model
    print("Loading ML models and data...")
    service = MLService()
    service.initialize()
    print("Backend ready!")
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title="Identity Anomaly Detection API",
    description="Ensemble ML-powered security monitoring with Isolation Forest + Autoencoder",
    version="1.0.0",
    lifespan=lifespan
)

# CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(dashboard.router)
app.include_router(detection.router)
app.include_router(models.router)
app.include_router(performance.router)
app.include_router(alerts.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Identity Anomaly Detection API is running"}
