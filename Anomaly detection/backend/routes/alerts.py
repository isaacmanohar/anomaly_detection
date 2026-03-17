from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from backend.services.ml_service import MLService

router = APIRouter()


def get_ml_service():
    return MLService()


@router.get("/api/alerts")
def get_alerts(
    severity: Optional[str] = Query(None, description="Comma-separated: CRITICAL,HIGH,MEDIUM,LOW"),
    attack_type: Optional[str] = Query(None, description="Comma-separated attack types"),
    department: Optional[str] = Query(None, description="Comma-separated departments"),
    service: MLService = Depends(get_ml_service)
):
    severity_filter = [s.strip() for s in severity.split(",")] if severity else None
    attack_filter = [a.strip() for a in attack_type.split(",")] if attack_type else None
    dept_filter = [d.strip() for d in department.split(",")] if department else None

    return service.get_alerts_data(severity_filter, attack_filter, dept_filter)
