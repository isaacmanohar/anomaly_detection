from fastapi import APIRouter, Depends
from backend.services.ml_service import MLService

router = APIRouter()


def get_ml_service():
    return MLService()


@router.get("/api/dashboard")
def get_dashboard(service: MLService = Depends(get_ml_service)):
    return service.get_dashboard_data()
