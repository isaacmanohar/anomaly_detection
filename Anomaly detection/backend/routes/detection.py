from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from backend.services.ml_service import MLService

router = APIRouter()


def get_ml_service():
    return MLService()


class DetectionRequest(BaseModel):
    failed_attempts: int = 0
    resources_accessed: int = 10
    download_mb: float = 50
    privilege_level: int = 1
    hour: int = 14
    is_weekend: bool = False
    location: str = "Mumbai"
    ip_type: str = "internal"
    sensitive_data: bool = False
    strategy: str = "weighted"


@router.post("/api/detect")
def detect_event(request: DetectionRequest, service: MLService = Depends(get_ml_service)):
    return service.detect_event(request.model_dump())
